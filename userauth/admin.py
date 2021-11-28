from django.contrib import admin
from .models import *
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin
from .views import sendPromo 
from django.db.models.functions import Now

admin.site.site_header='CES Admin'

admin.site.unregister(Group)

def Archive(modeladmin,request,queryset):
    for movie in queryset:
        queryset.update(archived=True)
    Archive.short_description = "Archive selected movies"
    
def Unarchive(modeladmin,request,queryset):
    for movie in queryset:
        queryset.update(archived=False)
    Unarchive.short_description = "Unarchive selected movies"

class ShowroomAdmin(admin.ModelAdmin):
    readonly_fields=('numSeats',)
    list_display = ('showroom','numSeats')

class MovieAdmin(admin.ModelAdmin):
    list_display=('title','archived','genre','rating')
    ordering=('archived',)
    actions=[Archive, Unarchive]

class UserAdmin(admin.ModelAdmin):
    exclude=('password','is_staff','last_login','groups','user_permissions','card_no','card_no2','card_no3','valid_thru','valid_thru_y','valid_thru1','valid_thru_y1','valid_thru2','valid_thru_y2',)
    list_display=('email','first_name','last_name', 'username','is_email_verified', 'recieve_promo')
    search_fields=('username','email')

class SeatAdmin(admin.ModelAdmin):
    list_display=('show',)

def send_promo_mail(modeladmin,request,queryset):
        for promouser in queryset:
            queryset.update(is_promo_sent=True)
            sendPromo(request, promouser.id)
        send_promo_mail.short_description = "Send the selected promotions"
def auto_delete_promo_expired(modeladmin, request,queryset):
    Promotions._base_manager.filter(promo_validity__lte=Now()).delete()
    auto_delete_promo_expired.short_description='Delete Expired Promotions'
class PromotionsAdmin(admin.ModelAdmin):
    list_display=('promo_code', 'promo_validity','is_promo_sent','less')
    Promotions._base_manager.filter(promo_validity__lte=Now()).delete()
    def has_delete_permission(self, request, obj=None):
        return False
        
    def get_readonly_fields(self, request, obj=None):
        if obj:
            return ['promo_code', 'promo_validity']
        else:
            return []
    actions = [send_promo_mail, auto_delete_promo_expired]

class ScheduleMovieAdmin(admin.ModelAdmin):
    model = ScheduleMovie
    ordering = ('PlayingOn',)
    movie = Movies.objects.filter(archived=True)
    list_display=('movie','PlayingOn','MovieTime','showroom','booked_seats','seats_left')
    readonly_fields = ('booked_seats','seats_left')
    ScheduleMovie._base_manager.filter(PlayingOn__lte=Now()).delete()
    def seats_left(self,obj):
        return obj.showroom.numSeats - obj.booked_seats

class MovieTimeAdmin(admin.ModelAdmin):
    exclude=('showDateTime',)
    readonly_fields=('showDateTime',)

def auto_delete_expired_tickets(modeladmin, request,queryset):
    for ticket in queryset:
        if ticket.should_booking_be_deleted():
            Tickets.objects.get(pk=ticket.pk).delete()
    auto_delete_expired_tickets.short_description='Delete Expired Tickets'

class TicketAdmin(admin.ModelAdmin):
    model=Tickets
    list_display=('user','show','time_created','total_tickets')
    try_del=Tickets.objects.filter(isBookingDone=True)
    for every in try_del:
        if every.should_booking_be_deleted():
            Tickets.objects.get(pk=every.pk).delete()
    actions = [auto_delete_expired_tickets]

admin.site.register(User,UserAdmin)
admin.site.register(Movies,MovieAdmin)
admin.site.register(Promotions, PromotionsAdmin)
admin.site.register(ScheduleMovie,ScheduleMovieAdmin)
admin.site.register(MovieShowTime)
admin.site.register(ShowRoom,ShowroomAdmin)
admin.site.register(Tickets, TicketAdmin)
admin.site.register(Seat,SeatAdmin)