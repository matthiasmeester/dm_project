import pathlib

import pandas as pd
import requests
from bs4 import BeautifulSoup

PERSCONFERENTIES_API_URL = 'https://www.rijksoverheid.nl/onderwerpen/coronavirus-covid-19/coronavirus-beeld-en-video/videos-persconferenties'


def download_toespraken():
    """"""
    response = requests.get(PERSCONFERENTIES_API_URL)
    soup = BeautifulSoup(response.content, "html.parser")

    urls = []
    for page_content in soup.findAll('a', href=True):
        urls.append(page_content['href'])
    urls = pd.Series(urls)
    urls = urls[urls.str.contains('letterlijk')]
    urls = 'http://www.rijksoverheid.nl' + urls

    pathlib.Path('../input/toespraken/').mkdir(parents=True, exist_ok=True)
    for i, url in enumerate(urls):
        response_text = requests.get(url)
        soup = BeautifulSoup(response_text.content, "html.parser")
        texts = [p.get_text() for p in soup.find_all('p')]
        file_name = f"../input/toespraken/toespraak_{i}.txt"
        with open(file_name, "w", encoding='utf-8') as txt_file:
            txt_file.write('\n'.join(texts))


def preprocess():
    pass
