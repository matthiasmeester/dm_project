import os

import pandas as pd

INFECTIONS_OUTPUT_FILE = 'input/infections/raw_infection_data.csv'
BESMETTINGEN_CSV_URL = 'https://data.rivm.nl/covid-19/COVID-19_aantallen_gemeente_cumulatief.csv'


def download_infections() -> pd.DataFrame:
    """
    Downloads the infections of the RIVM url

    :return: dataframe with the raw infection data
    """
    content = pd.read_csv(BESMETTINGEN_CSV_URL, error_bad_lines=False, sep=';')
    content.to_csv(INFECTIONS_OUTPUT_FILE, sep=';')
    return content


def _preprocess_infection_data(raw_infection_df: pd.DataFrame) -> pd.DataFrame:
    """
    Preprocesses the raw infection data by RIVM

    :param raw_infection_df: raw infection data
    :return: preprocessed infection data (total_infections per date)
    """
    processed_df = raw_infection_df
    processed_df = processed_df.groupby('Date_of_report').sum().reset_index()  # Group infections by date
    processed_df = processed_df[['Date_of_report', 'Total_reported']]  # Select the desired columns
    processed_df.columns = ['date', 'total_infections']  # Rename columns

    # Add a column for new infections
    processed_df['new_infections'] = processed_df['total_infections'].diff(periods=1)
    processed_df.new_infections.fillna(processed_df['total_infections'], inplace=True)
    processed_df['new_infections'] = processed_df['new_infections'].astype(int)

    # Convert date to formatted string
    processed_df['date'] = processed_df['date'].apply(pd.to_datetime).dt.strftime('%Y-%m-%d')

    return processed_df


def get_infection_data() -> pd.DataFrame:
    """
    Returns the preprocessed infection data

    :return: dataframe containing the preprocessed infection data
    """
    if os.path.isfile(INFECTIONS_OUTPUT_FILE):
        raw_infection_data = pd.read_csv(INFECTIONS_OUTPUT_FILE, sep=';')
    else:
        raw_infection_data = download_infections()
    return _preprocess_infection_data(raw_infection_data)
