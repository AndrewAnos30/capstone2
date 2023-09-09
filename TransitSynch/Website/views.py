# django_project/main/views.py
from django.shortcuts import render
from django.http import HttpResponse
from .models import ArticleSeries, Article

# Create your views here.
def homepage(request):


    return render(request=request, template_name='home.html')
