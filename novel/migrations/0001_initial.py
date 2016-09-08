# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Book',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('name', models.CharField(verbose_name='书名', max_length=100)),
                ('source_site', models.CharField(verbose_name='来源网站', max_length=100)),
                ('author', models.CharField(default='暂无作者信息', verbose_name='作者', max_length=50)),
                ('img', models.CharField(default='', verbose_name='封面地址', max_length=200)),
                ('desc', models.CharField(default='', verbose_name='简介', max_length=1000)),
                ('index_url', models.CharField(verbose_name='主页', null=True, blank=True, max_length=200)),
                ('down_url', models.CharField(default='', verbose_name='下载地址', null=True, blank=True, max_length=200)),
                ('add_time', models.DateTimeField(verbose_name='入库时间', auto_now_add=True)),
                ('update_time', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
                ('hot', models.IntegerField(default=0, verbose_name='火热指数')),
                ('read_on_site', models.BooleanField(default=False, verbose_name='本站是否可读')),
            ],
            options={
                'verbose_name': '小说',
                'verbose_name_plural': '小说',
            },
        ),
        migrations.CreateModel(
            name='BookChapter',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('title', models.CharField(verbose_name='章节名称', max_length=100)),
                ('url', models.CharField(verbose_name='章节地址', max_length=200)),
                ('index', models.IntegerField(verbose_name='章节序号')),
                ('path', models.CharField(default='', verbose_name='内容路径', max_length=100)),
                ('book', models.ForeignKey(to='novel.Book')),
            ],
            options={
                'verbose_name': '小说章节',
                'verbose_name_plural': '小说章节',
                'ordering': ['-index'],
            },
        ),
        migrations.CreateModel(
            name='BookTag',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('tag_name', models.CharField(verbose_name='书本分类', unique=True, max_length=50)),
            ],
            options={
                'verbose_name': '书本分类',
                'verbose_name_plural': '书本分类',
            },
        ),
        migrations.AddField(
            model_name='book',
            name='tag',
            field=models.ForeignKey(blank=True, to='novel.BookTag', null=True),
        ),
    ]
