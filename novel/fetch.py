# coding: utf-8
import logging
from urllib import request, parse as parseurl
import asyncio
import sys
import os
import time
import async_timeout
import aiohttp

if __name__ == '__main__':
    from django.core.wsgi import get_wsgi_application

    sys.path.extend(
        ['/Users/zhangdesheng/Documents/python-learning/zds-git/newnovel/', ])
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "newnovel.settings")
    application = get_wsgi_application()

from django.conf import settings
import requests
from bs4 import BeautifulSoup

from novel.models import Config, Book, BookTag, BookChapter

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.11; rv:46.0) Gecko/20100101 Firefox/46.0'}


def search_by_config(bookname):
    bookname = bookname.strip()
    for source in Config.objects.all().order_by('priority')[:2]:
        __searchdata = {}
        __searchdata[source.search_keyword] = bookname  # 构建搜索关键词
        # print(source.search_link)
        url = source.search_link + \
            parseurl.urlencode(__searchdata, encoding='utf8')  # 关键词URL编码
        # print(url)
        logging.info(url)
        try:
            data = requests.get(url, headers=headers).content  # 读取搜索页面内容
        except:
            logging.error('无法连接到: {0}'.format(source.site_url))
            source.priority -= 1
            source.save()
            continue
        soup = BeautifulSoup(data, "html.parser")  # 构建BS数据
        title_string = 'soup.' + source.novel_name
        url_string = 'soup.' + source.novel_link
        try:
            title = eval(title_string)  # 获取小说标题
            title = title.strip()
            if not title == bookname:
                continue
            bookurl = eval(url_string)  # 获取小说页面链接
            if not bookurl.startswith('http'):
                bookurl = source.site_url + bookurl  # 构建小说页面链接
        except Exception as e:
            logging.error('解析查询页面失败: {0}').format(url)
            logging.error('解析查询页面失败: {0}').format(e)
            continue
        noveldata = get_novel_info(bookurl, source)
        if noveldata == -1:
            source.priority -= 1
            source.save()
            continue
        if not noveldata.get('title', None):
            source.priority -= 1
            source.save()
            continue

        book = save_noveldata(noveldata)
        if not book:
            break
        book.source_site2 = source
        try:
            book.save()
        except Exception as e:
            logging.error('保存失败: {0},原因: {1}'.format(bookname, e))
            continue


def get_novel_info(bookurl, source):
    '''获取小说信息
    bookurl：小说信息（目录）页
    source：源站点配置'''

    noveldata = {}
    try:
        data = requests.get(bookurl, headers=headers).content  # 读取小说页面内容
    except:
        return -1  # 小说页面无法连接
    soup = BeautifulSoup(data, "html.parser")  # 构建BS数据
    # --------------------------------------------------抓取小说信息
    noveldata['homepage'] = source.site_url
    noveldata['infolink'] = bookurl
    noveldata['id'] = source.site_short_name
    noveldata['website'] = source.site_desc

    string = 'soup.' + source.title
    noveldata['title'] = eval(string)
    try:
        string = 'soup.' + source.description
        noveldata['description'] = eval(string)
    except:
        pass

    try:
        string = 'soup.' + source.category
        noveldata['category'] = eval(string)
    except:
        pass

    try:
        string = 'soup.' + source.author
        noveldata['author'] = eval(string)
    except:
        pass

    try:
        string = 'soup.' + source.status
        noveldata['status'] = eval(string)
    except:
        pass

    try:
        string = 'soup.' + source.update
        noveldata['update'] = eval(string)
    except:
        pass

    try:
        string = 'soup.' + source.latest
        noveldata['latest'] = eval(string)
    except:
        pass

    try:
        string = 'soup.' + source.image
        string = eval(string)
        if not string.startswith('http'):
            string = noveldata['homepage'] + string
        noveldata['image'] = string
    except:
        pass

    return noveldata


def save_noveldata(noveldata):
    bookname = noveldata['title'].strip()
    if Book.objects.filter(name=bookname).exists():
        return False
    book_author = noveldata.get('author', '')
    book_img = noveldata.get('image', '')
    book_website = noveldata.get('id', '')
    if 'content_link' in noveldata.keys():
        book_url = noveldata['content_link']
    else:
        book_url = noveldata['infolink']
    book_desc = noveldata.get('description', '暂无简介')
    book_tag = None
    if 'category' in noveldata.keys():
        try:
            book_tag = BookTag.objects.get(tag_name=noveldata['category'])
        except BookTag.DoesNotExist:
            book_tag = BookTag(tag_name=noveldata['category'])
            book_tag.save()
        except:
            pass
    book = Book(name=bookname, author=book_author, desc=book_desc, img=book_img, source_site=book_website,
                index_url=book_url, tag=book_tag, hot=1, read_on_site=True)
    return book


async def dbook(book_id):
    loop = asyncio.get_event_loop()
    reqs = []
    ress = []
    text = ''
    book = Book.objects.all().get(id=book_id)
    config = Config.objects.all().get(site_short_name=book.source_site)
    for chapter in BookChapter.objects.filter(book_id=book_id).order_by('-index'):
        reqs.append(loop.run_in_executor(None, requests.get, chapter.url))

    for req in reqs:
        ress.append(await req)

    for res in ress:
        try:
            data = res.content.decode('gbk', 'ignore').replace('<br />', '\n')
            soup = BeautifulSoup(data, "html.parser")
            content = eval('soup.' + opts['text'])
        except:
            content = '未找到章节内容,刷新重试'
        text +=  """chapter.title + '\n' + content + '\n\n'"""
    return text


async def get_content(session, chapter):
    url = chapter.url
    index = chapter.index
    with async_timeout.timeout(10):
        async with session.get(url) as resp:
            if resp.status != 200:
                return (index, '\n' + 'sorry 获取正文失败 |' + '\n', url)
            try:
                content = await resp.read()
                content = parse(content)
                content = ''.join([chapter.title, '\n', content])
            except Exception as e:
                print(url)
                print(e)
                content = ''.join([chapter.title, '\n', ' sorry 获取正文失败 '])
            return (index, content, url)


async def fetch(book_id, begin=0, end=100):
    tasks = []
    async with aiohttp.ClientSession() as session:
        for chapter in BookChapter.objects.all().filter(book_id=book_id).order_by('index')[begin:end]:
            task = asyncio.ensure_future(get_content(session, chapter))
            tasks.append(task)
        datas = await asyncio.gather(*tasks)
        return datas


def parse(content):
    # if type(content[1]) == bytes:
    c = content.decode('gbk', 'ignore').replace('<br />', '\n')
    soup = BeautifulSoup(c, "html.parser")
    try:
        text = soup.find("div", id="content").get_text()
    except:
        text = '\n' + 'sorry 获取正文失败 |' + '\n' + content[2]
    return text


def downbook(book_id):
    _num = 50
    begin, end = 0, _num
    contents = []
    while begin + 1 < BookChapter.objects.all().filter(book_id=book_id).count():
        loop = asyncio.get_event_loop()
        contents = loop.run_until_complete(
            fetch(book_id=book_id, begin=begin, end=end))
        # contents.extend(datas)
        begin += _num
        end += _num
        for content in contents:
            yield content[1]


if __name__ == '__main__':

    start = time.time()
    i = 1
    with open('贴身高手.txt', 'w') as f:
        for text in downbook(23):
            f.write(text)
            f.write('\n')

    end = time.time()
    print('time1:', (end - start))
    time.sleep(5)
