import datetime
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.conf import settings
from django.shortcuts import render, redirect
from .forms import RegisterForm
from django.views.decorators.csrf import csrf_exempt

# Create your views here.
@csrf_exempt
def register_user(request) :
    form = RegisterForm()
    
    if request.user.is_authenticated :
        return redirect('main:main')
    
    if request.method == "POST" :
        form = RegisterForm(request.POST)
        if form.is_valid() :
            if form.cleaned_data['role'] == 'ADM' and form.cleaned_data['password1'] != settings.ADMIN_ACCOUNT_SECRET_TOKEN:
                messages.error(request, 'Invalid Admin Credentials')
                return redirect('authentication:register')
            
            form.save()
            messages.success(request, 'Your account has been successfully created!')
            return redirect('authentication:login')
        else :
            messages.error(request, 'Failed to create account')
            return redirect('authentication:register')
        
    context = {'form':form}
    return render(request, 'register.html', context)

@csrf_exempt
def login_user(request) :
    if request.user.is_authenticated :
        return redirect('main:main')
    
    if request.method == 'POST' :
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username = username, password = password)
        
        if user is not None :
            login(request, user)
            next = request.GET.get('next')
            if next is not None :
                response = redirect(next)
            else :
                response = redirect('main:main')
            response.set_cookie('user_login', user)
            return response
        else :
            messages.error(request, 'Invalid username or password')
            return redirect('authentication:login')

    return render(request, 'login.html')

def logout_user(request) :
    logout(request)
    response = redirect('main:main')
    response.delete_cookie('user_login')
    return response