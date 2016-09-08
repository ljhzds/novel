# coding=utf-8

from django.db import models

# Create your models here.

class BookTag(models.Model):
    tag_name = models.CharField(max_length=50, verbose_name='书本分类', unique=True)

    class Meta:
        verbose_name = '书本分类'
        verbose_name_plural = '书本分类'

    def __str__(self):
        return self.tag_name

    @property
    def countTagBooks(self):
        return Book.objects.filter(tag=self.id).count()


class Book(models.Model):
    name = models.CharField(max_length=100, verbose_name='书名')
    tag = models.ForeignKey(BookTag, blank=True, null=True)
    source_site = models.CharField(max_length=100, verbose_name='来源网站')
    author = models.CharField(max_length=50, verbose_name='作者', default='暂无作者信息')
    img = models.CharField(max_length=200, verbose_name='封面地址', default='')
    desc = models.CharField(max_length=1000, verbose_name='简介', default='')
    index_url = models.CharField(max_length=200, verbose_name='主页', blank=True, null=True)
    down_url = models.CharField(max_length=200, verbose_name='下载地址', blank=True, null=True, default='')

    add_time = models.DateTimeField(verbose_name='入库时间', auto_now_add=True)
    update_time = models.DateTimeField(verbose_name='更新时间', auto_now=True)
    
    hot = models.IntegerField(verbose_name='火热指数', default=0)
    read_on_site = models.BooleanField(verbose_name='本站是否可读', default=False)

    class Meta:
        verbose_name = '小说'
        verbose_name_plural = '小说'
    def __str__(self):
        return self.name

    @property
    def get_download_url(self):
        return None


class BookChapter(models.Model):
    book = models.ForeignKey(Book)
    title = models.CharField(max_length=100, verbose_name='章节名称')
    url = models.CharField(max_length=200, verbose_name='章节地址')
    index = models.IntegerField(verbose_name='章节序号')
    path = models.CharField(max_length=100, verbose_name='内容路径', default='')

    class Meta:
        ordering = ['-index']
        verbose_name = '小说章节'
        verbose_name_plural = '小说章节'

    def __str__(self):
        return self.title
