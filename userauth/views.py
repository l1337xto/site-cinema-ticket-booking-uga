
from django import forms
from django.contrib import auth
from django.core.exceptions import ObjectDoesNotExist
from django.core.validators import EMPTY_VALUES
from django.http import request
from django.shortcuts import render, redirect, get_object_or_404, Http404
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
from .forms import MovieSearchForm, NewCardForm, PromotionForm
from django.core.mail import EmailMessage
from django.conf import settings
import threading #Sends emails in the background 
from django.forms import ModelForm
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.views import PasswordChangeView, logout_then_login
from django.db.models.functions import Now
from datetime import datetime, timezone, timedelta
#Any.objects.filter(exp_date__gt=Now())
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
    request.session.flush()
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
@login_required
def select_showtime_home(request,key):
    movie = get_object_or_404(Movies,pk=key)
    title=movie.title
    showtime = ScheduleMovie.objects.filter(movie__title__exact=title)
    return render(request,'ces/showtimes.html',{'showtime':showtime,'movie':title})

class TicketForm(ModelForm):
    class Meta:
        model = Tickets
        exclude = ('show','user','isBookingDone', 'time_created','seat_data')
@login_required
def select_ticket(request,key):
    user = request.user
    form = TicketForm(request.POST)
    show = get_object_or_404(ScheduleMovie,pk=key)
    seats_left = show.remaining_seats()
    request.session.set_expiry(600)
    expiry = request.session.get_expiry_age()
    expiry_time = request.session.get_expiry_date()
    if request.method=="POST":
        if form.is_valid():
            c=form.cleaned_data['ticket_child']
            a=form.cleaned_data['ticket_adult']
            s=form.cleaned_data['ticket_senior']
            if(c >=0 and a>=0 and s>=0) and (c+a+s>0):
                if (c+a+s <= seats_left) and (c+a+s <= 10):
                    if request.session:
                        show.booked_seats+=c+a+s
                        show.save()
                        bookedTicket = form.save(commit=False)
                        bookedTicket.user = user
                        bookedTicket.show = show
                        bookedTicket.time_created = datetime.now()
                        bookedTicket.save()
                        return redirect('seat',bookedTicket.pk)
                elif(c+a+s == seats_left):
                    messages.add_message(request,messages.ERROR, 'Show fullhouse')
                    return render(request, 'ces/ticket.html',{'user':user,'form':form,'show':show,'remain':seats_left})
                else:
                    messages.add_message(request,messages.ERROR, 'Seats overflow, try selecting lesser seats')
                    return render(request, 'ces/ticket.html',{'user':user,'form':form,'show':show,'remain':seats_left})
            else:
                messages.add_message(request,messages.ERROR, 'Seat quantity should be valid')
                return render(request, 'ces/ticket.html',{'user':user,'form':form,'show':show,'expiry':expiry,'expiryt':expiry_time,'remain':seats_left})
            messages.add_message(request,messages.ERROR, f'Session timed out due to in-activity' )
    else:
        form=TicketForm(instance=request.user)
    return render(request, 'ces/ticket.html',{'user':user,'form':form,'show':show,'expiry':expiry, 'expiryt':expiry_time,'remain':seats_left})
