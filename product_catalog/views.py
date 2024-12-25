from django.shortcuts import render, redirect
from .models import Car
from django.contrib.auth.decorators import login_required
from .forms import CarForm, CarFilterForm
from authentication.models import UserProfile
from django.shortcuts import get_object_or_404
from wishlist.models import Wishlist
from django.http import JsonResponse
from django.core import serializers
import uuid
from django.http import HttpResponse
from django.contrib import messages
from django.http import JsonResponse
from django.contrib.auth.models import User
import json
from django.views.decorators.csrf import csrf_exempt


@csrf_exempt
def delete_flutter(request):
    print(f"Received {request.method} request")
    if request.method == 'POST':
        print(f"Raw data received: {request.body}")

        data = json.loads(request.body)
        car_id = data.get('car_id')
        username = data.get('username')

        print(f"Car ID extracted: {car_id}")
        print(f"Username extracted: {username}")

        car = get_object_or_404(Car, id=car_id)
        if car.seller.username == username:
            car.delete()
            response_data = {"status": "success", "message": "Car deleted successfully"}
            return HttpResponse(json.dumps(response_data), content_type="application/json", status=200)
        else:
            response_data = {"status": "error", "message": "Unauthorized to delete this car"}
            return HttpResponse(json.dumps(response_data), content_type="application/json", status=403)

