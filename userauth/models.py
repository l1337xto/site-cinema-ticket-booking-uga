from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models.fields import BLANK_CHOICE_DASH
from django.db.models.fields.related import ManyToManyField #Encrypting data
from mirage import fields
from django.conf import settings
from embed_video.fields import EmbedVideoField
from django.db.models.functions import Now
from django.core.validators import MaxValueValidator, MinValueValidator
from datetime import datetime
from django.contrib.postgres.fields import ArrayField
class User(AbstractUser):
    is_email_verified = models.BooleanField(default=False)
    recieve_promo = models.BooleanField(default=False)
    billing_address = models.CharField(max_length=100, default='')
    profile_pic = models.ImageField(blank=True, default='', upload_to='user_pics/')
    card_no = fields.EncryptedCharField(default='', blank=True)
    card_no2 = fields.EncryptedCharField(default='',blank=True)
    card_no3 = fields.EncryptedCharField(default='',blank=True)
    valid_thru = models.CharField(max_length=2, choices=[('1','1'),('2','2'),('3','3'),('4','4'),('5','5'),('6','6'),('7','7'),('8','8'),('9','9'),('10','10'),('11','11'),('12','12')], default='',blank=True)
    valid_thru_y = models.CharField(max_length=2,choices=[('21','21'),('22','22'),('23','23'),('24','24'),('25','25'),('26','26'),('27','27'),('28','29'),('28','29')], default='', blank=True)
    valid_thru1= models.CharField(max_length=2, choices=[('1','1'),('2','2'),('3','3'),('4','4'),('5','5'),('6','6'),('7','7'),('8','8'),('9','9'),('10','10'),('11','11'),('12','12')], default='',blank=True)
    valid_thru_y1 = models.CharField(max_length=2,choices=[('21','21'),('22','22'),('23','23'),('24','24'),('25','25'),('26','26'),('27','27'),('28','29'),('28','29')], default='', blank=True)
    valid_thru2 = models.CharField(max_length=2, choices=[('1','1'),('2','2'),('3','3'),('4','4'),('5','5'),('6','6'),('7','7'),('8','8'),('9','9'),('10','10'),('11','11'),('12','12')], default='',blank=True)
    valid_thru_y2 = models.CharField(max_length=2,choices=[('21','21'),('22','22'),('23','23'),('24','24'),('25','25'),('26','26'),('27','27'),('28','29'),('29','29')], default='', blank=True)
   
    def __str__(self):
        return self.email
    def card1(self):
        if self.card_no:
            return True
        else:
            return False
    def card2(self):
        if self.card_no2:
            return True
        else:
            return False
    def card3(self):
        if self.card_no3:
            return True
        else:
            return False

class Movies(models.Model):
    title = models.CharField(max_length=100,default='')
    genre = models.CharField(max_length=25, choices=[('Action','Action'), ('Adventure','Adventure'), ('Animation','Animation'),('Biography','Biography'), ('Comedy','Comedy'), ('Crime','Crime'),('Documentary','Documentary'), ('Drama','Drama'), ('Family','Family'),('Fantasy','Fantasy'), ('Filmnoir','Film-Noir'), ('Gameshow','Game-show'),('History','History'), ('Horror','Horror'), ('Music','Music'),('Musical','Musical'), ('Mystery','Mystery'), ('News','News'),('Realitytv','Reality-TV'), ('Romance','Romance'), ('Scifi','Sci-Fi'),('Sport','Sport'), ('Talkshow','Talk-Show'), ('Thriller','Thriller'),('War','War'), ('Western','Western')])
    cast = models.CharField(max_length=200,default='')
    director = models.CharField(max_length=100,default='')
    producer = models.CharField(max_length=100,default='')
    synopsis = models.CharField(max_length=300,default='')
    review = models.URLField(max_length=200,default='')
    thumbnail = models.ImageField(upload_to='images/',default='')
    trailer = models.URLField(max_length=200,default='')
    rating = models.CharField(max_length=100, choices = [('G','G General Audiences'),('PG','PG Parental Guidance Suggested'),('PG-13', 'PG-13 Parents Strongly Cautioned'),('R','R Restricted'),('NC-17', 'NC-17 Adults Only')],default='')
    archived = models.BooleanField(default=False,null=True,blank=True,help_text='Setting as yes will not allow users to book ticket for this movie')
    video = EmbedVideoField()
    def __str__(self):
        return self.title

    # def save(self, *args, **kwargs):
    #     super().save(*args, **kwargs)
    #     abc = ['A', 'B', 'C', 'D', 'E', 'F']
    #     for j in range(6):
    #         for i in range(15):
    #             s = Seat(seat_id=abc[j] + str(i+1), cost=100, movie=self, show=self.show)
    #             s.save()
