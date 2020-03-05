# -*- coding: UTF-8 -*-

import requests
from bs4 import BeautifulSoup
import pymysql
import base64
import re
from datetime import datetime

HTML_PARSER = "html.parser"

ROOT_URL = 'https://securityaffairs.co/wordpress/'
news_link = []

page_number = 2

passwd = 'bmJjeC01OTE='


def get_next_page_link(url):
    global next_page_link
    global page_number
    next_page_link = ROOT_URL + 'page/' + str(page_number) + '/'
    page_number += 1
    print(next_page_link)

    get_news_link(url)


def get_news_link(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
    list_req = requests.get(url, headers=headers)
    if list_req.status_code == requests.codes.ok:
        soup = BeautifulSoup(list_req.content, HTML_PARSER)
        news_link_source = soup.find_all('div', 'post_header single_post')

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
        title = title1.text.replace('\n', '')
        title = title1.text.replace('	', '')

        title = re.sub(r'[^\x00-\x7f]', r' ', title)
        # title = title.replace('\n', '')
        print(title)

        # article content
        content = ''
        raw = soup.find('div', "post_inner_wrapper")
        source = raw.find_all('p')
        for x in source:
            x = x.text.replace("Security Affairs", '')
            x = x.replace("Pierluigi", '')
            x = x.replace("Paganini", '')

            content += x + '\n'
        content = re.sub(r'[^\x00-\x7f]', r' ', content)
        content = (content[:18000]) if len(content) > 18000 else content

        # article post_date
        date = soup.find("div", "post_detail")
        x = date.text
        match = re.search('[a-zA-Z]+ \d{1,2}, \d{4}', x)
        date = match.group()
        d = datetime.strptime(date, '%B %d, %Y')
        date = d.strftime('%Y-%m-%d')
        print(date)

        # insert into sql server
        insert = \
            "INSERT INTO securityaffairs (post_date, title, content, url, new_event_news) VALUES (%s, %s, %s, %s, %s)"
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

        # empty content
        content = ''


if __name__ == '__main__':
    for i in range(0, 10):
        if i == 0:
            get_next_page_link(ROOT_URL)
        else:
            get_next_page_link(next_page_link)

    get_news_article()
