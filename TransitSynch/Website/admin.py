from django.contrib import admin
from .models import Location, Route, DataCrawl,CurrentPrice

admin.site.register(Location)
admin.site.register(Route)
admin.site.register(DataCrawl)
admin.site.register(CurrentPrice)