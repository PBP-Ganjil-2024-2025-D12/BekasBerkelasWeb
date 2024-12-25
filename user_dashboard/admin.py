from django.contrib import admin

# Register your models here.
from authentication.models import UserProfile
from .models import SellerProfile, BuyerProfile
from review_rating.models import ReviewRating

admin.site.register(UserProfile)
admin.site.register(SellerProfile)
admin.site.register(BuyerProfile)
admin.site.register(ReviewRating)