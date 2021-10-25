from django.contrib import admin
from .models import *
from django.contrib.auth.admin import UserAdmin

class UserAdmin(admin.ModelAdmin):
    list_display=('email', 'username','is_email_verified', 'recieve_promo')
    search_fields=('username','email')
class PromotionsAdmin(admin.ModelAdmin):
    list_display=('promo_code', 'promo_validity')
    search_fields = ('promo_code',)

admin.site.register(User,UserAdmin)
# Register your models here.
admin.site.register(Movies)
admin.site.register(Promotions, PromotionsAdmin)
admin.site.register(Shows)
