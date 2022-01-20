import os
import pathlib
from datetime import datetime

import pandas as pd
import requests
from bs4 import BeautifulSoup

PERSCONFERENTIES_API_URL = 'https://www.rijksoverheid.nl/onderwerpen/coronavirus-covid-19/coronavirus-beeld-en-video/videos-persconferenties'
RIJKSOVERHEID_URL = 'https://www.rijksoverheid.nl'
CONFERENCE_OUTPUT_FOLDER = '../input/conferences/'


def get_date(date_row: str) -> str:
    """
    Parses the first row of the press conference, and converts it to a readable yyyy-mm-dd format.

    :param date_row: first text row of press conference
    :return: String formatted date
    """
    date_raw = date_row.split(' | ')[1]
    datetime_object = datetime.strptime(date_raw, "%d-%m-%Y")
    return datetime_object.strftime("%Y-%m-%d")


def download_conferences():
    """
    Downloads all the available press conferences and stores them into the output folder
    """
    response = requests.get(PERSCONFERENTIES_API_URL)
    soup = BeautifulSoup(response.content, "html.parser")

    urls = []
    for page_content in soup.findAll('a', href=True):
        urls.append(page_content['href'])
    urls = pd.Series(urls)
    urls = urls[urls.str.contains('letterlijk')]
    urls = RIJKSOVERHEID_URL + urls

    pathlib.Path(CONFERENCE_OUTPUT_FOLDER).mkdir(parents=True, exist_ok=True)
    for i, url in enumerate(urls):
        response_text = requests.get(url)
        soup = BeautifulSoup(response_text.content, "html.parser")
        raw_paragraphs = soup.find_all('p')
        date_row = raw_paragraphs[0].get_text()
        texts = [p.get_text() for p in raw_paragraphs[2:]]
        file_name = f"{CONFERENCE_OUTPUT_FOLDER}/{get_date(date_row)}.txt"
        with open(file_name, "w", encoding='utf-8') as txt_file:
            txt_file.write('\n'.join(texts))


def _preprocess_conference_data(conference_data: list):
    """
    Preprocesses the text of a single conference
    Todo.
    """

    # Starts with saving text for Rutte
    save_text = 'rutte'
    words = set()

    # Only keep the sentences of Rutte and De Jonge
    text_rutte, text_de_jonge = [], []
    for line in conference_data:
        if save_text == 'rutte':
            text_rutte.append(line)
        if save_text == 'de jonge':
            text_de_jonge.append(line)

        if line.isupper():
            if 'RUT' in line:
                save_text = 'rutte'
            elif 'DE JONGE' in line:
                save_text = 'de jonge'
            else:
                words.add(line)
                save_text = 'other'

    return text_rutte, text_de_jonge


def _preprocess_all_conferences():
    """
    Todo.
    """
    conference_paths = os.listdir(CONFERENCE_OUTPUT_FOLDER)
    all_text_rutte, all_text_de_jonge = [], []

    for conf_file_name in conference_paths:
        with open(f"{CONFERENCE_OUTPUT_FOLDER}/{conf_file_name}", "r", encoding='utf-8') as f:
            text_rutte, text_de_jonge = _preprocess_conference_data(f.readlines())
            conf_date = conf_file_name.replace('.txt', '')
            all_text_rutte.append({'date': conf_date, 'text': text_rutte})
            all_text_de_jonge.append({'date': conf_date, 'text': text_de_jonge})

    return all_text_rutte, all_text_de_jonge


def get_conference_data():
    """
    Todo.
    """
    if not os.listdir(CONFERENCE_OUTPUT_FOLDER):
        download_conferences()
    return _preprocess_all_conferences()
