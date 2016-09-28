# from django.test import TestCase

# Create your tests here.
import requests

if __name__ == '__main__':

    # index
    print('index')
    r = requests.get('http://127.0.0.1:8000/')
    assert r.status_code == 200
    print('search')
    r = requests.get('http://127.0.0.1:8000/search?bookname=大主宰')

    assert r.status_code == 200
    print('book')
    r = requests.get('http://127.0.0.1:8000/book/1')

    assert r.status_code == 200
    print('chapter')
    r = requests.get('http://127.0.0.1:8000/book/1/10')
    print(r.status_code)
    assert r.status_code == 200
    print('update')
    r = requests.get('http://127.0.0.1:8000/update/1')
    assert r.status_code == 200
    r = requests.get('http://127.0.0.1:8000/download/1')
    print('download')
    assert r.status_code == 200
