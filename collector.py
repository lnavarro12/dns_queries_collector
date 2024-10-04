""" Collector script for dns_queries.txt """
import argparse
import os
import re
from datetime import datetime
import numpy as np

# 1. Reading and Parsing the BIND Log
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

# 1.1 Process BIND server log file
def process_queries(queries: str):
    """ Process BIND server log file and send DNS queries to Lumu API
        Args:
            queries (str): Path to the BIND server log file
        Returns:
            None
    """
    with open(queries, 'r', encoding='utf-8') as file:
        processed_queries = []
        for line in file:
            # Procesar cada línea del archivo
            query = formatting_queries(line)

            if query:
                processed_queries.append(query)

    # Divide the processed queries into chunks of 500
    query_chunks = np.array_split(processed_queries, np.ceil(len(processed_queries) / 500))

    for chunk in query_chunks:
        print(chunk.tolist(), flush=True)

    return query_chunks




def main():
    """ Main function """
    queries = parse_arguments()
    process_queries(queries)


if __name__ == '__main__':
    main()
