from django.db import models
from authentication.models import UserProfile

# Create your models here.
class SellerProfile(models.Model):
    user_profile = models.OneToOneField(UserProfile, on_delete=models.CASCADE)
    total_sales = models.PositiveIntegerField(default=0)
    rating = models.FloatField(default=0.0)


class BuyerProfile(models.Model):
    user_profile = models.OneToOneField(UserProfile, on_delete=models.CASCADE)

class AdminProfile(models.Model):
    user_profile = models.OneToOneField(UserProfile, on_delete=models.CASCADE)
