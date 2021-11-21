from django import forms
from django.contrib import auth
from django.http import request
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views.generic.base import ContextMixin
from validate_email import validate_email # Pip package
from .models import *
from django.contrib.auth import authenticate, login, logout # for dealing with registered user in database
from django.urls import reverse
from django.contrib.auth.decorators import login_required #decorator which allows if a view can be accessed by user
from helpers.decorators import auth_user_should_not_access # custom decorator which a user
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.encoding import force_bytes, force_str, force_text, DjangoUnicodeDecodeError
from .utils import generate_token
from .forms import MovieSearchForm
from django.core.mail import EmailMessage
from django.conf import settings
import threading #Sends emails in the background 
from django.forms import ModelForm
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.views import PasswordChangeView
from django.db.models.functions import Now
#Food.objects.filter(exp_date__gt=Now())
#####################PASSWORD CHANGE VIEW#############################
class PasswordsChangeView(PasswordChangeView):
    form_class = PasswordChangeForm
######################Email with threading for faster response#########################################        
class EmailThread(threading.Thread):
    def __init__(self, email):
        self.email=email
        threading.Thread.__init__(self)
    def run(self):
        self.email.send()
################################Send Activation Mail to User######################################### 
@auth_user_should_not_access
def send_activation_email(request,user):
    domain_name = get_current_site(request)
    email_subject = 'Verify your account'
    context = {'user':user, 'domain':domain_name, 'uid':urlsafe_base64_encode(force_bytes(user.pk)), 'token':generate_token.make_token(user)}
    email_body = render_to_string('userauth/activation.html',context)
    email=EmailMessage(subject=email_subject, body=email_body, from_email = settings.EMAIL_FROM_USER, to=[user.email])
    EmailThread(email).start()
###############################Registration View###########################################
@auth_user_should_not_access
def register(request):
    if request.method == "POST":
        context={'has_error':False,'data':request.POST, 'auth':auth}
######################################USER INFO INPUT#########################################        
        email = request.POST.get('email')
        username = request.POST.get('username')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')
        recieve_promo = request.POST.get('recieve_promo')
######################################USER INFO VALIDATION#########################################  
        if len(password)<8:
            messages.add_message(request,messages.ERROR,'Password should be atleast 8 characters')
            context['has_error']= True
        if password!=password2:
            messages.add_message(request,messages.ERROR,'Passwords do not match')
            context['has_error']= True
        if not validate_email(email):
            messages.add_message(request,messages.ERROR,'Invalid email address')
            context['has_error']= True
        if not username:
            messages.add_message(request,messages.ERROR,'Please supply a username for account')
            context['has_error']= True
        if User.objects.filter(username=username).exists():
            messages.add_message(request,messages.ERROR,'Username taken, choose another one')
            context['has_error']= True
        if User.objects.filter(email=email).exists():
            messages.add_message(request,messages.ERROR,'Email address is already in use')
            context['has_error']= True
        if context['has_error']:
           return render(request,'userauth/register.html',context)
######################################USER SAVE#########################################  
        user = User.objects.create_user(username=username, email=email)
        if recieve_promo == "on":
            user.recieve_promo=True
        user.set_password(password)
        user.save()
######################################USER SEND ACTIVATION MAIL#########################################  
        send_activation_email(request,user)
        messages.add_message(request,messages.SUCCESS,'User account created successfully, verify your email address to log in')
        return redirect('login')
    return render(request,'userauth/register.html')
######################################LOGIN VIEW#########################################  
@auth_user_should_not_access
def login_user(request):
    if request.method=='POST':
        context={'data':request.POST}
        username=request.POST.get('username')
        password=request.POST.get('password')
        user=authenticate(request, username=username,password=password)
######################################USER INFO INPUT#########################################        
        if not user:
            messages.add_message(request,messages.ERROR, 'Invalid credentials')
            return render(request,'userauth/login.html', context)
        if not user.is_email_verified:
            uid=urlsafe_base64_encode(force_bytes(user.pk))
            messages.add_message(request,messages.ERROR, f'Please verify E-mail address({user.email}) for {user.username}.')
            return render(request,'userauth/login.html', {'uid':uid,'user':user})
        login(request,user)
        messages.add_message(request,messages.SUCCESS, f'Log-in successful, Welcome {user.username}')
        return redirect(reverse('home'))
######################################USER LOGGED IN#########################################        
    return render(request,'userauth/login.html')
######################################USER LOGOUT#########################################  
@login_required    
def logout_user(request):
    logout(request)
    messages.add_message(request,messages.SUCCESS, 'Logout successful')
    return redirect(reverse('home'))
######################################USER ACTIVATION WITH DJANGO TOKENS#########################################  
def activate_user(request, uidb64, token):
    try:
        uid=force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except Exception as e:
        user=None
    if user and generate_token.check_token(user, token):
        user.is_email_verified=True
        user.save()
        messages.add_message(request, messages.SUCCESS,'Your email has been verified')
        return redirect(reverse('login'))            
    return render(request,'userauth/activation_failed.html',{'userid':uidb64})
