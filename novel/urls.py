"""bhzd URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""
from django.conf.urls import include, url
from . import views

app_name = 'novel'
urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^search/', views.search, name='search'),
    url(r'^book/(?P<book_id>[0-9]+)/$', views.book_index, name='book'),
    url(r'^book/(?P<book_id>[0-9]+)/(?P<index>[0-9]+)/$', views.chapter, name='chapter'),
    url(r'^update/(?P<book_id>[0-9]+)/$', views.update, name='update'),
    url(r'^download/(?P<book_id>[0-9]+)/$', views.download, name='download'),
    url(r'^feedback/', views.feedback, name='feedback'),
]
