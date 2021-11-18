from . import views
from django.urls import path
from django.contrib.auth import views as auth_views
urlpatterns = [
    path('login',views.login_user,name='login'),
    path('register',views.register,name='register'),
    path('logout',views.logout_user,name='logout_user'),
    path('activate_user/<uidb64>/<token>',views.activate_user,name='activation'),
    path('retry_activation/<uidb64>/',views.retry_activation,name='retry_activation'),
    path('profile',views.profile,name='profile'),
    path('payments',views.payments,name="payments"),
    path('addpay',views.payments1,name="addpay"),
    path('addpay1',views.payments2,name="addpay1"),
    path('search',views.MovieSearch,name='search'),
    path('editprofile',views.editprofile,name="editprofile"),
    path('trailer/<int:key>/',views.playtrailer, name='trailer'),
    path('selectshowhome/<int:key>',views.select_showtime_home, name='show_home'),

    ###########Password Reset#########
    path('reset_password',auth_views.PasswordResetView.as_view(template_name="userauth/password_reset.html"),name="reset_password"),
    path('reset_password_sent',auth_views.PasswordResetDoneView.as_view(template_name="userauth/password_reset_sent.html"),name="password_reset_done"),
    path('reset/<uidb64>/<token>',auth_views.PasswordResetConfirmView.as_view(template_name="userauth/password_reset_confirm.html"),name="password_reset_confirm"),
    path('reset_password_complete',auth_views.PasswordResetCompleteView.as_view(template_name="userauth/password_reset_complete.html"),name="password_reset_complete"),

    path('password/',auth_views.PasswordChangeView.as_view(template_name="userauth/password_change.html"),name="password_change"),
    path('password_change_done/',auth_views.PasswordChangeDoneView.as_view(template_name="userauth/password_change_done.html"),name="password_change_done"),

]