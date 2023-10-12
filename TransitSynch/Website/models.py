from django.db import models
from django.utils import timezone

class Route(models.Model):
    Rname = models.CharField(max_length=50, null=True, blank=True)

    def __str__(self):
        return self.Rname  # This will display the Rname in the admin and other contexts

class Location(models.Model):
    LocName = models.CharField(max_length=200, null=True, blank=True)
    Coordinates = models.CharField(max_length=100, null=True, blank=True)
    route = models.ForeignKey(Route, on_delete=models.CASCADE, null=True, blank=True)  # Use ForeignKey to establish a relationship

    def __str__(self):
        return self.LocName  # This will display the LocName in the admin and other contexts
    
class DataCrawl (models.Model):
    CrawlDate = models.CharField (max_length=200, null=True, blank=True)
    CrawlPHP = models.FloatField (null=True, blank=True)
    CrawlUSD = models.FloatField (null=True, blank=True)

    def __str__(self):
        return self.CrawlDate 
    

    
class CurrentPrice(models.Model):
    CurrentDate = models.DateField(null=True, blank=True)
    CurrentFare = models.FloatField(null=True, blank=True, default=0)
    CurrentDiesel = models.FloatField(null=True, blank=True, default=0)
    CurrentSucceeding = models.FloatField(null=True, blank=True, default=0)
    Num = models.IntegerField (null=True, blank=True, default=1)
    
    def __str__(self):
        return str(self.CurrentDate)

