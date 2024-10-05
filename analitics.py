import pandas as pd

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
