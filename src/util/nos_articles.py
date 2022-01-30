import pathlib
import requests
import os

import pandas as pd
from tqdm.notebook import tqdm
from bs4 import BeautifulSoup

ARTICLE_OUTPUT_FOLDER = '../input/articles'
NOS_ARCHIVE_URL = 'https://nos.nl/nieuws/archief/'
NOS_URL = 'https: //nos.nl'
startdate = '2020-04-01'
enddate = '2020-04-30' # datetime.today()

pathlib.Path(ARTICLE_OUTPUT_FOLDER).mkdir(parents=True, exist_ok=True)

# Example article url: https://nos.nl/nieuws/archief/2020-05-25


# get list of formatted dates
list_of_dates = [x.strftime('%Y-%m-%d') for x in pd.date_range(start=startdate, end=enddate, freq='D')]


def get_article_urls(dates):
    """
    Downloads all article urls that can be found in the archive for the given list of dates
    """
    article_urls_dict = {}

    for date in tqdm(dates, total=len(dates)):
        urls = []
        response = requests.get(NOS_ARCHIVE_URL+date)
        soup = BeautifulSoup(response.content, "html.parser")

        for page_content in soup.findAll('a', href=True):
            urls.append(page_content['href'])
        urls = pd.Series(urls)
        urls = urls[urls.str.contains('/artikel/')]
        urls = NOS_URL + urls
        article_urls_dict[date] = list(urls)

    return article_urls_dict


def download_article_text(article_url, date):
    """
    Downloads and stores the main text of the articles in {article_id}{article_title}.txt files
    """
    file_name = f"{ARTICLE_OUTPUT_FOLDER}/{date}/{article_url[article_url.find('/artikel/')+9:]}.txt"

    if not os.path.exists(file_name):
        response_text = requests.get(article_url)
        soup = BeautifulSoup(response_text.content, "html.parser")
        raw_paragraphs = soup.find_all("p", class_="text_3v_J6Y0G")
        texts = [p.get_text() for p in raw_paragraphs]
        try:
            with open(file_name, "w", encoding="utf-8") as txt_file:
                txt_file.write('\n'.join(texts))
        except:
            print(f'Could not save: {file_name}')


def download_articles(dates, max_articles=10000, articles_dir='../input/articles', refresh_articles=False):
    """
    Main function that collects article urls and downloads the article content
    """
    article_files = os.listdir(articles_dir)
    if not refresh_articles:
        dates = [date for date in dates if date not in article_files]

    if count_articles(articles_dir) < max_articles:
        article_urls_dict = get_article_urls(dates=dates)
        downloaded_articles = 0
        for date in tqdm(article_urls_dict, total=len(article_urls_dict)):
            pathlib.Path(ARTICLE_OUTPUT_FOLDER + '/' + date).mkdir(parents=True, exist_ok=True)
            for article_url in tqdm(article_urls_dict[date], total=len(article_urls_dict[date])):
                if downloaded_articles >= max_articles:
                    break
                download_article_text(article_url=article_url, date=date)
                downloaded_articles += 1
            else:
                continue
            break


def count_articles(articles_dir='../input/articles'):
    nr_of_articles = sum(len(files) for _, _, files in os.walk(articles_dir))
    print(f'There are {nr_of_articles} articles!')
    return nr_of_articles


def load_articles(articles_path) -> list:
    text_list = []
    for article in os.listdir(articles_path):
        full_path = f"{articles_path}/{article}"

        if os.path.exists(full_path):
            with open(full_path, "r", encoding="utf-8") as f:
                text_list.append(f.readlines())

    return text_list


def load_nos_texts(dates=[]) -> dict:
    """
    Used for loading text files content into a dictionary
    """
    base_path = "../input/articles/"
    text_dict = {}

    if not dates:
        dates = os.listdir(base_path)
        for date in tqdm(dates, total=len(dates)):
            text_dict[date] = load_articles(articles_path=f"{base_path}{date}")
    else:
        for date in tqdm(dates, total=len(dates)):
            if date in os.listdir(base_path):
                text_dict[date] = load_articles(articles_path=f"{base_path}{date}")

    return text_dict


# load_nos_texts(dates=list_of_dates)
# # print(x)