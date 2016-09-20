# coding: utf8

import requests

from bs4 import BeautifulSoup

content = requests.get('http://www.gugehk.com/book.asp?id=27689').content
content = content.decode('gb2312', 'ignore')
soup = BeautifulSoup(content, "html.parser")

for div in soup.find_all('div', class_='zuopinji'):
    href = div.a["href"]
    c = requests.get(href).content
    c = c.decode('gb2312', 'ignore')
    s = BeautifulSoup(c, "html.parser")
    title = s.find('strong').text
    content = s.find('td', class_='content').text
    print(title)
    print('\n')
    print(content)
    print('\n')