#######################################if activation failed#########################################  
def retry_activation(request,uidb64):
    uid=force_text(urlsafe_base64_decode(uidb64))
    user = User.objects.get(pk=uid)
    send_activation_email(request,user)
    messages.add_message(request,messages.SUCCESS, f'Activation link sent to {user.email}')
    return redirect(reverse('home'))
###########PROFILE PAGE FOR USER##############
@login_required
def profile(request):
    user = request.user
    return render(request, 'ces/profilepage.html',{'user':user})#'userauth/profile.html'

#######################Payments Form######################
class PaymentForm(ModelForm):
    class Meta:
        model = User
        fields = ('card_no','valid_thru','valid_thru_y')
        labels  = {
        'card_no':'Card 1',
        'valid_thru':'Valid Till Month',
        'valid_thru_y':'Valid Till Year',
        }
class PaymentForm1(ModelForm):
    class Meta:
        model = User
        fields = ('card_no2','valid_thru1','valid_thru_y1')
        labels  = { 
        'card_no2':'Card 2', 
        'valid_thru1':'Valid Till Month',
        'valid_thru_y1':'Valid Till Year',
        }
class PaymentForm2(ModelForm):
    class Meta:
        model = User
        fields = ('card_no3','valid_thru2','valid_thru_y2')
        labels  = {
        'card_no3':'Card 3',
        'valid_thru2':'Valid Till Month',
        'valid_thru_y2':'Valid Till Year'
        }
@login_required
def payments(request):
    user = request.user
    if request.method=="POST":
        form = PaymentForm(request.POST, instance=request.user)
        if form.is_valid():
            card_no = form.cleaned_data['card_no']
            if not (len(card_no) == 16 and card_no.isnumeric()):
                messages.add_message(request,messages.ERROR, f"Invalid Card Details {card_no}")
                return render(request, 'userauth/payments.html',{'user':user,'form':form})
        form.save()
        messages.add_message(request,messages.SUCCESS, f'Card added successfully xxxx-xxxx-xxxx-{card_no[12:16]}')
        return redirect('profile')
    else:
        form=PaymentForm(instance=request.user)
    return render(request, 'userauth/payments.html',{'user':user,'form':form})
@login_required
############CARD 2#############
def payments1(request):
    user = request.user
    if request.method=="POST":
        form = PaymentForm1(request.POST, instance=request.user)
        if form.is_valid():
            card_no = form.cleaned_data['card_no2']
            if not (len(card_no) == 16 and card_no.isnumeric()):
                messages.add_message(request,messages.ERROR, f"Invalid Card Details {card_no}")
                return render(request, 'userauth/payments_add.html',{'user':user,'form':form})
        form.save()
        messages.add_message(request,messages.SUCCESS, f'Card added successfully xxxx-xxxx-xxxx-{card_no[12:16]}')
        return redirect('profile')
    else:
        form=PaymentForm1(instance=request.user)
    return render(request, 'userauth/payments_add.html',{'user':user,'form':form})
######################Card 3##############################
def payments2(request):
    user = request.user
    if request.method=="POST":
        form = PaymentForm2(request.POST, instance=request.user)
        if form.is_valid():
            card_no = form.cleaned_data['card_no3']
            if not (len(card_no) == 16 and card_no.isnumeric()):
                messages.add_message(request,messages.ERROR, f"Invalid Card Details {card_no}")
                return render(request, 'userauth/payments_add1.html',{'user':user,'form':form})
        form.save()
        messages.add_message(request,messages.SUCCESS, f'Card added successfully xxxx-xxxx-xxxx-{card_no[12:16]}')
        return redirect('profile')
    else:
        form=PaymentForm2(instance=request.user)
    return render(request, 'userauth/payments_add1.html',{'user':user,'form':form})
###################USER PROFILE EDIT#########################
class ProfileForm(ModelForm):   
    class Meta:
        model = User
        fields = ('username','first_name','last_name','recieve_promo','profile_pic','billing_address')
################Send user profile change update mail###################
def send_update_email(request,user):
    domain_name = get_current_site(request)
    email_subject = 'Profile changed successfully'
    context = {'user':user}
    email_body = render_to_string('userauth/profile_update.html',context)
    email=EmailMessage(subject=email_subject, body=email_body, from_email = settings.EMAIL_FROM_USER, to=[user.email])
    EmailThread(email).start()
@login_required
def editprofile(request):
    if request.method == "POST":
        form = ProfileForm(request.POST,request.FILES, instance = request.user)
        if form.is_valid():
            form.save()
            send_update_email(request, request.user)
            messages.add_message(request,messages.SUCCESS, 'Profile Updated Successfully')
        return redirect('profile')
    else:
        form = ProfileForm(instance = request.user)
    return render(request, 'ces/editprofile.html',{'form':form, 'user':request.user})

