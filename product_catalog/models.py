from django.db import models
from django.contrib.auth.models import User
from user_dashboard.models import SellerProfile
import uuid

class Car(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    CAR_TRANSMISSION_CHOICES = [
        ('Manual', 'Manual'),
        ('Automatic', 'Automatic'),
    ]
    
    PLATE_TYPE_CHOICES = [
        ('Even', 'Even'),
        ('Odd', 'Odd'),
    ]
    
    seller = models.ForeignKey(User, on_delete=models.CASCADE)
    car_name = models.CharField(max_length=100)
    brand = models.CharField(max_length=100)
    year = models.PositiveIntegerField()
    mileage = models.PositiveIntegerField() 
    location = models.CharField(max_length=100)
    transmission = models.CharField(max_length=10, choices=CAR_TRANSMISSION_CHOICES)
    plate_type = models.CharField(max_length=10, choices=PLATE_TYPE_CHOICES)
    rear_camera = models.BooleanField(default=False)
    sun_roof = models.BooleanField(default=False)
    auto_retract_mirror = models.BooleanField(default=False)
    electric_parking_brake = models.BooleanField(default=False)
    map_navigator = models.BooleanField(default=False)
    vehicle_stability_control = models.BooleanField(default=False)
    keyless_push_start = models.BooleanField(default=False)
    sports_mode = models.BooleanField(default=False)
    camera_360_view = models.BooleanField(default=False)
    power_sliding_door = models.BooleanField(default=False)
    auto_cruise_control = models.BooleanField(default=False)
    price = models.DecimalField(max_digits=15, decimal_places=2)
    instalment = models.DecimalField(max_digits=15, decimal_places=2)
    image_url = models.URLField(max_length=200, blank=True)


