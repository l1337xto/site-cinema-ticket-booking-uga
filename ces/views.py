from django.shortcuts import render,get_object_or_404

from userauth.models import *
def index(request):
    movie = Movies.objects
    return render(request, 'ces/index.html',{'movies':movie})
def movie_detail(request, movie_id):
    movied = get_object_or_404(Movies, pk=movie_id)
    showtime = ScheduleMovie.objects.filter(movie__title__exact=movied.title)
    return render(request, 'ces/movie_detail.html',{'movied':movied,'time':showtime})