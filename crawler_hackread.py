# -*- coding: UTF-8 -*-

import requests
from bs4 import BeautifulSoup
import pymysql
import base64
import re
from datetime import datetime

HTML_PARSER = "html.parser"

ROOT_URL = 'https://www.hackread.com//hacking-news/'
news_link = []

page_number = 2

passwd = 'bmJjeC01OTE='


def get_next_page_link(url):
    global next_page_link
    global page_number
    next_page_link = ROOT_URL + '/page/' + str(page_number) + '/'
    print(next_page_link)
    page_number += 1

    get_news_link(url)


def get_news_link(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
    list_req = requests.get(url, headers=headers)
    if list_req.status_code == requests.codes.ok:
        soup = BeautifulSoup(list_req.content, HTML_PARSER)
        news_link_source = soup.find_all('h3', itemprop="name")

        for link in news_link_source:
            x = link.find('a')['href']
            news_link.append(x)
            print(x)


def get_news_article():
    for link in news_link:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
        list_req = requests.get(link, headers=headers)
        if list_req.status_code == requests.codes.ok:
            soup = BeautifulSoup(list_req.content, HTML_PARSER)

        # article URL
        url = link

        # article title
        title1 = soup.find('h1')
        if not title1:
            continue
        title = title1.text.replace('\n', '')
        title = title.replace("	", '')
        title = re.sub(r'[^\x00-\x7f]', r' ', title)
        # title = title.replace('\n', '')
        print(title)

        # article content
        content = ''
        raw = soup.find('div', "article-post-content clearfix")
        if not raw:
            continue
        source = raw.find_all('p')
        for x in source:
            if "Image credit:" in x.text:
                continue
            if "Image Credit:" in x.text:
                continue
            if "calculate the cost and probability of a DDoS attack on your business with this" in x.text:
                continue
            if "adsbygoogle" in x.text:
                continue
            if "Did you enjoy reading this article" in x.text:
                continue
            else:
                content += x.text + '\n'
        content = re.sub(r'[^\x00-\x7f]', r' ', content)
        content = (content[:18000]) if len(content) > 18000 else content
        print(content)

        # article post_date
        date = soup.findAll('time')

        x = str(date)
        match = re.search('\d{4}-\d{2}-\d{2}', x)
        date = match.group()
        print(date)

        # insert into sql server
        insert = \
            "INSERT INTO hackread (post_date, title, content, url, new_event_news) VALUES (%s, %s, %s, %s, %s)"
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
    for i in range(0, 3):
        if i == 0:
            get_next_page_link(ROOT_URL)
        else:
            get_next_page_link(next_page_link)

    get_news_article()
