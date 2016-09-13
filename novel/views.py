#coding : utf8
import logging, json, time

from django.http import HttpResponse, StreamingHttpResponse, HttpResponseBadRequest
from django.template import RequestContext, Context
from django.template.loader import get_template
from django.shortcuts import render_to_response, redirect
from django.utils.http import urlquote
from django.core.paginator import Paginator
from django.views.decorators.csrf import csrf_exempt
from .models import Book, BookChapter, Feedback
from .parse_novels import search as book_search, get_hot_books_by_json, search_like_bookname
from .parse_novels import record_books, get_hot_number
# from .fetch_novel import save_search_result_data_to_book, search_by_keyword, save_content, get_chapter_content, escapefrom .fetch_novel import save_search_result_data_to_book, search_by_keyword, save_content, get_chapter_content, escape
from .fetch_novel import save_content, get_chapter_content, escape
from .fetch import search_by_config


def get_html(template_filename, context):
    this_context = context
    t = get_template(template_filename)
    content_html = t.render(Context(this_context))
    payload = {
        'content_html': content_html,
        'success': True
        }
    return HttpResponse(json.dumps(payload), content_type="application/json")


def index(request):
    # hot_books = get_hot_books_by_json()[:24]
    hot_books = Book.objects.all().order_by('-hot')[:20]
    mycontext = {}
    mycontext.update({'books': hot_books})
    return render_to_response('novel/index.html', context=mycontext, context_instance=RequestContext(request))


def search(request):
    start = time.time()
    mycontext = {}
    if 'bookname' in request.GET and request.GET['bookname']:
        bookname = request.GET['bookname'].strip()
        mycontext.update({'bookname': bookname})
        logging.info('查询: {0}'.format(bookname))
        if not Book.objects.filter(name=bookname).exists():
            # if not this book in, then search from the internet
            search_by_config(bookname)        
        if Book.objects.filter(name=bookname).exists():
            books = Book.objects.filter(name=bookname)
        else:
            books = Book.objects.filter(name__contains=bookname).order_by('-hot')[:4]
        mycontext.update({'books': books})
        hotbooks = Book.objects.all().order_by('-hot')[:8]
        mycontext.update({'hotbooks': hotbooks})
    end = time.time()
    print(end-start)
    return render_to_response('novel/search.html', context=mycontext, context_instance=RequestContext(request))


@csrf_exempt
def book_index(request, book_id):

    book = Book.objects.get(pk=book_id)
    chapters = BookChapter.objects.filter(book=book).order_by('index')
    paginator = Paginator(chapters, 144)
    page_count = paginator.num_pages
    page_range = paginator.page_range

    # ajax 分页请求处理
    if request.method=='POST' and request.is_ajax():
        current_page = int(request.POST.get('current_page')) + 1
        chapters = paginator.page(current_page)
        return get_html('novel/chapters.html', locals())

    chapters = paginator.page(1)
    return render_to_response('novel/bookindex.html', locals())


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
        content = escape(content)
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
        return render_to_response('novel/chapter.html', context=mycontext)
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
    logging.info('download book: {0} begin'.format(book_id))
    book = Book.objects.get(pk=book_id)
    file_name = book.name + '.txt'
    # print(file_name)

    def downloadbook():
        chapters = BookChapter.objects.filter(book_id=book_id).order_by('index')
        for chapter in chapters:
            title = chapter.title
            content = get_chapter_content(chapter_url=chapter.url, book_website=book.source_site)
            yield title + '\n' + content + '\n'

    response = StreamingHttpResponse(downloadbook())
    response['Content-Type'] = 'application/octet-stream'
    response['Content-Disposition'] = 'attachment;filename="{0}"'.format(urlquote(file_name))
    logging.info('download book: {0} end'.format(book_id))
    return response


def page_not_found(request):
    return render_to_response('404.html')


def page_error(request):
    return render_to_response('500.html')


def insert(request):
    return HttpResponse('已插入')


@csrf_exempt
def feedback(request):

    if request.method == 'GET':
        feedbacks = Feedback.objects.all().order_by('-add_time')[:5]
        return render_to_response('novel/feedback.html', locals())
    elif request.method == 'POST':
        title = request.POST.get('title')
        desc = request.POST.get('desc')
        email = request.POST.get('email')
        fb = Feedback(title=title, desc=desc, email=email)
        fb.save()
        return redirect('novel:feedback')
    else:
        return HttpResponseBadRequest('非法访问方式.')


