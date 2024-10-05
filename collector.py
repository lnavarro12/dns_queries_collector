""" Collector script for dns_queries.txt """
import argparse
import os
import re
from datetime import datetime

from analitics import analitics_overview
from utils.utils import request_service
from utils.constants import (
    CHUNKS,
    SERVICE,
)



def parse_arguments():
    """ Parse command line arguments 
        Args:
            None
        Returns:
            queries (str): Path to the BIND server log file
    """

    parser = argparse.ArgumentParser(
        description='Parse BIND server log and send DNS queries to Lumu API.'
    )
    # Agregar un argumento para el archivo
    parser.add_argument('queries', help='Path to the BIND server log file')

    # Parsear los argumentos
    args = parser.parse_args()

    # Verificar si el archivo existe en la ruta proporcionada
    if not os.path.isfile(args.queries):
        raise FileNotFoundError(f"The file {args.queries} does not exist or is not a file.")

    return args.queries


def formatting_queries(query: str) -> dict:
    """ Format DNS queries
        Args:
            query (str): DNS query
        Returns:
            formatted_query (dict): DNS query formatted
    """
    # Remove spaces at the beginning and at the end of the string
    original = query.strip()

    # "timestamp": "2021-01-06T14:37:02.228Z",
    # "name": "www.example.com",
    # "client_ip": "192.168.0.103",
    # "client_name": "MACHINE-0987",
    # "type": "A"

    # timestamp
    evaluated_date = re.search(
        r'\d{1,2}-[A-Za-z]{3}-\d{4} \d{2}:\d{2}:\d{2}\.\d{3}', original
    ).group()

    if not evaluated_date:
        timestamp = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")

    # first change the format to 2021-01-06T14:37:02.228Z
    dt = datetime.strptime(evaluated_date, '%d-%b-%Y %H:%M:%S.%f')
    timestamp = dt.strftime("%Y-%m-%dT%H:%M:%SZ")

    # client_ip
    client_ip = re.search(
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', original
    ).group()

    if not client_ip:
        client_ip = '0.0.0.0'

    # type
    type_ = re.search(
        r'(?<=\bIN\s)(\S+)', original
    ).group()

    if not type_:
        type_ = 'A'

    # client_name
    client_name = re.search(
        r'(?<=query:\s)(\S+)', original
    ).group()

    if not client_name:
        client_name = 'Unknown'

    return {
        'timestamp': timestamp,
        'client_ip': client_ip,
        'type': type_,
        'name': client_name
    }


def process_queries(queries: str):
    """ Process BIND server log file and send DNS queries to Lumu API
        Args:
            queries (str): Path to the BIND server log file
        Returns:
            processed_queries (list): List of processed DNS queries
    """
    processed_queries = []
    try:
        with open(queries, 'r', encoding='utf-8') as file:
            for line in file:
                # Format each line of the file
                query = formatting_queries(line)

                if query:
                    processed_queries.append(query)

        # if the list do not have the chunk size
        # then I send the remaining queries
        if len(processed_queries) > 0:
            chunk_queries(processed_queries)

    except FileNotFoundError as e:
        print(f'Error opening file: {e}')
    except UnicodeDecodeError as e:
        print(f'Error decoding line: {e}')

    return processed_queries


def chunk_queries(queries: list):
    """ Send DNS queries to Lumu API
        Args:
            queries (str): Path to the BIND server log file
        Returns:
            
    """
    # Divide the processed queries into chunks of CHUNKS
    for i in range(0, len(queries), CHUNKS):
        chunk = queries[i:i + CHUNKS]
        send_queries(chunk)

    print(f"Processed {len(queries)} queries in {len(queries) / CHUNKS} chunks.")


def send_queries(queries: list):
    """ Send DNS queries to Lumu API
        Args:
            queries (str): Path to the BIND server log file
        Returns:
            None
    """
    url = (f"{SERVICE.get('LUMU_HOST')}/collectors/{SERVICE.get('COLLECTOR_ID')}/dns/queries"
           f"?key={SERVICE.get('LUMU_CLIENT_KEY')}")

    try:
        # send the queries to Lumu API
        response = request_service(
            data=queries,
            url=url,
            method="POST",
            headers={"Content-Type": "application/json"}
        )

        if response:
            print(
                f"Sent {len(queries)} queries to Lumu API. Response:"
                f"{response.text} - {response.status_code}"
            )

    except Exception as e:
        print(f"Error sending queries to Lumu API: {e}")

    return response




def main():
    """ Main function """
    queries = parse_arguments()
    format_querys = process_queries(queries)
    analitics_overview(format_querys)


if __name__ == '__main__':
    main()
