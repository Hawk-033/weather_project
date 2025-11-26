
from django.shortcuts import render
from .models import WeatherRecord

def dashboard(request):
    records = WeatherRecord.objects.all()[:30]
    return render(request,'dashboard.html',{'records':records})
