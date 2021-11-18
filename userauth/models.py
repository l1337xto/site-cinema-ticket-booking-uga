from django.db import models
from django.contrib.auth.models import AbstractUser
from cryptography.fernet import _MAX_CLOCK_SKEW, Fernet
from django.db.models.fields import BLANK_CHOICE_DASH
from django.db.models.fields.related import ManyToManyField #Encrypting data
from mirage import fields
from django.conf import settings
from embed_video.fields import EmbedVideoField
from django.db.models.functions import Now
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
    numSeats = models.IntegerField(help_text='Number of seats should be a positive input')
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
    objects = Scheduler()
    class Meta:
        unique_together = ('showroom', 'MovieTime','PlayingOn')
    def __str__(self):
        return self.movie.title
#################################################################################

class Promotions(models.Model):
    is_promo_sent = models.BooleanField(default=False, editable=False)
    promo_code = models.CharField(max_length=10, unique=True, editable=is_promo_sent,help_text='Promotion code once created is non-editable' )
    promo_validity = models.DateField()
    def __str__(self):
        return self.promo_code
     
class Seat(models.Model):
    seat_id = models.CharField(max_length=4)
    seat_state = models.BooleanField(default=False)
    cost = models.IntegerField()
    # show = models.ForeignKey(Theatre, on_delete=models.CASCADE)


class Tickets(models.Model):
    ticket_id = models.CharField(max_length=75)
    username = models.CharField(max_length=20)
    seat = models.ForeignKey(Seat, on_delete = models.CASCADE)
    date = models.DateTimeField()
    price = models.IntegerField()
    
class Bookings(models.Model):
    user = models.ManyToManyField(User)
    showroom = models.ForeignKey(ShowRoom,on_delete=models.CASCADE)
    promo = models.ForeignKey(Promotions,on_delete=models.CASCADE)
    seats = models.ForeignKey(Seat,on_delete=models.CASCADE)
    tickets = models.ForeignKey(Tickets,on_delete=models.CASCADE)
    #no need for date since tickets has date field?
    
class Shows(models.Model):
    running_movie=models.ManyToManyField(Movies) # a show has many movies with each movie having a data time showroom
    playing_at = models.ForeignKey(ShowRoom, on_delete=models.CASCADE,default='') # showroom has the seat defined has foreign key 
    date = models.DateField()
    time = models.TimeField()
    duration = models.IntegerField()