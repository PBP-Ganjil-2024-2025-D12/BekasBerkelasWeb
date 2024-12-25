from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseRedirect
from django.urls import reverse
from .models import Wishlist
from product_catalog.models import Car
from django.views.decorators.http import require_http_methods
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.core import serializers
import json
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

@require_POST
@login_required(login_url='/auth/login')
def add_to_wishlist(request, car_id):
    try:
        car = get_object_or_404(Car, id=car_id)
        user = request.user
            
        try:
            wishlist_item, created = Wishlist.objects.get_or_create(user=user, car=car, defaults={'priority':'1'})
            
            if created:
                return JsonResponse({'status': 'success','action': 'added','message': 'Menambahkan ke wishlist'})
            else:
                wishlist_item.delete()
                return JsonResponse({'status': 'success','action': 'removed','message': 'Menghapus dari wishlist'})
                
        except Exception as e:
            return JsonResponse({'status': 'error','message': f'Error with wishlist operation: {str(e)}'}, status=500)
            
    except Exception as e:
        return JsonResponse({'status': 'error','message': str(e)}, status=500)

@login_required(login_url='/auth/login')
def show_wishlist(request):
    priority_filter = request.GET.get('priority', None)
    wishlists = Wishlist.objects.filter(user=request.user)
    
    if priority_filter:
        wishlists = wishlists.filter(priority=priority_filter)
        
    context = {'wishlists': wishlists, 'selected_priority': priority_filter, 'priority_choices': Wishlist.PRIORITY_CHOICES}
    return render(request, 'wishlist.html', context)

@csrf_exempt
@login_required(login_url='/auth/login')
def edit_wishlist(request, wishlist_id):
    wishlist = get_object_or_404(Wishlist, id=wishlist_id, user=request.user)
    
    if request.method == 'POST':
        priority_map = {'Rendah': 1, 'Sedang': 2, 'Tinggi': 3}
        new_priority = request.POST.get('priority')
        wishlist.priority = priority_map.get(new_priority, 1)
        wishlist.save()
        return redirect('wishlist:show_wishlist')
    
    return render(request, 'edit_wishlist.html', {'wishlist': wishlist})

@csrf_exempt
@require_POST
@login_required(login_url='/auth/login')
def remove_from_wishlist(request, wishlist_id):
    wishlist = get_object_or_404(Wishlist, id=wishlist_id, user=request.user)
    wishlist.delete()
    return HttpResponseRedirect(reverse('wishlist:show_wishlist'))

def show_json(request):
    wishlists = Wishlist.objects.filter(user=request.user)
    data = []
    for wishlist in wishlists:
        car = wishlist.car
        data.append({
            'id': str(wishlist.pk),
            'image_url': car.image_url,
            'car_name': car.car_name,
            'price': car.price,
            'brand': car.brand,
            'year': car.year,
            'mileage': car.mileage,
            'priority': wishlist.priority,
        })
    return JsonResponse(data, safe=False)

def get_wishlist_item(request, wishlist_id):
    wishlist = get_object_or_404(Wishlist, id=wishlist_id, user=request.user)
    data = {
        'id': str(wishlist.id),
        'image_url': wishlist.car.image_url,
        'car_name': wishlist.car.car_name,
        'price': wishlist.car.price,
        'brand': wishlist.car.brand,
        'year': wishlist.car.year,
        'mileage': wishlist.car.mileage,
        'priority': wishlist.priority,
    }
    return JsonResponse(data, safe=False)

@csrf_exempt
def get_wishlist_car_ids(request):
    try:
        wishlist_items = Wishlist.objects.filter(user=request.user)
        car_ids = [str(item.car.id) for item in wishlist_items]
        return JsonResponse({'car_ids': car_ids})
    except Wishlist.DoesNotExist:
        return JsonResponse({'car_ids': []})

@csrf_exempt
@require_POST
def add_wishlist_flutter(request, car_id):
    try:
        car = get_object_or_404(Car, id=car_id)
        user = request.user
        wishlist_item, created = Wishlist.objects.get_or_create(user=user, car=car, defaults={'priority':'1'})
        if created:
            return JsonResponse({'status': 'success', 'action': 'added', 'message': 'Added to wishlist'})
        else:
            wishlist_item.delete()
            return JsonResponse({'status': 'success', 'action': 'removed', 'message': 'Removed from wishlist'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    

@csrf_exempt
@require_POST
def edit_wishlist_flutter(request, wishlist_id):
    try:
        wishlist = get_object_or_404(Wishlist, id=wishlist_id, user=request.user)
        new_priority = request.POST.get('priority')
        wishlist.priority = new_priority
        wishlist.save()
        return JsonResponse({'status': 'success', 'message': 'Priority updated successfully.'}, status=200  )
    except ValueError as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    except Wishlist.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Wishlist not found.'}, status=404)

@csrf_exempt
@require_POST
def remove_wishlist_flutter(request, wishlist_id):
    try:
        wishlist = get_object_or_404(Wishlist, id=wishlist_id, user=request.user)
        wishlist.delete()
        return JsonResponse({'status': 'success'})
    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=500)
    except Wishlist.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Wishlist entry not found.'}, status=404)