chosen_seats=[]
saved_seats=[]
@login_required
def seatselection(request, key):
    ticket = get_object_or_404(Tickets,pk=key)
    show = ScheduleMovie.objects.get(pk=ticket.show.pk)
    if not (Seat.objects.filter(show__pk=show.pk)):
        seat=Seat.objects.create(show=show)
    else:
        seat=Seat.objects.get(show__pk=show.pk)
    expiry = request.session.get_expiry_age()
    expiry_time = request.session.get_expiry_date()
    total_ticket_for_booking = ticket.ticket_adult+ticket.ticket_child+ticket.ticket_senior
    seats_remaining = show.remaining_seats()
    allow_payment=False
    if not request.method == "POST":
        saved_seats.clear()
        #chosen_seats.clear()
    if request.method == "GET":
        if len(chosen_seats) <= total_ticket_for_booking:
            if 'seat_0' in request.GET:
                seat01 = request.GET['seat_0']
                if seat01=='1' and seat.seat_state_01 == "seat":
                    seat.seat_state_01 = "seat occupied"
                    seat.save()
                    chosen_seats.append(seat01)
                if seat01=='2' and seat.seat_state_02 == "seat":
                    seat.seat_state_02 = "seat occupied"
                    seat.save()
                    chosen_seats.append(seat01)
                if seat01=='3' and seat.seat_state_03 == "seat":
                    seat.seat_state_03 = "seat occupied"
                    seat.save()
                    chosen_seats.append(seat01)
                if seat01=='4' and seat.seat_state_04 == "seat":
                    seat.seat_state_04 = "seat occupied"
                    seat.save()
                    chosen_seats.append(seat01)
                if seat01=='5' and seat.seat_state_05 == "seat":
                    seat.seat_state_05 = "seat occupied"
                    seat.save()
                    chosen_seats.append(seat01)
                if seat01=='6' and seat.seat_state_06 == "seat":
                    seat.seat_state_06 = "seat occupied"
                    seat.save()
                    chosen_seats.append(seat01)
                if seat01=='7' and seat.seat_state_07 == "seat":
                    seat.seat_state_07 = "seat occupied"
                    seat.save()
                    chosen_seats.append(seat01)
                if seat01=='8' and seat.seat_state_08 == "seat":
                    seat.seat_state_08 = "seat occupied"
                    seat.save()
                    chosen_seats.append(seat01)
                if seat01=='9' and seat.seat_state_09 == "seat":
                    seat.seat_state_09 = "seat occupied"
                    seat.save()
                    chosen_seats.append(seat01)
                if seat01=='10' and seat.seat_state_10 == "seat":
                    seat.seat_state_10 = "seat occupied"
                    seat.save()
                    chosen_seats.append(seat01)
                if seat01=='11' and seat.seat_state_11 == "seat":
                    seat.seat_state_11 = "seat occupied"
                    seat.save()
                    chosen_seats.append(seat01)
                if seat01=='12' and seat.seat_state_12 == "seat":
                    seat.seat_state_12 = "seat occupied"
                    seat.save()
                    chosen_seats.append(seat01)
                if seat01=='13' and seat.seat_state_13 == "seat":
                    seat.seat_state_13 = "seat occupied"
                    seat.save()
                    chosen_seats.append(seat01)
                if seat01=='14' and seat.seat_state_14 == "seat":
                    seat.seat_state_14 = "seat occupied"
                    seat.save()
                    chosen_seats.append(seat01)
                if seat01=='15' and seat.seat_state_15 == "seat":
                    seat.seat_state_15 = "seat occupied"
                    seat.save()
                    chosen_seats.append(seat01)
                if seat01=='16' and seat.seat_state_16 == "seat":
                    seat.seat_state_16 = "seat occupied"
                    seat.save()
                    chosen_seats.append(seat01)
                if seat01=='17' and seat.seat_state_17 == "seat":
                    seat.seat_state_17 = "seat occupied"
                    seat.save()
                    chosen_seats.append(seat01)
                if seat01=='18' and seat.seat_state_18 == "seat":
                    seat.seat_state_18 = "seat occupied"
                    seat.save()
                    chosen_seats.append(seat01)
                if seat01=='19' and seat.seat_state_19 == "seat":
                    seat.seat_state_19 = "seat occupied"
                    seat.save()
                    chosen_seats.append(seat01)
                if seat01=='20' and seat.seat_state_20 == "seat":
                    seat.seat_state_20 = "seat occupied"
                    seat.save()
                    chosen_seats.append(seat01)
                if seat01=='21' and seat.seat_state_21 == "seat":
                    seat.seat_state_21 = "seat occupied"
                    seat.save()
                    chosen_seats.append(seat01)
                if seat01=='22' and seat.seat_state_22 == "seat":
                    seat.seat_state_22 = "seat occupied"
                    seat.save()
                    chosen_seats.append(seat01)
                if seat01=='23' and seat.seat_state_23 == "seat":
                    seat.seat_state_23 = "seat occupied"
                    seat.save()
                    chosen_seats.append(seat01)
                if seat01=='24' and seat.seat_state_24 == "seat":
                    seat.seat_state_24 = "seat occupied"
                    seat.save()
                    chosen_seats.append(seat01)
                if seat01=='25' and seat.seat_state_25 == "seat":
                    seat.seat_state_25 = "seat occupied"
                    seat.save()
                    chosen_seats.append(seat01)
                if seat01=='26' and seat.seat_state_26 == "seat":
                    seat.seat_state_26 = "seat occupied"
                    seat.save()
                    chosen_seats.append(seat01)
                if seat01=='27' and seat.seat_state_27 == "seat":
                    seat.seat_state_27 = "seat occupied"
                    seat.save()
                    chosen_seats.append(seat01)
                if seat01=='28' and seat.seat_state_28 == "seat":
                    seat.seat_state_28 = "seat occupied"
                    seat.save()
                    chosen_seats.append(seat01)
                if seat01=='29' and seat.seat_state_29 == "seat":
                    seat.seat_state_29 = "seat occupied"
                    seat.save()
                    chosen_seats.append(seat01)
                if seat01=='30' and seat.seat_state_30 == "seat":
                    seat.seat_state_30 = "seat occupied"
                    seat.save()
                    chosen_seats.append(seat01)
                if seat01=='31' and seat.seat_state_31 == "seat":
                    seat.seat_state_31 = "seat occupied"
                    seat.save()
                    chosen_seats.append(seat01)
                if seat01=='32' and seat.seat_state_32 == "seat":
                    seat.seat_state_32 = "seat occupied"
                    seat.save()
                    chosen_seats.append(seat01)
                if seat01=='33' and seat.seat_state_33 == "seat":
                    seat.seat_state_33 = "seat occupied"
                    seat.save()
                    chosen_seats.append(seat01)
                if seat01=='34' and seat.seat_state_34 == "seat":
                    seat.seat_state_34 = "seat occupied"
                    seat.save()
                    chosen_seats.append(seat01)
                if seat01=='35' and seat.seat_state_35 == "seat":
                    seat.seat_state_35 = "seat occupied"
                    seat.save()
                    chosen_seats.append(seat01)
                if seat01=='36' and seat.seat_state_36 == "seat":
                    seat.seat_state_36 = "seat occupied"
                    seat.save()
                    chosen_seats.append(seat01)
                if seat01=='37' and seat.seat_state_37 == "seat":
                    seat.seat_state_37 = "seat occupied"
                    seat.save()
                    chosen_seats.append(seat01)
                if seat01=='38' and seat.seat_state_38 == "seat":
                    seat.seat_state_38 = "seat occupied"
                    seat.save()
                    chosen_seats.append(seat01)
                if seat01=='39' and seat.seat_state_39 == "seat":
                    seat.seat_state_39 = "seat occupied"
                    seat.save()
                    chosen_seats.append(seat01)
                if seat01=='40' and seat.seat_state_40 == "seat":
                    seat.seat_state_40 = "seat occupied"
                    seat.save()
                    chosen_seats.append(seat01)
                if seat01=='41' and seat.seat_state_41 == "seat":
                    seat.seat_state_41 = "seat occupied"
                    seat.save()
                    chosen_seats.append(seat01)
                if seat01=='42' and seat.seat_state_42 == "seat":
                    seat.seat_state_42 = "seat occupied"
                    seat.save()
                    chosen_seats.append(seat01)
                if seat01=='43' and seat.seat_state_43 == "seat":
                    seat.seat_state_43 = "seat occupied"
                    seat.save()
                    chosen_seats.append(seat01)
                if seat01=='44' and seat.seat_state_44 == "seat":
                    seat.seat_state_44 = "seat occupied"
                    seat.save()
                    chosen_seats.append(seat01)
                    chosen_seats.append(seat01)
                if seat01=='45' and seat.seat_state_45 == "seat":
                    seat.seat_state_45 = "seat occupied"
                    seat.save()
                    chosen_seats.append(seat01)
                if seat01=='46' and seat.seat_state_46 == "seat":
                    seat.seat_state_46 = "seat occupied"
                    seat.save()
                    chosen_seats.append(seat01)
                if seat01=='47' and seat.seat_state_47 == "seat":
                    seat.seat_state_47 = "seat occupied"
                    seat.save()
                    chosen_seats.append(seat01)
                if seat01=='48' and seat.seat_state_48 == "seat":
                    seat.seat_state_48 = "seat occupied"
                    seat.save()
                    chosen_seats.append(seat01)
                
                chosen_seats.sort()
    if len(chosen_seats) == total_ticket_for_booking:
        allow_payment=True
        temp_seat=''
        for seats_xYx in chosen_seats:
            saved_seats.append(seats_xYx)
            saved_seats.sort()
            temp_seat+=str(seats_xYx)+' '
        ticket.seat_data=temp_seat
        ticket.save()
        chosen_seats.clear()   
    saved_seats.sort()
    allowed_seats = total_ticket_for_booking - len(chosen_seats)
    #############TICKET CANCEL################
    if request.method =="POST":
        if request.POST.get('cancel'):
            showtoedit = ScheduleMovie.objects.get(pk=ticket.show.pk)
            showtoedit.booked_seats-=ticket.total_tickets()
            showtoedit.save()
            Tickets.objects.get(pk=ticket.pk).delete()
            for seat01 in saved_seats:
                if seat01=='1':
                    seat.seat_state_01 = "seat"
                    seat.save()
                if seat01=='2':
                    seat.seat_state_02 = "seat"
                    seat.save()
                if seat01=='3':
                    seat.seat_state_03 = "seat"
                    seat.save()
                if seat01=='4':
                    seat.seat_state_04 = "seat"
                    seat.save()
                if seat01=='5':
                    seat.seat_state_05 = "seat"
                    seat.save()
                if seat01=='6':
                    seat.seat_state_06 = "seat"
                    seat.save()
                if seat01=='7':
                    seat.seat_state_07 = "seat"
                    seat.save()
                if seat01=='8':
                    seat.seat_state_08 = "seat"
                    seat.save()
                if seat01=='9':
                    seat.seat_state_09 = "seat"
                    seat.save()
                if seat01=='10':
                    seat.seat_state_10 = "seat"
                    seat.save()
                if seat01=='11':
                    seat.seat_state_11 = "seat"
                    seat.save()
                if seat01=='12':
                    seat.seat_state_12 = "seat"
                    seat.save()
                if seat01=='13':
                    seat.seat_state_13 = "seat"
                    seat.save()
                if seat01=='14':
                    seat.seat_state_14 = "seat"
                    seat.save()
                if seat01=='15':
                    seat.seat_state_15 = "seat"
                    seat.save()
                if seat01=='16':
                    seat.seat_state_16 = "seat"
                    seat.save()
                if seat01=='17':
                    seat.seat_state_17 = "seat"
                    seat.save()
                if seat01=='18':
                    seat.seat_state_18 = "seat"
                    seat.save()
                if seat01=='19':
                    seat.seat_state_19 = "seat"
                    seat.save()
                if seat01=='20':
                    seat.seat_state_20 = "seat"
                    seat.save()
                if seat01=='21':
                    seat.seat_state_21 = "seat"
                    seat.save()
                if seat01=='22':
                    seat.seat_state_22 = "seat"
                    seat.save()
                if seat01=='23':
                    seat.seat_state_23 = "seat"
                    seat.save()
                if seat01=='24':
                    seat.seat_state_24 = "seat"
                    seat.save()
                if seat01=='25':
                    seat.seat_state_25 = "seat"
                    seat.save()
                if seat01=='26':
                    seat.seat_state_26 = "seat"
                    seat.save()
                if seat01=='27':
                    seat.seat_state_27 = "seat"
                    seat.save()
                if seat01=='28':
                    seat.seat_state_28 = "seat"
                    seat.save()
                if seat01=='29':
                    seat.seat_state_29 = "seat"
                    seat.save()
                if seat01=='30':
                    seat.seat_state_30 = "seat"
                    seat.save()
                if seat01=='31':
                    seat.seat_state_31 = "seat"
                    seat.save()
                if seat01=='32':
                    seat.seat_state_32 = "seat"
                    seat.save()
                if seat01=='33':
                    seat.seat_state_33 = "seat"
                    seat.save()
                if seat01=='34':
                    seat.seat_state_34 = "seat"
                    seat.save()
                if seat01=='35':
                    seat.seat_state_35 = "seat"
                    seat.save()
                if seat01=='36':
                    seat.seat_state_36 = "seat"
                    seat.save()
                if seat01=='37':
                    seat.seat_state_37 = "seat"
                    seat.save()
                if seat01=='38':
                    seat.seat_state_38 = "seat"
                    seat.save()
                if seat01=='39':
                    seat.seat_state_39 = "seat"
                    seat.save()
                if seat01=='40':
                    seat.seat_state_40 = "seat"
                    seat.save()
                if seat01=='41':
                    seat.seat_state_41 = "seat"
                    seat.save()
                if seat01=='42':
                    seat.seat_state_42 = "seat"
                    seat.save()
                if seat01=='43':
                    seat.seat_state_43 = "seat"
                    seat.save()
                if seat01=='44':
                    seat.seat_state_44 = "seat"
                    seat.save()
                if seat01=='45':
                    seat.seat_state_45 = "seat"
                    seat.save()
                if seat01=='46':
                    seat.seat_state_46 = "seat"
                    seat.save()
                if seat01=='47':
                    seat.seat_state_47 = "seat"
                    seat.save()
                if seat01=='48':
                    seat.seat_state_48 = "seat"
                    seat.save()
                messages.add_message(request,messages.SUCCESS, f'Cancelled ticket registration for seats: %s' % str(saved_seats) )
                return redirect('home')
    if(ticket.should_booking_be_deleted()):
        ticket.delete()
    context={'allowed_seats':allowed_seats,'saved_seats':saved_seats,'seats':chosen_seats,'allow_pay':allow_payment,'range': range(total_ticket_for_booking),'ticket':ticket,'qnty':total_ticket_for_booking,'seat_left': seats_remaining,'expiry':expiry, 'expiryt':expiry_time,'seat':seat}
    return render(request, 'ces/seat.html',context)

