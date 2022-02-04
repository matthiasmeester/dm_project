import os

import pandas as pd

INFECTIONS_OUTPUT_FILE = 'input/infections/raw_infection_data.csv'
INFECTIONS_CSV_URL = 'https://data.rivm.nl/covid-19/COVID-19_aantallen_gemeente_cumulatief.csv'

IC_HOSPITALIZATIONS_URL = 'https://data.rivm.nl/covid-19/COVID-19_ic_opnames.csv'
IC_OUTPUT_FILE = 'input/infections/raw_ic_data.csv'


def download_infections() -> tuple:
    """
    Downloads the infections of the RIVM url

    :return: dataframe with the raw infection data
    """
    raw_infection_data = pd.read_csv(INFECTIONS_CSV_URL, error_bad_lines=False, sep=';')
    raw_infection_data.to_csv(INFECTIONS_OUTPUT_FILE, sep=';')

    raw_ic_data = pd.read_csv(IC_HOSPITALIZATIONS_URL, error_bad_lines=False, sep=';')
    raw_ic_data.to_csv(IC_OUTPUT_FILE, sep=';')

    return raw_infection_data, raw_ic_data


def _preprocess_infection_data(raw_infection_df: pd.DataFrame, raw_ic_data: pd.DataFrame) -> pd.DataFrame:
    """
    Preprocesses the raw infection data by RIVM

    :param raw_infection_df: raw infection data
    :return: preprocessed infection data (total_infections per date)
    """
    processed_df = raw_infection_df
    processed_df = processed_df.groupby('Date_of_report').sum().reset_index()  # Group infections by date

    # Convert date to formatted string
    processed_df['Date_of_report'] = processed_df['Date_of_report'].apply(pd.to_datetime).dt.strftime('%Y-%m-%d')
    raw_ic_data['Date_of_report'] = raw_ic_data['Date_of_report'].apply(pd.to_datetime).dt.strftime('%Y-%m-%d')

    raw_ic_data = raw_ic_data[['Date_of_statistics', 'IC_admission']]
    raw_ic_data.columns = ['Date_of_report', 'new_ic_admissions']
    processed_df = pd.merge(processed_df, raw_ic_data, how='left', on='Date_of_report')
    processed_df = processed_df[['Date_of_report', 'Total_reported', 'new_ic_admissions']]  # Select the desired columns
    processed_df.columns = ['date', 'total_infections', 'new_ic_admissions']  # Rename columns

    # Add a column for new infections
    processed_df['new_infections'] = processed_df['total_infections'].diff(periods=1)
    processed_df = processed_df.fillna(method="ffill")

    processed_df.fillna(method='ffill', inplace=True)
    processed_df.fillna(method='bfill', inplace=True)

    processed_df['new_infections'] = processed_df['new_infections'].astype(int)
    processed_df['new_ic_admissions'] = processed_df['new_ic_admissions'].astype(int)

    return processed_df


def get_infection_data() -> pd.DataFrame:
    """
    Returns the preprocessed infection data

    :return: dataframe containing the preprocessed infection data
    """
    if os.path.isfile(INFECTIONS_OUTPUT_FILE) and os.path.isfile(IC_HOSPITALIZATIONS_URL):
        raw_infection_data = pd.read_csv(INFECTIONS_OUTPUT_FILE, sep=';')
        raw_ic_data = pd.read_csv(IC_OUTPUT_FILE, sep=';')
    else:
        raw_infection_data, raw_ic_data = download_infections()
    return _preprocess_infection_data(raw_infection_data, raw_ic_data)
