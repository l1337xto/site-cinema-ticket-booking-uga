from django.contrib import auth
from django.http import request
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
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
from django.core.mail import EmailMessage
from django.conf import settings
import threading #Sends emails in the background 
from django.forms import ModelForm
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.views import PasswordChangeView

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
@login_required
def payments(request):
    user = request.user
    return render(request, 'userauth/payments.html',{'user':user})

###################USER PROFILE EDIT#########################
class ProfileForm(ModelForm):   
    class Meta:
        model = User
        fields = ('username','first_name','last_name','recieve_promo','profile_pic','billing_address')
def editprofile(request):
    if request.method == "POST":
        form = ProfileForm(request.POST,request.FILES, instance = request.user)
        if form.is_valid():
            form.save()
            messages.add_message(request,messages.SUCCESS, 'Profile Updated Successfully')
        return redirect('profile')
    else:
        form = ProfileForm(instance = request.user)
    return render(request, 'ces/editprofile.html',{'form':form, 'user':request.user})