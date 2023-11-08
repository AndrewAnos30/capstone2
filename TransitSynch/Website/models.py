from django.db import models
from django.utils import timezone
from users.models import CustomUser


    
class DataCrawl (models.Model):
    CrawlDate = models.CharField (max_length=200, null=True, blank=True)
    CrawlPHP = models.FloatField (null=True, blank=True)
    CrawlUSD = models.FloatField (null=True, blank=True)

    def __str__(self):
        return self.CrawlDate 
    

    
class CurrentPrice(models.Model):
    CurrentDate = models.DateField(null=True, blank=True)
    CurrentFarePUJ = models.FloatField(null=True, blank=True, default=0)
    CurrentSucceedingPUJ = models.FloatField(null=True, blank=True, default=0)
    CurrentDiesel = models.FloatField(null=True, blank=True, default=0)
    CurrentSucceedingBus = models.FloatField(null=True, blank=True, default=0)
    CurrentFareBus = models.FloatField(null=True, blank=True, default=0)
    Num = models.IntegerField (null=True, blank=True, default=1)
    
    def __str__(self):
        return str(self.CurrentDate)

class TranspoType(models.Model):

    STATUS = (
        ('PUJ', 'PUJ'),
        ('Modernized PUJ', 'Modernized PUJ'),
        ('AirConditioned PUJ', 'AirConditioned PUJ'),
        ('Regular PUJ', 'Regular PUJ'),
        ('Modernized Bus', 'Modernized Bus'),
    )

class CashierTransaction(models.Model):

    TransactionID = models.CharField (null= True, blank= True, max_length=20)
    CashierSN = models.CharField (null= True, blank= True, max_length=100)
    CommuterSN = models.CharField (null= True, blank= True, max_length=100) 
    CashIn = models.FloatField (null= True, blank= True, default=0)
    paidAmount = models.FloatField (null= True, blank= True, default=0)
    change = models.FloatField (null= True, blank= True, default=0)
    DateIn = models.DateTimeField (null= True, blank= True)

    def __str__(self):
        return str(self.TransactionID)
    

class TransportationRecord(models.Model):
    longitudeIN = models.FloatField(null=True, blank=True)
    latitudeIN = models.FloatField(null=True, blank=True)
    longitudeOUT = models.FloatField(null=True, blank=True)
    latitudeOUT = models.FloatField(null=True, blank=True)
    scan_type = models.CharField(max_length=20, null=True, blank=True)
    extracted_data = models.TextField(null=True, blank=True)
    scan_date = models.DateTimeField(auto_now_add=True)
    TranspoSN = models.CharField(max_length=25, unique=True, null=True, blank=True)
    user = models.CharField(max_length=30, null=True, blank=True)
    price = models.FloatField(null=True,blank=True)
    km = models.FloatField(null=True, blank=True)
    commuterStatus = models.CharField(max_length=25, null=True, blank=True)
    TranspoType = models.CharField(max_length=25, null=True, blank=True)
    
    def __str__(self):
        return str(self.TranspoSN)
