from django.contrib import admin
from .models import Book, BookChapter, BookTag, Config


class BookAdmin(admin.ModelAdmin):
    list_display = ("name", "show_tag", "author", "source_site",
                    "index_url", "add_time", "update_time", "hot")
    # readonly_fields = ("book_name", "book_author", "book_website", "book_index_url", "book_add_time", "show_tag")

    list_filter = ("author", "source_site")

    def show_tag(self, book):
        return book.tag


class BookChapterAdmin(admin.ModelAdmin):
    list_display = ('title', 'url', 'index', "path")
    list_filter = ('book',)


class ConfigAdmin(admin.ModelAdmin):
    pass


admin.site.register(BookChapter, admin_class=BookChapterAdmin)
admin.site.register(Book, admin_class=BookAdmin)
admin.site.register(Config, admin_class=ConfigAdmin)
