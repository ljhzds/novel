# coding=utf-8

from django.db import models
from django.conf import settings

# Create your models here.
class Config(models.Model):
    # 站点源信息
    site_short_name = models.CharField(max_length=20, verbose_name='ID', unique=True)
    site_desc = models.CharField(max_length=50, verbose_name='站点源')
    site_url = models.CharField(max_length=200, verbose_name='站点源URL')
    search_link = models.CharField(max_length=200, verbose_name='查询URL')
    search_keyword = models.CharField(max_length=20, verbose_name='查询参数')
    # 查询结果页面解析配置
    novel_link = models.CharField(max_length=200, verbose_name='小说主页地址')
    novel_name = models.CharField(max_length=100, verbose_name='书名')

    # 小说主页信息获取
    title = models.CharField(max_length=100, verbose_name='主页书名')
    description = models.CharField(max_length=200, verbose_name='主页简介')
    image = models.CharField(max_length=200, verbose_name='封面图片')
    category = models.CharField(max_length=200, verbose_name='分类')
    author = models.CharField(max_length=200, verbose_name='作者')
    status = models.CharField(max_length=200, verbose_name='更新状态')
    update = models.CharField(max_length=200, verbose_name='最后更新时间')
    latest = models.CharField(max_length=200, verbose_name='最近章节')

    # 章节信息
    chapter_list = models.CharField(max_length=200, verbose_name='章节列表')
    chapter_name = models.CharField(max_length=200, verbose_name='章节名称')
    chapter_link = models.CharField(max_length=200, verbose_name='章节地址')
    text = models.CharField(max_length=200, verbose_name='章节正文')

    #priority 优先级
    priority = models.IntegerField(verbose_name='查询优先级', default=1)

    class Meta:
        verbose_name = '源站点配置'
        verbose_name_plural = '源站点配置'

    def __str__(self):
        return self.site_desc


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
    source_site2 = models.ForeignKey(Config, verbose_name='站点源', default='', null= True, blank=True)
    author = models.CharField(max_length=50, verbose_name='作者', default='暂无作者信息')
    img = models.CharField(max_length=200, verbose_name='封面地址', default='')
    desc = models.CharField(max_length=1000, verbose_name='简介', default='')
    index_url = models.CharField(max_length=200, verbose_name='主页', blank=True, null=True)
    down_url = models.CharField(max_length=200, verbose_name='下载地址', blank=True, null=True, default='')

    add_time = models.DateTimeField(verbose_name='入库时间', auto_now_add=True)
    update_time = models.DateTimeField(verbose_name='更新时间', auto_now=True)
    
    hot = models.IntegerField(verbose_name='火热指数', default=0)
    read_on_site = models.BooleanField(verbose_name='本站是否可读', default=False)

    read_times = models.IntegerField(verbose_name='阅读次数', default=1)
    download_times = models.IntegerField(verbose_name='下载次数', default=1)

    class Meta:
        verbose_name = '小说'
        verbose_name_plural = '小说'
    def __str__(self):
        return self.name

    @property
    def get_default_source(self):
        try:
            site = Config.objects.get(site_short_name=self.source_site)
            return site.id
        except:
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


class Feedback(models.Model):
    title = models.CharField(max_length=100, verbose_name='问题')
    desc = models.CharField(max_length=500, verbose_name='详细描述')
    email = models.EmailField(max_length=50, verbose_name='邮箱', null=True, blank=True)

    add_time = models.DateTimeField(verbose_name='反馈时间', auto_now_add=True)

    done_flag = models.BooleanField(verbose_name='是否解决', default=False)

    class Meta:
        verbose_name='问题反馈'
        verbose_name_plural='问题反馈'  

    def __str__(self):
        return self.title


class FeedbackComment(models.Model):
    feedback = models.ForeignKey(Feedback, verbose_name='所属问题')
    parent_comment = models.ForeignKey('self', related_name='my_children', blank=True, null=True)
    comment = models.CharField(max_length=200, blank=True,null=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name='回复人', null=True, blank=True)

    def clean(self):
        if len(self.comment) ==0:
            raise ValidationError('评论内容不能为空')

    def __str__(self):
        return self.comment
