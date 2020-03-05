# -*- coding: UTF-8 -*-
import requests
from bs4 import BeautifulSoup
import pymysql
import base64
import re
from datetime import datetime

HTML_PARSER = "html.parser"
news_link = []
ROOT_URL = 'https://thehackernews.com/'
passwd = 'bmJjeC01OTE='


def get_next_page_link(URL):
    global next_page_link
    list_req = requests.get(URL)
    if list_req.status_code == requests.codes.ok:
        soup = BeautifulSoup(list_req.content, HTML_PARSER)
        # next_page = soup.find('span', id="blog-pager-older-link")
        next_page = soup.find('a', "blog-pager-older-link-mobile")
        if not next_page:
            if "https://thehackernews.com/search?updated-max=2018-04-26T01:32:00-11:00&max-results=12&start=156&by-date=false" in URL:
                link = 'https://thehackernews.com/search?updated-max=2018-04-19T00:47:00-11:00&max-results=12&start=168&by-date=false'
                print("true")
            if "https://thehackernews.com/search?updated-max=2017-05-03T05:39:00-11:00&max-results=12&start=779&by-date=false" in URL:
                link = "https://thehackernews.com/search?updated-max=2017-04-24T23:38:00-11:00&max-results=12&start=791&by-date=false"
                print("true")
            if "https://thehackernews.com/search?updated-max=2016-11-10T21:54:00-11:00&max-results=12&start=1066&by-date=false" in URL:
                link = "https://thehackernews.com/search?updated-max=2016-11-06T22:25:00-11:00&max-results=12&start=1078&by-date=false"
                print("true")
        else:
            link = next_page['href']
        next_page_link = link
        print(link)
        get_news_link(URL)


def get_news_link(URL):
    list_req = requests.get(URL)
    if list_req.status_code == requests.codes.ok:
        soup = BeautifulSoup(list_req.content, HTML_PARSER)
        news_link_source = soup.find_all('div', "body-post clear")

        for link in news_link_source:
            x = link.find('a')['href']
            # print(x)
            news_link.append(x)


def get_news_article():
    for link in news_link:
        list_req = requests.get(link)
        if list_req.status_code == requests.codes.ok:
            soup = BeautifulSoup(list_req.content, HTML_PARSER)

        # article URL
        url = link

        # article title
        for source in soup.find_all('h1', "story-title"):
            x = source.text.replace('\n', '')
            title = re.sub(r'[^\x00-\x7f]', r' ', x)
            title = title.replace('\n', '')
            print(title)

        # article content
        for source in soup.find_all('div', "articlebody clear cf"):
            related = source.find('div', 'cf note-b')
            if related:
                related.extract()
            x = source.text
            x = x.replace(' (adsbygoogle = window.adsbygoogle || []).push({}); ', '')
            x = x.replace('(adsbygoogle = window.adsbygoogle || []).push({});', '')
            if 'The Information Technology industry has witnessed exponential growth over the years' in x:
                x = ''
            if 'Hat Hacker 2018 Bundle ' in x:
                x = ''
            # content = x.replace('\n', '')
            content = x
            content = re.sub(r'[^\x00-\x7f]', r' ', content)
            content = (content[:18000]) if len(content) > 18000 else content
            print(content)

        # article date
        date = soup.find('div', 'postmeta')
        x = str(date)
        match = re.search('[a-zA-Z]+ \d{1,2}, \d{4}', x)
        date = match.group()
        d = datetime.strptime(date, '%B %d, %Y')
        date = d.strftime('%Y-%m-%d')
        print(date)

        # insert into sql server
        insert = \
            "INSERT INTO thehackernews (post_date, title, content, url, new_event_news) VALUES (%s, %s, %s, %s, %s)"
        data = (date, title, content, url, 0)
        p = base64.b64decode(passwd).decode('utf-8')
        conn = pymysql.connect(host='localhost', user='root', passwd=p, db='thehackernews')
        sql = conn.cursor()
        if not content:
            continue
        else:
            sql.execute(insert, data)
            conn.commit()

        sql.close()
        conn.close()


if __name__ == '__main__':
    for i in range(0, 4):
        if i == 0:
            get_next_page_link(ROOT_URL)
        else:
            get_next_page_link(next_page_link)

    get_news_article()
