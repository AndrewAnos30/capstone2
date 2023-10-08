from django.contrib import admin
from .models import Location, Route, DataCrawl

admin.site.register(Location)
admin.site.register(Route)
admin.site.register(DataCrawl)