import sys, os, logging
import requests
from bs4 import BeautifulSoup
import time
from django.core.wsgi import get_wsgi_application


sys.path.extend(['/Users/zhangdesheng/Documents/python-learning/zds-git/newnovel/',])
os.environ.setdefault("DJANGO_SETTINGS_MODULE","newnovel.settings")
application = get_wsgi_application()

from novel.models import Book, BookTag, BookChapter


header = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.11; rv:46.0) Gecko/20100101 Firefox/46.0'}


def get_baidu_top_books():
    
    XHQH = 'http://top.baidu.com/buzz?b=353&c=10&fr=topbuzz_b7_c10'
    DSYQ = 'http://top.baidu.com/buzz?b=355&c=10&fr=topbuzz_b353_c10'
    CYJK = 'http://top.baidu.com/buzz?b=1509&c=10&fr=topbuzz_b459_c10'
    QCXS = 'http://top.baidu.com/buzz?b=1508&c=10&fr=topbuzz_b355_c10'
    WXXX = 'http://top.baidu.com/buzz?b=354&c=10&fr=topbuzz_b1508_c10'

    # 先找这四项
    hot_books = []
    for url in (XHQH, DSYQ, CYJK, QCXS, WXXX):
        try:
            _get = requests.get(url, headers=header)
            soup = BeautifulSoup(_get.content.decode('gbk', 'ignore'), "html.parser")
            # print(soup)
            for tr in soup.find_all('tr'):
                # print(tr);break;
                try:
                    bookname = tr.find(name='td', attrs={'class':'keyword'}).a.text.strip()
                    bookhotcount = tr.find(name='td', attrs={'class':'last'}).text.strip()
                    hot_books.append((bookname, bookhotcount))
                except:
                    continue
            time.sleep(0.2)
        except AttributeError as e:
            logging(e)
    hot_books = sorted(hot_books, key=lambda x: int(x[1]), reverse=True)
    return hot_books


def record_hot_book(bookname, hot_number):
    try:
        _ = requests.get('http://novels.freelycode.com/search/?bookname={0}'.format(bookname))
    except:
        pass
    if Book.objects.filter(name=bookname).exists():
        try:
            book = Book.objects.filter(name=bookname).update(hot=int(hot_number))
        except:
            logging.error('更新热度失败bookname:{0} hotnumber:{1}'.format(bookname, hot_number))
    return True


def update_all_books():
    for book in Book.objects.all().order_by('-hot'):
        try:
            _ = requests.get('http://novels.freelycode.com/update/{0}'.format(book.id), headers=header)
        except:
            logging.error('更新book_id: {0} 失败了'.format(book.id))
            pass
        time.sleep(0.2)


if __name__ == '__main__':
    hots = get_baidu_top_books()
    print(hots)
    # for bookname, hot_number in hots:
    #     try:
    #         record_hot_book(bookname, hot_number)
    #     except:
    #         continue
    # time.sleep(3)
    # update_all_books()
