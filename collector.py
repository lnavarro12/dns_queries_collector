""" Collector script for dns_queries.txt """
import argparse
import os
import re
from datetime import datetime
from utils import request_service
from constants import (
    CHUNKS,
    SERVICE,
)
import numpy as np
import pandas as pd

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
        n = 0
        for line in file:
            n += 1
            # Procesar cada línea del archivo
            query = formatting_queries(line)

            if query:
                processed_queries.append(query)

    #chunk_queries(processed_queries)
    return processed_queries


def analitics_overview(queries: list):
    """ Analyze DNS queries
        Args:
            queries (str): Path to the BIND server log file
        Returns:
            None
    """
    # Analyze DNS queries

    # create a dataframe
    df = pd.DataFrame(queries)

    # calculate the number of clients_ip
    clients_ip = df['client_ip'].value_counts()

    # calculate the percentage of clients_ip
    total_records = df.shape[0]
    clients_ip_percentage = (clients_ip / total_records) * 100
    clients_ip_percentage = clients_ip_percentage.round(2)
    clients_ip_percentage = clients_ip_percentage.apply(lambda x: f'{x:.2f}%')

    # calculate the rank of clients_ip
    value_counts_ranked = clients_ip.rank(ascending=False, method='dense')
    ranking_df = pd.DataFrame({
        'count': clients_ip,
        'rank': value_counts_ranked,
        'percentage': clients_ip_percentage,
    })

    print(ranking_df)


    # calculate the number of clients_name
    clients_name = df['name'].value_counts()

    # calculate the percentage of clients_name
    clients_name_percentage = (clients_name / total_records) * 100
    clients_name_percentage = clients_name_percentage.round(2)
    clients_name_percentage = clients_name_percentage.apply(lambda x: f'{x:.2f}%')

    # calculate the rank of clients_name
    value_counts_ranked = clients_name.rank(ascending=False, method='dense')
    ranking_df = pd.DataFrame({
        'count': clients_name,
        'rank': value_counts_ranked,
        'percentage': clients_name_percentage,
    })

    print(ranking_df)




def chunk_queries(queries: list):
    """ Send DNS queries to Lumu API
        Args:
            queries (str): Path to the BIND server log file
        Returns:
            None
    """
    # Divide the processed queries into chunks of 500
    query_chunks = np.array_split(queries, np.ceil(len(queries) / CHUNKS))

    for chunk in query_chunks:
        send_queries(chunk.tolist())

    return query_chunks

def send_queries(queries: list):
    """ Send DNS queries to Lumu API
        Args:
            queries (str): Path to the BIND server log file
        Returns:
            None
    """

    # send the queries to Lumu API
    response = request_service(
        data=queries,
        url=SERVICE.get('LUMU_HOST') +
        f'/collectors/{SERVICE.get("COLLECTOR_ID")}' +
        f'/dns/queries?key={SERVICE.get("LUMU_CLIENT_KEY")}',
        method="POST",
        headers={"Content-Type": "application/json"}
    )
    return response


def main():
    """ Main function """
    queries = parse_arguments()
    format_querys = process_queries(queries)
    analitics_overview(format_querys)


if __name__ == '__main__':
    main()
