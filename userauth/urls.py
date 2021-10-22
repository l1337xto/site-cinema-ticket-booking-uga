from . import views
from django.urls import path
urlpatterns = [
    path('login',views.login_user,name='login'),
    path('register',views.register,name='register'),
    path('logout',views.logout_user,name='logout_user'),
    path('activate_user/<uidb64>/<token>',views.activate_user,name='activation'),

]