@login_required
def pay(request, key):
    ticket = get_object_or_404(Tickets,pk=key)
    if(ticket.should_booking_be_deleted()):
        ticket.delete()
    if request.method == "POST":
        if request.POST.get('cancel'):
            showtoedit = ScheduleMovie.objects.get(pk=ticket.show.pk)
            showtoedit.booked_seats-=ticket.total_tickets()
            showtoedit.save()
            Tickets.objects.get(pk=ticket.pk).delete()
            messages.add_message(request,messages.SUCCESS, f'Cancelled ticket registration')
            return redirect('home')
        form=PromotionForm(request.POST)
        discount=0
        if form.is_valid():
            code = form.cleaned_data['promo_code']
            error_me=''
            promo=Promotions.objects.filter(promo_code=code)
            if promo:
                promo = promo.first()
                discount=ticket.order_total_promo(promo.pk)
                if not payamount.objects.filter(ticket__pk=ticket.pk):
                    price = payamount.objects.create(ticket=ticket,ticket_cost=discount)
                else:
                    price = payamount.objects.get(ticket__pk=ticket.pk)
                    price.ticket_cost = discount
                    price.save()
            else:
                error_me = 'Promo Invalid'
                if not payamount.objects.filter(ticket__pk=ticket.pk):
                    price = payamount.objects.create(ticket=ticket,ticket_cost=ticket.order_total())
                else:
                    price = payamount.objects.get(ticket__pk=ticket.pk)
                    price.ticket_cost = ticket.order_total()
                    price.save()
            contextn={'ticket':ticket,'off':discount,'code':code,'promo':promo,'error_me':error_me,'form':form, 'payamount':price.ticket_cost}
            return render(request,'ces/payments.html',contextn)
        contextn={'form':form,'ticket':ticket,'off':discount}
        return render(request,'ces/payments.html',contextn)
    else:
        form = PromotionForm()
        context={'ticket':ticket,'form':form}
        return render(request,'ces/payments.html',context)
