from django.contrib import admin
from .models import *
from django.contrib.auth.admin import UserAdmin
admin.site.register(User,UserAdmin)
# Register your models here.
admin.site.register(Movies)
admin.site.register(Promotions)
admin.site.register(Shows)
