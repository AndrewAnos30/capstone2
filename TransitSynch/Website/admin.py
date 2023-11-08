from django.contrib import admin
from .models import  DataCrawl,CurrentPrice, CashierTransaction, TransportationRecord

admin.site.register(DataCrawl)
admin.site.register(CurrentPrice)
admin.site.register(CashierTransaction)
admin.site.register(TransportationRecord)