@login_required
def pay_saved(request,key):
    user = request.user
    ticket = get_object_or_404(Tickets,pk=key)
    payable_amount = payamount.objects.get(ticket__pk=key)
    if request.method == "POST":
        if request.POST.get('cancel'):
            showtoedit = ScheduleMovie.objects.get(pk=ticket.show.pk)
            showtoedit.booked_seats-=ticket.total_tickets()
            showtoedit.save()
            Tickets.objects.get(pk=ticket.pk).delete()
            messages.add_message(request,messages.SUCCESS, f'Cancelled ticket registration')
            return redirect('home')
    if request.method=="POST":         
        form = NewCardForm(request.POST)
        if form.is_valid():
            credit_card_no=form.cleaned_data['lname']
            expiry=form.cleaned_data['expiry']
            cvv=form.cleaned_data['cvv']
            if not (len(credit_card_no) == 16 and credit_card_no.isnumeric()):
                messages.add_message(request,messages.ERROR, f"Invalid Card Details {credit_card_no}")
                return render(request, 'ces/pay.html',{'user':user,'form':form,'ticket':ticket,'pay':payable_amount})
    context={'ticket':ticket,'user':user,'pay':payable_amount}
    return render(request,'ces/pay.html',context)
@login_required
def order_confirmation(request,key):
    ticket=Tickets.objects.get(pk=key)
    price = payamount.objects.get(ticket__pk=key)

    if not Bookings.objects.filter(tickets__pk=ticket.pk):
        booked = Bookings.objects.create(tickets=ticket,total=price.ticket_cost)
    else:
        booked = Bookings.objects.get(tickets__pk=ticket.pk)
    ticket.isBookingDone=True
    ticket.save()
########TICKET#########
    domain_name = get_current_site(request)
    email_subject = 'Your recent online ticket purchase at CES'
    context = {'user':ticket.user, 'domain':domain_name, 'uid':urlsafe_base64_encode(force_bytes(ticket.user.pk)), 'token':generate_token.make_token(ticket.user),'booked':booked}
    email_body = render_to_string('ces/orderconfirmationmail.html',context)
    email=EmailMessage(subject=email_subject, body=email_body, from_email = settings.EMAIL_FROM_USER, to=[ticket.user.email])
    EmailThread(email).start()
    return render(request,'ces/order_confirmation.html',context)
@login_required    
def order_history(request):
    user=request.user
    booking = Bookings.objects.filter(tickets__user__pk=user.pk)
    context={'r':booking}
    return render(request, 'ces/orderhistory.html',context)