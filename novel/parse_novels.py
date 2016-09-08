# coding: utf8

import json, os.path
from django.conf import settings

BASE_DIR = settings.BASE_DIR
json_file_dir = os.path.join(BASE_DIR, 'novel')
all_book_json = os.path.join(json_file_dir, 'txt56_novels.json')
hot_book_json = os.path.join(json_file_dir, 'hotbooks.json')
hot_in_record = os.path.join(json_file_dir, 'hots.json')
def record_books():
    records = dict()
    with open(all_book_json) as bookdata:
        for line in bookdata:
            books = json.loads(line)
            records.update(books)
    return records


def search(bookname, allbook=record_books()):
    bookname = bookname.strip()
    books = record_books()
    for book_id in books:
        # print(book_id)
        if bookname == books[book_id]['book_name'].strip():
            book_name = bookname
            book_down_url = books[book_id]['book_down_url']
            book_img_url = books[book_id]['book_image_url']
            book_author = books[book_id]['book_author']
            return (book_name, book_author, book_down_url, book_img_url)
    return None


def search_like_bookname(bookname, allbook=record_books()):
    bookname = bookname.strip()
    result = []
    for book_id in allbook:
        if bookname in allbook[book_id]['book_name']:
            book_name = allbook[book_id]['book_name'].strip()
            book_down_url = allbook[book_id]['book_down_url']
            book_img_url = allbook[book_id]['book_image_url']
            book_author = allbook[book_id]['book_author']
            result.append((book_name, book_author, book_down_url, book_img_url))
    if len(result) == 0: result = None
    return result


def get_hot_books_by_dict():
    allbook = record_books()
    hot_records = list()
    with open(hot_book_json) as hot:
        for book in json.load(hot):
            record = search(book[0], allbook=allbook)
            if record:
                hot_records.append((record, int(book[1])))
                # print(hot_records)
    hot_records = sorted(hot_records, key=lambda x: int(x[1]), reverse=True)
    hots = [hot[0] for hot in hot_records]
    print(hots)
    with open(hot_in_record, 'w') as hot:
        json.dump(hots, hot)
    return hots


def get_hot_books_by_json():
    with open(hot_in_record) as hot:
        return json.load(hot)


def get_hot_number(bookname):
    with open(hot_book_json) as hot:
        for book in json.load(hot):
            if book[0] == bookname:
                # print(int(book[1]))
                return int(book[1])
    return 0


if __name__ == '__main__':
    # print(len(record_books()))
    # hots = get_hot_books_by_dict()
    # print(1)
    hots2 = get_hot_books_by_json()
    print(hots2)
    # # print(len(hots2))
    # book = search('永夜君王')
    # print(book)
    # print(hots==hots2)
    # print(len(hots))
    # search('我们是兄弟')