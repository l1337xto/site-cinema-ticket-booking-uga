from django.shortcuts import render
from userauth.models import *
def index(request):
    movie = Movies.objects
    return render(request, 'ces/index.html',{'movies':movie})
