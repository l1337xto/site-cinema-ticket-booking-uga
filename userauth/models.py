from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    is_email_verified = models.BooleanField(default=False)
    recieve_promo = models.BooleanField(default=False)
    billing_address = models.CharField(max_length=100, default='')
    profile_pic = models.ImageField(blank=True, default='', upload_to='user_pics/')
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
    showDate = models.DateField(null=True, blank=True)
    showTimes = models.CharField(max_length=10, blank=True,
    choices=[('9.00 AM','9.00 AM'),('11.00 AM','11.00 AM'),('2.00 PM','2.00 PM'),('5.00 PM','5.00 PM'),('9.00 PM','9.00 PM'),('11.00 PM','11.00 PM')], default='')
    def __str__(self):
        return self.title

    # def save(self, *args, **kwargs):
    #     super().save(*args, **kwargs)
    #     abc = ['A', 'B', 'C', 'D', 'E', 'F']
    #     for j in range(6):
    #         for i in range(15):
    #             s = Seat(seat_id=abc[j] + str(i+1), cost=100, movie=self, show=self.show)
    #             s.save()
    
class Promotions(models.Model):
    promo_code = models.CharField(max_length=10)
    promo_validity = models.DateField()
    
    def __str__(self):
        return self.promo_code
     
class Seat(models.Model):
    seat_id = models.CharField(max_length=4)
    seat_state = models.BooleanField(default=False)
    cost = models.IntegerField()
    movie = models.ForeignKey(Movies, on_delete=models.CASCADE)
    # show = models.ForeignKey(Theatre, on_delete=models.CASCADE)

class ShowRoom(models.Model):
    showroom = models.IntegerField()
    # theatre = models.ForeignKey(Theatre)
    numSeats = models.IntegerField() # is there max amount of seats in instructions?
    movie = models.ForeignKey(Movies,on_delete=models.CASCADE)
    seat = models.ForeignKey(Seat, on_delete=models.CASCADE)

class Theatre(models.Model):
    theatre_name = models.CharField(max_length=50)
    city = models.CharField(max_length=20)
    showroom = models.ForeignKey(ShowRoom,on_delete=models.CASCADE)
    def __str__(self):
        return self.theatre_name
     

#theatre is not logical booking or show

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