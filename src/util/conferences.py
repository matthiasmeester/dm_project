import os
import pathlib
import re
from datetime import datetime

import pandas as pd
import requests
from bs4 import BeautifulSoup

PERSCONFERENTIES_API_URL = 'https://www.rijksoverheid.nl/onderwerpen/coronavirus-covid-19/coronavirus-beeld-en-video/videos-persconferenties'
RIJKSOVERHEID_URL = 'https://www.rijksoverheid.nl'
CONFERENCE_OUTPUT_FOLDER = 'input/conferences/'
FORBIDDEN_LINES = ['Let op. De datum van deze tekst']


def correct_cwd():
    cwd = os.getcwd()
    if not cwd.endswith('src'):
        os.chdir('..')


def get_date(date_row: str) -> str:
    """
    Parses the first row of the press conference, and converts it to a readable yyyy-mm-dd format.

    :param date_row: first text row of press conference
    :return: String formatted date
    """
    date_raw = date_row.split(' | ')[1]
    datetime_object = datetime.strptime(date_raw, "%d-%m-%Y")
    return datetime_object.strftime("%Y-%m-%d")


def download_single_conference(url):
    response_text = requests.get(url)
    soup = BeautifulSoup(response_text.content, "html.parser")
    raw_paragraphs = soup.find_all('p')
    date_row = raw_paragraphs[0].get_text()
    texts = [p.get_text() for p in raw_paragraphs[2:]]
    file_name = f"{CONFERENCE_OUTPUT_FOLDER}/{get_date(date_row)}.txt"
    with open(file_name, "w", encoding='utf-8') as txt_file:
        txt_file.write('\n'.join(texts))


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

    for url in urls:
        download_single_conference(url)

    with open('input/extra_conferences.txt') as f:
        extra_urls = f.read().splitlines()

    for url in extra_urls:
        download_single_conference(url)


def _preprocess_conference_data(conference_data: list, include_journalist_questions) -> tuple:
    """
    Preprocesses the text of a single conference

    :return: a tuple containing Rutte texts and De Jonge texts respectively per press conference
    """

    # Starts with saving text for Rutte
    save_text = 'rutte'

    # Only keep the sentences of Rutte and De Jonge
    text_rutte, text_de_jonge = [], []
    text_other = []

    # Is rutte conference
    rutte_conference = any(['rutte' in line.lower() for line in conference_data])
    if not rutte_conference:
        return text_rutte, text_de_jonge

    for line in conference_data:
        if any([forbidden in line for forbidden in FORBIDDEN_LINES]):
            continue
        if line.isupper():
            if 'RUT' in line:
                save_text = 'rutte'
            elif 'DE JONGE' in line:
                save_text = 'de jonge'
            else:
                save_text = 'other'
        else:
            if save_text == 'rutte':
                text_rutte.append(line)
            if save_text == 'de jonge':
                text_de_jonge.append(line)
            if save_text == 'other':
                if not include_journalist_questions:
                    break
                text_other.append(line)

    speakers_text = [text_rutte, text_de_jonge]

    # get rid of newline characters
    for i, data in enumerate(speakers_text):
        speakers_text[i] = ''.join(data).replace("\n", " ").replace("\r", " ")

    return tuple(speakers_text)


def get_sentences(conference_text: list):
    str_text = ''.join(conference_text).replace("\n", " ")
    sentences = re.split(r'(?<![A-Z][a-z]\.)(?<=\.|\?)\s(?<!\w\.\w.\s)', str_text)
    for sentence in sentences.copy():
        if not sentence or sentence.isspace() or len(sentence) <= 2:
            sentences.remove(sentence)
    return sentences


def _get_number_of_sentences(text_by_speaker: tuple) -> tuple:
    """

    Adds the number of sentences by speaker per conference

    :return: a tuple containing Rutte texts and De Jonge texts respectively

    """
    for i, conferences_list in enumerate(text_by_speaker):
        for j, conference in enumerate(conferences_list):
            text_by_speaker[i][j]['number_of_sentences'] = len(get_sentences(conference['text']))

    return text_by_speaker[0], text_by_speaker[1]


def _preprocess_all_conferences(include_journalist_questions) -> tuple:
    """

    Returns the preprocessed conference data

    :return: a tuple containing Rutte texts and De Jonge texts respectively

    """
    conference_paths = os.listdir(CONFERENCE_OUTPUT_FOLDER)
    all_text_rutte, all_text_de_jonge = [], []

    for conf_file_name in conference_paths:
        with open(f"{CONFERENCE_OUTPUT_FOLDER}/{conf_file_name}", "r", encoding='utf-8') as f:
            text_rutte, text_de_jonge = _preprocess_conference_data(f.readlines(), include_journalist_questions)
            conf_date = conf_file_name.replace('.txt', '')
            if text_rutte:
                all_text_rutte.append({'date': conf_date, 'text': text_rutte})
                all_text_de_jonge.append({'date': conf_date, 'text': text_de_jonge})
            else:
                print(f"Print {conf_file_name} is not a rutte press conference")

    return all_text_rutte, all_text_de_jonge


def get_conference_data(include_journalist_questions=False) -> tuple:
    """
    Returns the preprocessed conference data

    :return: a tuple containing Rutte texts and De Jonge texts respectively
    """
    if not os.listdir(CONFERENCE_OUTPUT_FOLDER):
        download_conferences()

    return _preprocess_all_conferences(include_journalist_questions)
