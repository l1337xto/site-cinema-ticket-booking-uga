from django.contrib import auth
from django.shortcuts import render, redirect
from django.contrib import messages
from validate_email import validate_email
from .models import User
from django.contrib.auth import authenticate, login, logout
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from helpers.decorators import auth_user_should_not_access
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.encoding import force_bytes, force_str, force_text, DjangoUnicodeDecodeError
from .utils import generate_token
from django.core.mail import EmailMessage
from django.conf import settings
import threading

######################Email with threading for faster response#########################################        
class EmailThread(threading.Thread):
    def __init__(self, email):
        self.email=email
        threading.Thread.__init__(self)
    def run(self):
        self.email.send()

################################Send Activation Mail to User#########################################        
def send_activation_email(request,user):
    domain_name = get_current_site(request)
    email_subject = 'Verify your account'
    context = {'user':user, 'domain':domain_name, 'uid':urlsafe_base64_encode(force_bytes(user.pk)), 'token':generate_token.make_token(user)}
    email_body = render_to_string('userauth/activation.html',context)

    email=EmailMessage(subject=email_subject, body=email_body, from_email = settings.EMAIL_FROM_USER, to=[user.email])
    EmailThread(email).start()


@auth_user_should_not_access
def register(request):
    if request.method == "POST":
        context={'has_error':False,'data':request.POST}
######################################USER INFO INPUT#########################################        
        email = request.POST.get('email')
        username = request.POST.get('username')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')
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
        user.set_password(password)
        user.save()

        send_activation_email(request,user)
        messages.add_message(request,messages.SUCCESS,'User account created successfully, verify your email address to log in')
        return redirect('login')
    return render(request,'userauth/register.html')


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
            messages.add_message(request,messages.ERROR, f'Please verify E-mail address({user.email}) for {user.username}.')
            return render(request,'userauth/login.html', context)
        login(request,user)
        messages.add_message(request,messages.SUCCESS, f'Log-in successful, Welcome {user.username}')
        return redirect(reverse('home'))
######################################USER LOGGED IN#########################################        
    return render(request,'userauth/login.html')
@login_required    
def logout_user(request):
    logout(request)
    messages.add_message(request,messages.SUCCESS, 'Logout successful')
    return redirect(reverse('home'))

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
    return render(request,'userauth/activation_failed.html',{'user':user})
