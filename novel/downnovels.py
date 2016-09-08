# coding: utf8
from bs4 import BeautifulSoup
import requests
import json


def get_download_links(page_url='http://www.txt56.com/list0-1.html'):
    '''
    输入: www.txt56.com/list0-1.html
    获取 www.txt56.com 上所有小说的信息，包括下载链接
    返回json格式
    '''
    agent = 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36'
    headers = {
        'User-Agent': agent
    }
    s = requests.session()

    try:
        r = s.get(page_url, headers=headers)
    except Exception as e:
        print(e)
        print('无法访问txt56')
        return False
    print(r.status_code)
    assert r.status_code == 200
    soup = BeautifulSoup(r.content, "html.parser")
    book_j_data = {}
    for dl in soup.find_all(name='dl'):
        # print(dl)
        try:
            book_index_url = dl.dt.a['href']
            book_id = book_index_url.split('.')[-2].split('/')[-1]
            book_down_url = 'http://www.txt56.com/txt/down/x{0}.html'.format(book_id)
            book_name = dl.dd.ul.li.a.get_text()
            book_author = dl.dd.ul.li.get_text()
            book_author = book_author.split('作者：')[-1]
            book_img_url = dl.dt.img['src']
            book_j_data.update({
            book_id:
                { 
                    'book_name': book_name, 
                    'book_author': book_author, 
                    'book_down_url': book_down_url,
                    'book_image_url': book_img_url
                }
            })
            # print(book_j_data)
        except Exception as e:
            print(e)
            pass

    try:
        next_page = soup.find(name='a', attrs={'class': 'next'})['href']
        if 'list0' not in next_page and 'list' in next_page:
            next_page = next_page.replace('list', 'list0')
        # get_download_links(next_page)
    except:
        next_page = None
        print('已经到了该页: {0}'.format(page_url))
        print('没有下一页了')
    return book_j_data, next_page


if __name__ == '__main__':
    page_url = 'http://www.txt56.com/list0-1.html'
    jsonfile = open('txt56_novels.json', 'a')
    while page_url:
        print(page_url)
        book_j_data, page_url = get_download_links(page_url=page_url)
        json.dump(book_j_data, jsonfile)
        jsonfile.write('\n')