############################### Movie Search ###################################    
#################################################################################
def MovieSearch(request):
    movieSearch = Movies.objects
    moviescheduleSearch = ScheduleMovie.objects
    no_of_movies = movieSearch.all().count()
    if request.method == 'POST':
        moviesearchform2 = MovieSearchForm(request.POST)
        if moviesearchform2.is_valid():
            name=moviesearchform2.cleaned_data['title']
            genre=moviesearchform2.cleaned_data['genre']
            note = 'All the movies in our theatre'
            if(name and genre):
                foundname=movieSearch.filter(genre__icontains=genre)
                foundname=foundname.filter(title__icontains=name)
                foundschedule=moviescheduleSearch.filter(movie__genre__icontains=genre)
                foundschedule=foundschedule.filter(movie__name__icontains=name)
                if not foundname:
                    note = 'No search results for Movie name: %s in Genre %s' %(name,genre)
                else:
                    note = 'Here are the search results for Movie name: %s in Genre %s' %(name,genre)

            elif(name):
                foundname=movieSearch.filter(title__icontains=name)
                foundschedule=moviescheduleSearch.filter(movie__title__icontains=name)
                if not foundname:
                    note = 'No search results for Movie name: %s' %(name)
                else:
                    note = 'Here are the search results for Movie:  %s' %(name)
            elif(genre):
                foundname=movieSearch.filter(genre__icontains=genre)
                foundschedule=moviescheduleSearch.filter(movie__genre__icontains=genre)
                if not foundname:
                    note = 'No search results in genre %s' %(genre)
                else:
                    note = 'Here are the search results for Genre %s' %(genre)
            else:
                foundname=movieSearch.all()
                foundschedule=moviescheduleSearch.all()
            newmoviesearchform2=MovieSearchForm()
            return render(request, 'ces/search1.html',{'newmoviesearchform2':newmoviesearchform2,'note':note, 'moviesearch':foundname, 'count':no_of_movies,'time':foundschedule})
    else:
        moviesearchform=MovieSearchForm()
        return render(request, 'ces/search1.html',{'moviesearchform':moviesearchform,'count':no_of_movies})
#################################################################################
def sendPromo(request, promo_id):
    user = User.objects.filter(recieve_promo=True)
    promo = get_object_or_404(Promotions,pk=promo_id)
    code = promo.promo_code
    valid = promo.promo_validity
    contextp = {'promotion_name': code, 'validity':valid}
    domain_name = get_current_site(request)
    email_subject = 'You have a new promotion from CES'
    email_body = render_to_string('ces/promo_mail.html',contextp)
    for theuser in user:
        email=EmailMessage(subject=email_subject, body=email_body, from_email = settings.EMAIL_FROM_USER, to=[theuser.email])
        EmailThread(email).start()
    messages.add_message(request,messages.SUCCESS, 'Promotion sent successfully')
def playtrailer(request, key):
    movie = get_object_or_404(Movies,pk=key)
    trailer_link = movie.video 
    return render(request,'ces/trailer.html', {'trailer':trailer_link})
def select_showtime_home(request,key):
    movie = get_object_or_404(Movies,pk=key)
    title=movie.title
    showtime = ScheduleMovie.objects.filter(movie__title__exact=title)
    return render(request,'ces/showtimes.html',{'showtime':showtime,'movie':title})

class TicketForm(ModelForm):
    class Meta:
        model = Tickets
        exclude = ('show','user','isBookingCancelled')
@login_required
def select_ticket(request,key):
    user = request.user
    form = TicketForm(request.POST, instance=request.user)
    show = ScheduleMovie.objects.get(pk=key)
    seats_left = show.remaining_seats()
    if request.method=="POST":
        if form.is_valid():
            c=form.cleaned_data['ticket_child']
            a=form.cleaned_data['ticket_adult']
            s=form.cleaned_data['ticket_senior']
            if(c >=0 and a>=0 and s>=0) and (c+a+s>0):
                if (c+a+s <= seats_left):
                    show.booked_seats+=c+a+s
                    show.save()
                    Tickets.objects.create(user=user,show=show,ticket_child=c,ticket_adult=a,ticket_senior=s)
                    form.save()
                elif(c+a+s == seats_left):
                    messages.add_message(request,messages.ERROR, 'Show fullhouse')
                    return render(request, 'ces/ticket.html',{'user':user,'form':form,'show':show})
                else:
                    messages.add_message(request,messages.ERROR, 'Seats overflow, try selecting lesser seats')
                    return render(request, 'ces/ticket.html',{'user':user,'form':form,'show':show})
            else:
                messages.add_message(request,messages.ERROR, 'Seat quantity should be valid')
                return render(request, 'ces/ticket.html',{'user':user,'form':form,'show':show})

        messages.add_message(request,messages.SUCCESS, 'Tickets selected')
        return redirect('home')
    else:
        form=TicketForm(instance=request.user)
    return render(request, 'ces/ticket.html',{'user':user,'form':form,'show':show})

def select_ticketz(request, key):
    show = get_object_or_404(ScheduleMovie,pk=key)
    context={'show':show}
    return render(request, 'ces/ticket.html',context)