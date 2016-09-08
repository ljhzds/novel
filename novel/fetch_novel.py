# encoding:UTF-8
# from threading import Thread
import logging
from configparser import ConfigParser
import os
from os import (path, makedirs, listdir)
from django.conf import settings
from urllib import (request, parse)
import requests
from bs4 import BeautifulSoup

try:
    from .models import Book, BookTag
except ImportError:
    from models import Book, BookTag
except:
    raise ImportError

CONFIG = ConfigParser()
BASE_DIR = settings.BASE_DIR
this_dir = os.path.join(BASE_DIR, 'novel')

CONFIG.read(os.path.join(this_dir, "config.ini"), encoding='utf8')

header = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.11; rv:46.0) Gecko/20100101 Firefox/46.0'}


def get_id():
    '''获取搜索网站设置的ID列表'''
    ID = list()

    for item in CONFIG.sections():
        ID.append(item)
    return ID


def search_by_id(novelname, id='bqg5200'):
    '''获取小说信息（目录）页
    novelname：小说名
    id：网站设置ID
    '''

    opts = CONFIG[id]
    __searchdata = {}
    __searchdata[opts['keyword']] = novelname  # 构建搜索关键词
    url = opts["slink"] + parse.urlencode(__searchdata, encoding='GBK')  # 关键词URL编码
    try:
        data = requests.get(url, headers=header).content  # 读取搜索页面内容
    except:
        return -1  # 网站无法连接
    soup = BeautifulSoup(data, "html.parser")  # 构建BS数据
    string = 'soup.' + opts["novel_link"]
    try:
        url = eval(string)  # 获取小说页面链接
    except:
        return -2
    if not url.startswith('http'):
        url = opts["url"] + url  # 构建小说页面链接
    # try:
    #     data = request.urlopen(url).read()                             #读取小说信息页面内容
    # except:
    #     return -1                                                      #小说信息页面无法连接
    return url

# url = search_by_id('雪鹰领主', 'bqg5200')
# print(url)


def get_novel_info(url, id='bqg5200'):
    '''获取小说信息
    url：小说信息（目录）页
    id：网站ID'''
    opts = CONFIG[id]
    noveldata = {}
    try:
        data = requests.get(url, headers=header).content  # 读取小说页面内容
    except:
        return -1  # 小说页面无法连接
    soup = BeautifulSoup(data, "html.parser")  # 构建BS数据
    # --------------------------------------------------抓取小说信息

    noveldata['homepage'] = opts['url']
    noveldata['infolink'] = url
    noveldata['id'] = opts['id']
    noveldata['website'] = opts['name']
    # print(noveldata)
    string = 'soup.' + opts['title']
    print(string)
    noveldata['title'] = eval(string)

    try:
        string = 'soup.' + opts['content_link']
        string = eval(string)
        if not string.startswith('http'):
            string = noveldata['homepage'] + string
        noveldata['content_link'] = eval(string)
    except:
        pass

    try:
        string = 'soup.' + opts['description']
        noveldata['description'] = eval(string)
    except:
        pass

    try:
        string = 'soup.' + opts['category']
        noveldata['category'] = eval(string)
    except:
        pass

    try:
        string = 'soup.' + opts['author']
        noveldata['author'] = eval(string)
    except:
        pass

    try:
        string = 'soup.' + opts['status']
        noveldata['status'] = eval(string)
    except:
        pass

    try:
        string = 'soup.' + opts['update']
        noveldata['update'] = eval(string)
    except:
        pass

    try:
        string = 'soup.' + opts['latest']
        noveldata['latest'] = eval(string)
    except:
        pass

    try:
        string = 'soup.' + opts['image']

    except:
        pass
    string = eval(string)
    if not string.startswith('http'):
        string = noveldata['homepage'] + string
    noveldata['image'] = string

    return noveldata


