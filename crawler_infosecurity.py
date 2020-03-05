# -*- coding: UTF-8 -*-
import requests
from bs4 import BeautifulSoup
import pymysql
import base64
import re

HTML_PARSER = "html.parser"

news_link = []
page_number = 2
ROOT_URL = 'https://www.infosecurity-magazine.com/news/'

passwd = 'bmJjeC01OTE='


def get_next_page_link(URL):
    global next_page_link
    global page_number
    next_page_link = ROOT_URL + 'page-' + str(page_number) + '/'
    page_number += 1
    print(next_page_link)

    get_news_link(URL)


def get_news_link(URL):
    list_req = requests.get(URL)
    if list_req.status_code == requests.codes.ok:
        soup = BeautifulSoup(list_req.content, HTML_PARSER)
        news_link_source = soup.find_all('div', "webpage-item with-thumbnail")

        for link in news_link_source:
            x = link.find('a')['href']
            news_link.append(x)


def get_news_article():
    for link in news_link:
        list_req = requests.get(link)
        if list_req.status_code == requests.codes.ok:
            soup = BeautifulSoup(list_req.content, HTML_PARSER)

        # article url
        url = link

        # article post_date
        for source in soup.findAll('div', 'article-meta'):
            x = str(source)
            match = re.search('\d{4}-\d{2}-\d{2}', x)
            date = match.group()
            print(date)

        # article title
        for source in soup.find_all('h1'):
            x = source.text
            title = re.sub(r'[^\x00-\x7f]', r' ', x)
            print(title)

        # article content
        for source in soup.find_all('div', "content-module "):
            x = source.text
            if 'Infosecurity Magazine' in x:
                x = ''
            # x = x.replace('\n', '')
            content = re.sub(r'[^\x00-\x7f]', r' ', x)
            print(content)

        # # insert into sql server
        # insert = "INSERT INTO infosecurity (url,title, content, post_date) VALUES (%s, %s, %s, %s)"
        # data = (url, title, content, date)
        # p = base64.b64decode(passwd).decode('utf-8')
        # conn = pymysql.connect(host='localhost', user='root', passwd=p, db='thehackernews')
        # sql = conn.cursor()
        # if not content:
        #     continue
        # else:
        #     sql.execute(insert, data)
        #     conn.commit()
        #
        # sql.close()
        # conn.close()


if __name__ == '__main__':
    for i in range(0, 2):
        if i == 0:
            get_next_page_link(ROOT_URL)
        else:
            get_next_page_link(next_page_link)

    get_news_article()
