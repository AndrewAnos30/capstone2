from django.contrib import admin
from .models import Article, ArticleSeries



class ArticleSeriesAdmin(admin.ModelAdmin):
    list_displays = [
        'title',
        'subtitle',
        'slug',
        'published'
    ]

class ArticleAdmin(admin.ModelAdmin):
    list_displays= [
        'title',
        'subtitle',
        'article_slug',
        'content',
        'modified',
        'published',
        'series'
    ]

# Register your models here.
admin.site.register(Article, ArticleAdmin)
admin.site.register(ArticleSeries, ArticleSeriesAdmin)