def save_content(noveldata):
    """从预定网站下载章节列表
    noveldata:小说信息字典
    """
    chapter_name = []
    chapter_link = []

    opts = CONFIG[noveldata['id']]

    if 'content_link' in noveldata:
        url = noveldata['content_link']
    else:
        url = noveldata['infolink']
    try:
        data = requests.get(url, headers=header).content  # 读取目录页面内容
    except:
        return -1  # 目录页面无法连接
    soup = BeautifulSoup(data, "html.parser")  # 构建BS数据
    # --------------------------------------------------抓取小说章节列表
    # bqg5200 需要从小说主页获取小说目录页
    try:
        url = soup.find(name='a', attrs={'class': 'tgcj'})['href']
        data = requests.get(url, headers=header).content
        soup = BeautifulSoup(data, "html.parser")
    except:
        pass

    string = 'soup.' + opts['chapter_list']
    chapters = []
    for chapter_list in eval(string):
        string = eval(opts['chapter_name'])
        string = str(string)
        # chapter_name.append(string)
        url = eval(opts['chapter_link'])
        if not url.startswith('http'):
            url = opts['url'] + eval(opts['chapter_link'])
        # chapter_link.append(url)
        chapters.append((string, url))
    # chapters = dict(zip(chapter_link, chapter_name))
    # for key, value in chapters.items():
    #     print(key, value)
    # if end == -1:
    #     end = len(self.chapter_link)
    # for i in range(start,end):
    #     data=request.urlopen(self.chapter_link[i]).read()            #读取章节内容
    #     soup = BeautifulSoup(data,"html.parser")                     #构建BS数据
    #     text = eval('soup.'+self.opts['text'])
    #     filename = './novel/' + self.noveldata['title'] + '/' + repr(i) + '.txt'
    #     fo = open(filename, "wb")
    #     fo.write(text.encode('utf8'))
    #     fo.close()
    return chapters


def escape(txt, space=1):
    '''将txt文本中的空格、&、<、>、（"）、（'）转化成对应的的字符实体，以方便在html上显示'''
    txt = txt.replace('&', '&amp;')
    txt = txt.replace(' ', '&nbsp;')
    txt = txt.replace('<', '&lt;')
    txt = txt.replace('>', '&gt;')
    txt = txt.replace('"', '&quot;')
    txt = txt.replace('\'', '&apos;')
    txt = txt.replace('\r', space * '<br />')
    txt = txt.replace('\n', space * '<br />')
    return txt


def get_chapter_content(chapter_url, book_website):
    opts = CONFIG[book_website]
    try:
        soup = BeautifulSoup(requests.get(chapter_url, headers=header).content, "html.parser")
        content = eval('soup.' + opts['text'])
    except:
        content = '未找到章节内容,刷新重试'
    return content


def search_by_keyword(keyword):
    search_result_status = 0
    search_result_noveldata = []
    for id in get_id():
        novel_url = search_by_id(novelname=keyword, id=id)
        # print(novel_url)
        if novel_url == -1 or novel_url == -2:
            continue
        noveldata = get_novel_info(novel_url, id=id)
        # print(noveldata)
        if noveldata == -1 or (not noveldata.get('title', None)):
            continue
        search_result_noveldata.append(noveldata)
        if noveldata.get('title', None) == keyword:
            search_result_noveldata = []
            search_result_noveldata.append(noveldata)
            break
    if len(search_result_noveldata):
        return search_result_noveldata
    else:
        return None


def save_search_result_data_to_book(search_result_noveldata):
    search_resutl_books = []
    # book = None
    for noveldata in search_result_noveldata:
        bookname = noveldata['title'].strip()
        if Book.objects.filter(name=bookname).exists():
            continue
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
        try:
            book.save()
            search_resutl_books.append(book)
        except Exception as e:
            logging.error('保存失败: {0},原因: {1}'.format(bookname, e))
            continue
    logging.info("找到以下结果:{0}".format(search_resutl_books))
    return search_resutl_books


class SearchFailedException(Exception):
    pass


if __name__ == '__main__':
    search_by_keyword("斗破苍穹")

