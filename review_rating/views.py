from django.http import HttpResponse, JsonResponse
import json
from django.forms.models import model_to_dict
from django.contrib.auth.models import User
from django.db.models import Avg
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from review_rating.models import ReviewRating
from user_dashboard.models import UserProfile, SellerProfile, BuyerProfile, AdminProfile
from product_catalog.models import Car
from django.shortcuts import render, redirect
from django.core import serializers
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.http import Http404
import json
import json

@login_required(login_url='/auth/login')
def show_reviews(request, username):
    seller = get_object_or_404(SellerProfile, user_profile=UserProfile.objects.get(user=User.objects.get(username=username)))
    reviews = ReviewRating.objects.filter(reviewee=seller)
    context = {
        'seller': seller,
        'reviews': reviews
    }
    return render(request, "seller_reviews.html", context)

@login_required(login_url='/auth/login')
def show_profile(request, username):
    try:
        user = get_object_or_404(User, username=username)
        user_profile = user.userprofile
        
        context = {
            'profile_user': user,
            'user_profile': user_profile
        }
        
        if user_profile.role == 'SEL':
            seller = get_object_or_404(SellerProfile, user_profile=user_profile)
            context.update({
                'seller': seller,
                'cars': Car.objects.filter(seller=user),
                'reviews': ReviewRating.objects.filter(reviewee=seller)
            })
            template_name = "seller_profile.html"
            
        else:
            template_name = "buyer_admin_profile.html"
            
        return render(request, template_name, context)
        
    except User.DoesNotExist:
        raise Http404("User profile not found")

@csrf_exempt
@require_POST
@login_required(login_url='/auth/login')
def add_review(request, username):
    try:
        user_profile = UserProfile.objects.get(user=request.user)

        if user_profile.role != 'BUY':
            return JsonResponse({'error': 'You must be a buyer to leave a review.'}, status=403)
        
        review = request.POST.get("review")
        rating = request.POST.get("rating")
        reviewee_username = username

        try:
            rating = int(rating)
            if not (1 <= rating <= 5):
                return JsonResponse({'error': 'Rating must be between 1 and 5'}, status=400)
        except ValueError:
            return JsonResponse({'error': 'Invalid rating format'}, status=400)

        reviewer = BuyerProfile.objects.get(user_profile=user_profile)

        if not all([review, rating, reviewee_username]):
            return JsonResponse({'error': 'All fields are required'}, status=400)

        try:
            reviewee = SellerProfile.objects.get(user_profile__user__username=reviewee_username)
        except SellerProfile.DoesNotExist:
            return JsonResponse({'error': 'Invalid reviewee'}, status=400)

        new_review_rating = ReviewRating(
            review=review,
            rating=rating,
            reviewer=reviewer,
            reviewee=reviewee
        )
        new_review_rating.save()

        average_rating = ReviewRating.objects.filter(reviewee=reviewee).aggregate(Avg('rating'))['rating__avg']

        reviewee.rating = average_rating
        reviewee.save()

        return JsonResponse({'message': 'Review created successfully'}, status=201)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def show_json(request, username):
    seller = get_object_or_404(SellerProfile, user_profile=UserProfile.objects.get(user=User.objects.get(username=username)))
    
    reviews = ReviewRating.objects.filter(reviewee=seller)
    
    data = []
    
    for review in reviews:
        can_delete = False
        if not request.user.is_anonymous:
            can_delete = (
                request.user == review.reviewer.user_profile.user or 
                request.user.userprofile.role == 'ADM'
            )
        data.append({
            'fields': {
                'rating': review.rating,
                'review': review.review,
                'id': str(review.id),
                'can_delete': can_delete,
                'reviewer': {
                    'user_profile': {
                        'profile_picture': str(review.reviewer.user_profile.profile_picture),
                        'name': review.reviewer.user_profile.user.username
                    }
                }
            }
        })
    
    return JsonResponse(data, safe=False)

@csrf_exempt
@require_POST
def delete_review(request, review_id):
    if request.user.is_authenticated:
        try:
            review = ReviewRating.objects.get(id=review_id)
            reviewee = review.reviewee
            review.delete()
            average_rating = ReviewRating.objects.filter(reviewee=reviewee).aggregate(Avg('rating'))['rating__avg']
            reviewee.rating = average_rating
            reviewee.save()
            return JsonResponse({"status": "success"}, status=200)
        except ReviewRating.DoesNotExist:
            return JsonResponse({"error": "Review not found"}, status=404)
    else:
        return JsonResponse({"error": "Not authenticated"}, status=401)
    
def show_user_json(request, username):
    user_profile = get_object_or_404(UserProfile, user__username=username)

    if user_profile.role == 'SEL':
        seller_profile = SellerProfile.objects.get(user_profile=user_profile)
        seller_profile_data = model_to_dict(seller_profile)
        seller_profile_data['user_profile'] = model_to_dict(user_profile)
        return JsonResponse(seller_profile_data, safe=False)

    elif user_profile.role == 'BUY':
        buyer_profile = BuyerProfile.objects.get(user_profile=user_profile)
        buyer_profile_data = model_to_dict(buyer_profile)
        buyer_profile_data['user_profile'] = model_to_dict(user_profile) 
        return JsonResponse(buyer_profile_data, safe=False)

    elif user_profile.role == 'ADM':
        admin_profile = AdminProfile.objects.get(user_profile=user_profile)
        admin_profile_data = model_to_dict(admin_profile)
        admin_profile_data['user_profile'] = model_to_dict(user_profile)
        return JsonResponse(admin_profile_data, safe=False)

    return JsonResponse({"error": "Role not found"}, status=400)

@csrf_exempt
@require_POST
def add_review_flutter(request, username):
    if request.method == 'POST':
        try:
            review = request.POST.get('review')
            rating = request.POST.get('rating')
            reviewer_username = request.POST.get('reviewer_username')
            reviewee_username = username

            reviewer = BuyerProfile.objects.get(user_profile__user__username=reviewer_username)
            reviewee = SellerProfile.objects.get(user_profile__user__username=reviewee_username)

            new_review_rating = ReviewRating(
                review=review,
                rating=rating,
                reviewer=reviewer,
                reviewee=reviewee
            )
            new_review_rating.save()

            average_rating = ReviewRating.objects.filter(reviewee=reviewee).aggregate(Avg('rating'))['rating__avg']

            reviewee.rating = average_rating
            reviewee.save()

            return JsonResponse({'message': 'Review created successfully'}, status=201)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    else:
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
@csrf_exempt
@require_POST
def delete_review_flutter(request, review_id):
    try:
        review = ReviewRating.objects.get(id=review_id)
        reviewee = review.reviewee
        review.delete()
        average_rating = ReviewRating.objects.filter(reviewee=reviewee).aggregate(Avg('rating'))['rating__avg'] or 0
        reviewee.rating = average_rating
        reviewee.save()
        return JsonResponse({"status": "success"}, status=200)
    except ReviewRating.DoesNotExist:
        return JsonResponse({"error": "Review not found"}, status=404)