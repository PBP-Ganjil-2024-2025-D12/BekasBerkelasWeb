import json
from django.http import JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.conf import settings
from django.shortcuts import render, redirect
from .forms import RegisterForm
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def register_user(request):
    if request.method == "POST":
        data = request.POST
        print(data)
        
        form = RegisterForm(data)
        if form.is_valid():
            if form.cleaned_data['role'] == 'ADM' and form.cleaned_data['password1'] != settings.ADMIN_ACCOUNT_SECRET_TOKEN:
                return JsonResponse({
                    'status': 'failed',
                    'message': 'Invalid Admin Credentials'
                }, status=400)
            
            form.save()
            return JsonResponse({
                'status': 'success',
                'message': 'Your account has been successfully created!'
            }, status=200)
        else:
            return JsonResponse({
                'status': 'failed',
                'message': 'Failed to create account',
                'errors': form.errors
            }, status=400)
            
    form = RegisterForm()
    context = {'form': form}
    return render(request, 'register.html', context)

@csrf_exempt
def login_user(request):
    if request.method == 'POST':
        try:
            if request.content_type == 'application/json':
                data = json.loads(request.body)
                username = data.get('username')
                password = data.get('password')
            else:
                username = request.POST.get('username')
                password = request.POST.get('password')

            user = authenticate(request, username=username, password=password)
            
            if user is not None:
                login(request, user)
                return JsonResponse({
                    'status': True,
                    'username': user.username,
                    'id': user.id,
                    'role': user.userprofile.role,
                    'message': 'Login successful!'
                }, status=200)
            else:
                return JsonResponse({
                    "status": "failed",
                    "message": "Invalid username or password"
                }, status=401)
                
        except json.JSONDecodeError:
            return JsonResponse({
                'status': 'failed',
                'message': 'Invalid JSON data'
            }, status=400)

    return render(request, 'login.html')

@csrf_exempt
def logout_user(request):
    logout(request)
    return JsonResponse({
        "status": "success",
        "message": "Successfully logged out!"
    }, status=200)