class ShowRoom(models.Model):
    showroom = models.CharField(max_length=1,help_text='Single character theatre code',unique=True)
    numSeats = models.IntegerField(default=40)
    def __str__(self):
        return self.showroom

############################### Movie Schedule ###################################    
#################################################################################
class MovieTime(models.Model):
    showDateTime = models.DateField()
    def __str__(self):
        return str(self.showDateTime)
class MovieShowTime(models.Model):
    showTimes = models.TimeField()
    def __str__(self):
        return str(self.showTimes)

class Scheduler(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(PlayingOn__gte=Now())

class ScheduleMovie(models.Model):
    movie=models.ForeignKey(Movies,on_delete=models.CASCADE)
    PlayingOn = models.DateField(db_index=True)
    MovieTime = models.TextField(max_length=10,choices=[('7AM','7AM'),('9AM','9AM'),('11AM','11AM'),('1PM','1PM'),('3PM','3PM'),('5PM','5PM'),('7PM','7PM'),('9PM','9PM'),('11PM','11PM')])
    showroom = models.ForeignKey(ShowRoom,on_delete=models.CASCADE)
    ticket_child=models.FloatField(default=4.99)
    ticket_adult=models.FloatField(default=7.99)
    ticket_senior=models.FloatField(default=6.99)
    booked_seats=models.IntegerField(default=0, validators=[MaxValueValidator(40), MinValueValidator(0)])
    def remaining_seats(self):
        return self.showroom.numSeats - self.booked_seats
    objects = Scheduler()
    class Meta:
        unique_together = ('showroom', 'MovieTime','PlayingOn')
    def __str__(self):
        return self.movie.title
#################################################################################

class Seat(models.Model):
    seat_state = (["seat","seat"],["seat selected","seat selected"],["seat occupied","seat occupied"])
    seat_state_01 = models.CharField(default="seat",max_length=15,choices=seat_state)
    seat_state_02 = models.CharField(default="seat",max_length=15,choices=seat_state)
    seat_state_03 = models.CharField(default="seat",max_length=15,choices=seat_state)
    seat_state_04 = models.CharField(default="seat",max_length=15,choices=seat_state)
    seat_state_05 = models.CharField(default="seat",max_length=15,choices=seat_state)
    seat_state_06 = models.CharField(default="seat",max_length=15,choices=seat_state)
    seat_state_07 = models.CharField(default="seat",max_length=15,choices=seat_state)
    seat_state_08 = models.CharField(default="seat",max_length=15,choices=seat_state)
    seat_state_09 = models.CharField(default="seat",max_length=15,choices=seat_state)
    seat_state_10 = models.CharField(default="seat",max_length=15,choices=seat_state)
    seat_state_11 = models.CharField(default="seat",max_length=15,choices=seat_state)
    seat_state_12 = models.CharField(default="seat",max_length=15,choices=seat_state)
    seat_state_13 = models.CharField(default="seat",max_length=15,choices=seat_state)
    seat_state_14 = models.CharField(default="seat",max_length=15,choices=seat_state)
    seat_state_15 = models.CharField(default="seat",max_length=15,choices=seat_state)
    seat_state_16 = models.CharField(default="seat",max_length=15,choices=seat_state)
    seat_state_17 = models.CharField(default="seat",max_length=15,choices=seat_state)
    seat_state_18 = models.CharField(default="seat",max_length=15,choices=seat_state)
    seat_state_19 = models.CharField(max_length=15,default="seat",choices=seat_state)
    seat_state_20 = models.CharField(max_length=15,default="seat",choices=seat_state)
    seat_state_21 = models.CharField(max_length=15,default="seat",choices=seat_state)
    seat_state_22 = models.CharField(max_length=15,default="seat",choices=seat_state)
    seat_state_23 = models.CharField(max_length=15,default="seat",choices=seat_state)
    seat_state_24 = models.CharField(max_length=15,default="seat",choices=seat_state)
    seat_state_25 = models.CharField(max_length=15,default="seat",choices=seat_state)
    seat_state_26 = models.CharField(max_length=15,default="seat",choices=seat_state)
    seat_state_27 = models.CharField(max_length=15,default="seat",choices=seat_state)
    seat_state_28 = models.CharField(max_length=15,default="seat",choices=seat_state)
    seat_state_29 = models.CharField(max_length=15,default="seat",choices=seat_state)
    seat_state_30 = models.CharField(max_length=15,default="seat",choices=seat_state)
    seat_state_31 = models.CharField(max_length=15,default="seat",choices=seat_state)
    seat_state_32 = models.CharField(max_length=15,default="seat",choices=seat_state)
    seat_state_33 = models.CharField(max_length=15,default="seat",choices=seat_state)
    seat_state_34 = models.CharField(max_length=15,default="seat",choices=seat_state)
    seat_state_35 = models.CharField(max_length=15,default="seat",choices=seat_state)
    seat_state_36 = models.CharField(max_length=15,default="seat",choices=seat_state)
    seat_state_37 = models.CharField(max_length=15,default="seat",choices=seat_state)
    seat_state_38 = models.CharField(max_length=15,default="seat",choices=seat_state)
    seat_state_39 = models.CharField(max_length=15,default="seat",choices=seat_state)
    seat_state_40 = models.CharField(max_length=15,default="seat",choices=seat_state)
    seat_state_41 = models.CharField(max_length=15,default="seat",choices=seat_state)
    seat_state_42 = models.CharField(max_length=15,default="seat",choices=seat_state)
    seat_state_43 = models.CharField(max_length=15,default="seat",choices=seat_state)
    seat_state_44 = models.CharField(max_length=15,choices=seat_state,default="seat",)
    seat_state_45 = models.CharField(max_length=15,choices=seat_state,default="seat")
    seat_state_46 = models.CharField(max_length=15,choices=seat_state,default="seat",)
    seat_state_47 = models.CharField(max_length=15,default="seat",choices=seat_state)
    seat_state_48 = models.CharField(default="seat",max_length=15,choices=seat_state)
    show = models.OneToOneField(ScheduleMovie, on_delete=models.CASCADE)

    def __str__(self):
        return f'%s on %s at %s' % (self.show.movie.title,self.show.PlayingOn,self.show.MovieTime)

class Promotions(models.Model):
    less = models.IntegerField()
    is_promo_sent = models.BooleanField(default=False, editable=False)
    promo_code = models.CharField(max_length=10, unique=True)
    promo_validity = models.DateField()
    def __str__(self):
        return self.promo_code
    def get_discount(self):
        return (1-(self.less/100))

class Tickets(models.Model):
    isBookingDone=models.BooleanField(default=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    show = models.ForeignKey(ScheduleMovie,on_delete=models.CASCADE)
    ticket_child=models.IntegerField(default=0, validators=[MaxValueValidator(10), MinValueValidator(0)])
    ticket_adult=models.IntegerField(default=0, validators=[MaxValueValidator(10), MinValueValidator(0)])
    ticket_senior=models.IntegerField(default=0, validators=[MaxValueValidator(10), MinValueValidator(0)])
    time_created = models.DateTimeField(auto_now_add=True,auto_now=False)
    seat_data = models.TextField(blank=True, null=True)
    def __str__(self):
        return self.user.username
    def total_tickets(self):
        return self.ticket_child+self.ticket_senior+self.ticket_adult
    def order_total(self):
        return self.ticket_child*self.show.ticket_child+self.ticket_senior*self.show.ticket_senior+self.ticket_adult*self.show.ticket_adult
    def should_booking_be_deleted(self):
        delta = datetime.now() - self.time_created
        if (delta.total_seconds() > 600) & (self.isBookingDone==False):
            return True
        else:
            return False
    def order_total_promo(self,key):
        total = self.order_total()
        promo = Promotions.objects.get(pk=key)
        discount = promo.get_discount()
        total*=discount
        return round(total,2)
"""
class Bookings(models.Model):
    tickets = models.OneToOneField(Tickets,on_delete=models.CASCADE)
    total = models.IntegerField()
"""