from django.shortcuts import render
from django.contrib import messages
from validate_email import validate_email
from .models import User
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
            messages.add_message(request,messages.ERROR,'Passwords donot match')
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
        messages.add_message(request,messages.SUCCESS,'User account created successfully')

    return render(request,'userauth/register.html')

def login(request):
    return render(request,'userauth/login.html')