def get_seller_verif(request, username):
    try:
        # Retrieve the user by username
        user = User.objects.get(username=username)
        
        # Check if the user has a profile and is verified
        seller_verif = user.userprofile.is_verified
        return JsonResponse({'seller_verif': seller_verif}, safe=False)
    except User.DoesNotExist:
        return JsonResponse({'error': 'User not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def get_seller_contact(request, car_id):
    try:
        car = Car.objects.get(id=car_id)
        seller_email = car.seller.email
        # Assuming `no_telp` is a field in a related `SellerProfile` model
        seller_phone_number = car.seller.userprofile.no_telp  # Adjust if no_telp is elsewhere
        return JsonResponse({
            'email': seller_email,
            'no_telp': seller_phone_number,
        }, safe=False)
    except Car.DoesNotExist:
        return JsonResponse({'error': 'Car not found'}, status=404)
    except AttributeError:
        return JsonResponse({'error': 'Seller profile or contact details are incomplete'}, status=500)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
    
def get_seller_username(request, car_id):
    try:
        car = Car.objects.get(id=car_id)
        seller_username = car.seller.username
        return JsonResponse({'seller_username': seller_username}, safe=False)
    except Car.DoesNotExist:
        return JsonResponse({'error': 'Car not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
    
@csrf_exempt
def delete_flutter_admin(request):
    print(f"Received {request.method} request")
    if request.method == 'POST':
        print(f"Raw data received: {request.body}")

        data = json.loads(request.body)
        car_id = data.get('car_id')

        print(f"Car ID extracted: {car_id}")

        car = get_object_or_404(Car, id=car_id)
        car.delete()
        response_data = {"status": "success", "message": "Car deleted successfully"}
        return HttpResponse(json.dumps(response_data), content_type="application/json", status=200)
    
def show_all_cars(request):
    data = Car.objects.all() 
    return HttpResponse(serializers.serialize("json", data), content_type="application/json")

def search_filter_cars(request):
    # Get all cars or filter based on parameters
    cars = Car.objects.all()

    # Apply search and filter parameters
    car_name = request.GET.get('car_name')
    brand = request.GET.get('brand')
    price_max = request.GET.get('price_max')
    year = request.GET.get('year')  # Retrieve 'year' from request
    plate_type = request.GET.get('plate_type')  # Retrieve 'plate_type' from request
    transmission = request.GET.get('transmission')

    if year:
        cars = cars.filter(year=year)
    if plate_type:
        cars = cars.filter(plate_type=plate_type)
    if car_name:
        cars = cars.filter(car_name__icontains=car_name)
    if brand:
        cars = cars.filter(brand__icontains=brand)
    if price_max:
        cars = cars.filter(price__lte=float(price_max))
    if transmission:
        cars = cars.filter(transmission=transmission)

    # Serialize data including all fields of the Car model
    car_data = serializers.serialize("json", cars)

    return HttpResponse(car_data, content_type="application/json")

@csrf_exempt
def filter_cars(request):
    # Debugging the request method
    print(f"Received {request.method} request")
    cars = Car.objects.all()

    if request.method == 'POST':
            # Debugging raw request body
            print(f"Raw data received: {request.body}")

            data = json.loads(request.body)
            username = data.get('username')

            # Debugging extracted username
            print(f"Username extracted: {username}")

            cars2 = cars.filter(seller__username=username)
            car_data = serializers.serialize("json", cars2)

            # Debugging the filtered car data
            return HttpResponse(car_data, content_type="application/json")

def user_profile_to_dict(user_profile):
    return {
        'user_id': user_profile.user.id,
        'username': user_profile.user.username,
        'name': user_profile.name,
        'email': user_profile.email,
        'no_telp': user_profile.no_telp,
        'role': user_profile.role,
        'role_display': user_profile.get_role_display(),  # This gets the human-readable version of the role
        'profile_picture': user_profile.profile_picture if user_profile.profile_picture else "default_picture_url",
        'profile_picture_id': user_profile.profile_picture_id,
        'is_verified': user_profile.is_verified
    }

@login_required
def show_user_profile_json(request):
    try:
        user_profile = UserProfile.objects.get(user=request.user)
        user_profile_data = user_profile_to_dict(user_profile)
        return JsonResponse(user_profile_data)  # Returns the user profile data as JSON
    except UserProfile.DoesNotExist:
        return JsonResponse({
            "status": False,
            "message": "User profile not found."
        }, status=404)

@login_required
def mobil_saya(request):
    user_profile = UserProfile.objects.get(user=request.user)
    if user_profile.role == 'SEL':
        cars = Car.objects.filter(seller=request.user)
    else:
        return redirect('product_catalog:car_list')
    form = CarFilterForm(request.GET)
    user_wishlist = Wishlist.objects.filter(user=request.user).values_list('id', flat=True)

    if form.is_valid():
        car_name = form.cleaned_data.get('car_name')
        brand = form.cleaned_data.get('brand')
        year = form.cleaned_data.get('year')
        mileage = form.cleaned_data.get('mileage')
        location = form.cleaned_data.get('location')
        transmission = form.cleaned_data.get('transmission')
        plate_type = form.cleaned_data.get('plate_type')

        if car_name:
            cars = cars.filter(car_name__icontains=car_name)
        if brand:
            cars = cars.filter(brand__icontains=brand)
        if year:
            cars = cars.filter(year=year)
        if mileage:
            cars = cars.filter(mileage=mileage)
        if location:
            cars = cars.filter(location__icontains=location)
        if transmission:
            cars = cars.filter(transmission=transmission)
        if plate_type:
            cars = cars.filter(plate_type=plate_type)

        if form.cleaned_data.get('rear_camera'):
            cars = cars.filter(rear_camera=True)
        if form.cleaned_data.get('sun_roof'):
            cars = cars.filter(sun_roof=True)
        if form.cleaned_data.get('auto_retract_mirror'):
            cars = cars.filter(auto_retract_mirror=True)
        if form.cleaned_data.get('electric_parking_brake'):
            cars = cars.filter(electric_parking_brake=True)
        if form.cleaned_data.get('map_navigator'):
            cars = cars.filter(map_navigator=True)
        if form.cleaned_data.get('vehicle_stability_control'):
            cars = cars.filter(vehicle_stability_control=True)
        if form.cleaned_data.get('keyless_push_start'):
            cars = cars.filter(keyless_push_start=True)
        if form.cleaned_data.get('sports_mode'):
            cars = cars.filter(sports_mode=True)
        if form.cleaned_data.get('camera_360_view'):
            cars = cars.filter(camera_360_view=True)
        if form.cleaned_data.get('power_sliding_door'):
            cars = cars.filter(power_sliding_door=True)
        if form.cleaned_data.get('auto_cruise_control'):
            cars = cars.filter(auto_cruise_control=True)

        price_min = form.cleaned_data.get('price_min')
        price_max = form.cleaned_data.get('price_max')
        instalment_min = form.cleaned_data.get('instalment_min')
        instalment_max = form.cleaned_data.get('instalment_max')

        if price_min is not None:
            cars = cars.filter(price__gte=price_min)
        if price_max is not None:
            cars = cars.filter(price__lte=price_max)
        if instalment_min is not None:
            cars = cars.filter(instalment__gte=instalment_min)
        if instalment_max is not None:
            cars = cars.filter(instalment__lte=instalment_max)

        context = {
            'cars': cars,
            'form': form,
            'is_seller': user_profile.role == 'SEL',
            'is_buyer': user_profile.role == 'BUY',
            'is_admin': user_profile.role == 'ADM',
            'user_wishlist': user_wishlist,
        }
        return render(request, 'mobil_saya.html', context)
    
@login_required   
def contact_seller(request, car_id):
    try:
        car = Car.objects.get(id=car_id)
        seller_email = car.seller.userprofile.email
        seller_phone = car.seller.userprofile.no_telp
        data = {
            'email': seller_email,
            'phone': seller_phone,
        }
        return JsonResponse(data)
    except Car.DoesNotExist:
        return JsonResponse({'error': 'Car not found'}, status=404)

@csrf_exempt
def view_details_json(request, car_id):
    try:
        car = get_object_or_404(Car, pk=car_id)
        car_data = {
            "seller": car.seller.id,
            "car_name": car.car_name,
            "brand": car.brand,
            "year": car.year,
            "mileage": car.mileage,
            "location": car.location,
            "transmission": car.transmission,
            "plate_type": car.plate_type,
            "rear_camera": car.rear_camera,
            "sun_roof": car.sun_roof,
            "auto_retract_mirror": car.auto_retract_mirror,
            "electric_parking_brake": car.electric_parking_brake,
            "map_navigator": car.map_navigator,
            "vehicle_stability_control": car.vehicle_stability_control,
            "keyless_push_start": car.keyless_push_start,
            "sports_mode": car.sports_mode,
            "camera_360_view": car.camera_360_view,
            "power_sliding_door": car.power_sliding_door,
            "auto_cruise_control": car.auto_cruise_control,
            "price": car.price,
            "instalment": car.instalment,
            "image_url": car.image_url,
        }
        return JsonResponse(car_data)
    except Car.DoesNotExist:
        return JsonResponse({"error": "Car not found"}, status=404)
    
@login_required
def car_list(request):
    user_profile = UserProfile.objects.get(user=request.user)
    if user_profile.role == 'SEL': 
        cars = Car.objects.filter(seller=request.user)
    else:
        cars = Car.objects.all()
    form = CarFilterForm(request.GET)
    user_wishlist = Wishlist.objects.filter(user=request.user).values_list('id', flat=True)

    if form.is_valid():
        car_name = form.cleaned_data.get('car_name')
        brand = form.cleaned_data.get('brand')
        year = form.cleaned_data.get('year')
        mileage = form.cleaned_data.get('mileage')
        location = form.cleaned_data.get('location')
        transmission = form.cleaned_data.get('transmission')
        plate_type = form.cleaned_data.get('plate_type')

        if car_name:
            cars = cars.filter(car_name__icontains=car_name)
        if brand:
            cars = cars.filter(brand__icontains=brand)
        if year:
            cars = cars.filter(year=year)
        if mileage:
            cars = cars.filter(mileage=mileage)
        if location:
            cars = cars.filter(location__icontains=location)
        if transmission:
            cars = cars.filter(transmission=transmission)
        if plate_type:
            cars = cars.filter(plate_type=plate_type)

        if form.cleaned_data.get('rear_camera'):
            cars = cars.filter(rear_camera=True)
        if form.cleaned_data.get('sun_roof'):
            cars = cars.filter(sun_roof=True)
        if form.cleaned_data.get('auto_retract_mirror'):
            cars = cars.filter(auto_retract_mirror=True)
        if form.cleaned_data.get('electric_parking_brake'):
            cars = cars.filter(electric_parking_brake=True)
        if form.cleaned_data.get('map_navigator'):
            cars = cars.filter(map_navigator=True)
        if form.cleaned_data.get('vehicle_stability_control'):
            cars = cars.filter(vehicle_stability_control=True)
        if form.cleaned_data.get('keyless_push_start'):
            cars = cars.filter(keyless_push_start=True)
        if form.cleaned_data.get('sports_mode'):
            cars = cars.filter(sports_mode=True)
        if form.cleaned_data.get('camera_360_view'):
            cars = cars.filter(camera_360_view=True)
        if form.cleaned_data.get('power_sliding_door'):
            cars = cars.filter(power_sliding_door=True)
        if form.cleaned_data.get('auto_cruise_control'):
            cars = cars.filter(auto_cruise_control=True)

        price_min = form.cleaned_data.get('price_min')
        price_max = form.cleaned_data.get('price_max')
        instalment_min = form.cleaned_data.get('instalment_min')
        instalment_max = form.cleaned_data.get('instalment_max')

        if price_min is not None:
            cars = cars.filter(price__gte=price_min)
        if price_max is not None:
            cars = cars.filter(price__lte=price_max)
        if instalment_min is not None:
            cars = cars.filter(instalment__gte=instalment_min)
        if instalment_max is not None:
            cars = cars.filter(instalment__lte=instalment_max)

    context = {
        'cars': cars,
        'form': form,
        'is_seller': user_profile.role == 'SEL',
        'is_buyer': user_profile.role == 'BUY',
        'is_admin': user_profile.role == 'ADM',
        'user_wishlist': user_wishlist,
    }
    return render(request, 'car_list.html', context)

@login_required
def view_details(request, car_id):
    car = get_object_or_404(Car, id=car_id)
    
    features = [
        ('Rear Camera', car.rear_camera),
        ('Sun Roof', car.sun_roof),
        ('Auto Retract Mirror', car.auto_retract_mirror),
        ('Electric Parking Brake', car.electric_parking_brake),
        ('Map Navigator', car.map_navigator),
        ('Vehicle Stability Control', car.vehicle_stability_control),
        ('Keyless Push Start', car.keyless_push_start),
        ('Sports Mode', car.sports_mode),
        ('Camera 360 View', car.camera_360_view),
        ('Power Sliding Door', car.power_sliding_door),
        ('Auto Cruise Control', car.auto_cruise_control)
    ]

    context = {
        'car': car,
        'features': features,
    }
    return render(request, 'detail.html', context)

@login_required
def delete_car(request, car_id):
    car = get_object_or_404(Car, id=car_id)
    
    user_profile = get_object_or_404(UserProfile, user=request.user)
    if user_profile.role == 'SEL' and car.seller == request.user:
        car.delete()
        return redirect('product_catalog:mobil_saya')
    elif user_profile.role == 'ADM':
        car.delete()
        return redirect('product_catalog:car_list')
    else:
        return redirect('authentication:login')

@csrf_exempt
def create_car_flutter(request):
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Only POST method is allowed'}, status=405)
    
    try:
        data = json.loads(request.body)
        username = data['username']  # Expect username to be sent in the request body
        seller = User.objects.get(username=username)  # Get the user object using the username
        
        car = Car(
            seller=seller,
            car_name=data['car_name'],
            brand=data['brand'],
            year=data['year'],
            mileage=data['mileage'],
            location=data['location'],
            transmission=data['transmission'],
            plate_type=data['plate_type'],
            rear_camera=data.get('rear_camera', False),
            sun_roof=data.get('sun_roof', False),
            auto_retract_mirror=data.get('auto_retract_mirror', False),
            electric_parking_brake=data.get('electric_parking_brake', False),
            map_navigator=data.get('map_navigator', False),
            vehicle_stability_control=data.get('vehicle_stability_control', False),
            keyless_push_start=data.get('keyless_push_start', False),
            sports_mode=data.get('sports_mode', False),
            camera_360_view=data.get('camera_360_view', False),
            power_sliding_door=data.get('power_sliding_door', False),
            auto_cruise_control=data.get('auto_cruise_control', False),
            price=data['price'],
            instalment=data['instalment'],
            image_url=data['image_url']
        )
        car.save()
        return JsonResponse({'status': 'success', 'message': 'Car created successfully'}, status=201)
    except User.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'User not found'}, status=404)
    except KeyError as e:
        return JsonResponse({'status': 'error', 'message': f'Missing field in data: {str(e)}'}, status=400)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': f'An error occurred: {str(e)}'}, status=500)
    
@login_required
def create_car(request):
    user_profile = UserProfile.objects.get(user=request.user)
    car_id = uuid.uuid4()

    if user_profile.role != 'SEL':
        return redirect('authentication:login')
    
    if not user_profile.is_verified:
        messages.error(request, "Ask admin for verification")
        return redirect('product_catalog:mobil_saya')

    if request.method == 'POST':
        form = CarForm(request.POST)
        if form.is_valid():
            car = form.save(commit=False)
            car.seller = request.user
            car.save()
            return redirect('product_catalog:mobil_saya')
        else:
            print(form.errors)

    else:
        form = CarForm()

    context = {
        'form': form,
        'car_id': car_id
    }
    return render(request, 'create_car.html', context)
