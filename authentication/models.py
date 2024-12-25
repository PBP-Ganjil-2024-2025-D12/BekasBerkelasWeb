from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class UserRole(models.TextChoices) :
    ADMIN = 'ADM', 'Admin',
    BUYER = 'BUY', 'Buyer',
    SELLER = 'SEL', 'Seller'

class UserProfile(models.Model) :
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=300)
    email = models.EmailField()
    no_telp = models.CharField(default='-', max_length=12)
    role = models.CharField(default=UserRole.BUYER, choices=UserRole.choices, max_length=3)
    profile_picture = models.URLField(max_length=500, blank=True, null=True)
    profile_picture_id = models.CharField(max_length=300,  blank=True, null=True)
    is_verified = models.BooleanField(default=False)