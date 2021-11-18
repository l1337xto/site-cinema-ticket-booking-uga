from django.urls import path
from . import views
urlpatterns = [
    path('',views.index,name='home'),
    path('detail/<int:movie_id>',views.movie_detail,name='movie_detail'),
]