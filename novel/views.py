#coding : utf8
import logging

from django.http import HttpResponse
from django.template import RequestContext
from django.shortcuts import render_to_response, redirect
from django.utils.http import urlquote
from .models import Book, BookChapter
from .parse_novels import search as book_search, get_hot_books_by_json, search_like_bookname
from .parse_novels import record_books, get_hot_number
from .fetch_novel import save_search_result_data_to_book, search_by_keyword, save_content, get_chapter_content


def index(request):
    # hot_books = get_hot_books_by_json()[:24]
    hot_books = Book.objects.all().order_by('-hot')[:20]
    mycontext = {}
    mycontext.update({'books': hot_books})
    return render_to_response('index.html', context=mycontext, context_instance=RequestContext(request))


def search(request):
    mycontext = {}
    if 'bookname' in request.GET and request.GET['bookname']:
        bookname = request.GET['bookname'].strip()
        mycontext.update({'bookname': bookname})
        logging.info('查询: {0}'.format(bookname))
        if not Book.objects.filter(name=bookname).exists():
            # if not this book in, then search from the internet
            bookdata = search_by_keyword(bookname)
            if bookdata:
                search_result_books = save_search_result_data_to_book(bookdata)
        
        if Book.objects.filter(name=bookname).exists():
            books = Book.objects.filter(name=bookname)
        elif not Book.objects.filter(name=bookname).exists() and len(search_result_books)==0:
            books = Book.objects.filter(name__contains=bookname).order_by('-hot')[:4]
        elif len(search_result_books) > 0:
            books = search_result_books
        mycontext.update({'books': books})
        hot_books = Book.objects.all().order_by('-hot')[:8]
        mycontext.update({'hotbooks': hot_books})
    return render_to_response('search.html', context=mycontext, context_instance=RequestContext(request))


def book_index(request, book_id):
    try:
        book = Book.objects.get(pk=book_id)
        chapters = BookChapter.objects.filter(book=book).order_by('index')
        try:
            book_tag = book.tag
        except:
            book_tag = '暂无分类'
        return render_to_response('bookindex.html', {'book': book, 'chapters': chapters, 'book_tag': book_tag})
    except Book.DoesNotExist:
        logging.error('book does not exist')
        return redirect('novel:index')


def chapter(request, book_id, index):
    # print(book_id, index)
    mycontext = {}
    try:
        book = Book.objects.get(pk=book_id)
        chapter_count = BookChapter.objects.filter(book=book).count()
        chapter = BookChapter.objects.filter(book=book).filter(index=index).first()
        source_site = book.source_site
        title = chapter.title
        url = chapter.url
        content = get_chapter_content(url, source_site)
        # content
        # content = escape(content)
        mycontext.update({'book_id': book.pk})
        mycontext.update({'bookname': book.name})
        mycontext.update({'title': title})
        mycontext.update({'content': content})
        if int(index) > 0:
            mycontext.update({'previous_': str(int(index)-1)})
        if int(index) < chapter_count - 1:
            mycontext.update({'next_': int(index) + 1})

        # print(mycontext['chapter_content'])
        # book.get_next_by_pk
        return render_to_response('chapter.html', context=mycontext)
    except Book.DoesNotExist:
        return redirect('novel:index')
    except Exception as e:
        mycontext.update({'error': 'fetch content error, please reclick..'})
        logging.error(e)
        return redirect('novel:book', book_id)


def update(request, book_id):
    try:
        book = Book.objects.get(pk=book_id)
        # print(book.book_name, book.source_site, book.book_index_url)
        noveldata = {}
        noveldata.update({'id': book.source_site})
        noveldata.update({'content_link': book.index_url})
        chapters = save_content(noveldata=noveldata)
        for index, chapter in enumerate(chapters):
            # print(chapter)
            chapter_title, url = chapter
            bookchapter = None
            if BookChapter.objects.filter(book=book).filter(index=index).exists():
                pass
            else:
                bookchapter = BookChapter(book=book, title=chapter_title, url=url, index=index)
                bookchapter.save()
    except Book.DoesNotExist:
        logging.error('book does not exist')
    except Exception as e:
        logging.error('fetch book chapters error...')
        logging.error('{0}'.format(e))
    return redirect('novel:book', book_id=book_id)


def download(request, book_id):

    book = Book.objects.get(pk=book_id)
    file_name = book.name + '.txt'
    # print(file_name)

    def downloadbook():
        chapters = BookChapter.objects.filter(book=book).order_by('index')
        for chapter in chapters:
            title = chapter.chapter_name
            content = get_chapter_content(url=chapter.url, source_site=book.source_site)
            yield title + '\n' + content + '\n'

    response = StreamingHttpResponse(downloadbook())
    response['Content-Type'] = 'application/octet-stream'
    response['Content-Disposition'] = 'attachment;filename="{0}"'.format(urlquote(file_name))
    return response


def page_not_found(request):
    return render_to_response('404.html')


def page_error(request):
    return render_to_response('500.html')


def insert(request):
    return HttpResponse('已插入')

