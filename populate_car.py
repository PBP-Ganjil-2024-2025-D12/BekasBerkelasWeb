import os
import django
import csv
import random

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bekas_berkelas.settings')
django.setup()

from django.contrib.auth.models import User
from product_catalog.models import Car 


sellers = User.objects.filter(userprofile__role='SEL')

# Read data from the CSV file
with open('cars.csv', mode='r', encoding='utf-8') as file:
    reader = csv.DictReader(file)
    
    for row in reader:
        car_data = {
            "seller": random.choice(sellers),  # Assign a random seller
            "car_name": row['car name'],  # Adjusted for the CSV header
            "brand": row['brand'],
            "year": int(row['year']),
            "mileage": float(row['mileage (km)']),
            "location": row['location'],
            "transmission": row['transmission'],
            "plate_type": row['plate type'],  # Adjusted for the CSV header
            "rear_camera": bool(int(row['rear camera'])),  # Adjusted for the CSV header
            "sun_roof": bool(int(row['sun roof'])),  # Adjusted for the CSV header
            "auto_retract_mirror": bool(int(row['auto retract mirror'])),  # Adjusted for the CSV header
            "electric_parking_brake": bool(int(row['electric parking brake'])),  # Adjusted for the CSV header
            "map_navigator": bool(int(row['map navigator'])),  # Adjusted for the CSV header
            "vehicle_stability_control": bool(int(row['vehicle stability control'])),  # Adjusted for the CSV header
            "keyless_push_start": bool(int(row['keyless push start'])),  # Adjusted for the CSV header
            "sports_mode": bool(int(row['sports mode'])),  # Adjusted for the CSV header
            "camera_360_view": bool(int(row['360 camera view'])),  # Adjusted for the CSV header
            "power_sliding_door": bool(int(row['power sliding door'])),  # Adjusted for the CSV header
            "auto_cruise_control": bool(int(row['auto cruise control'])),  # Adjusted for the CSV header
            "price": float(row['price (Rp)']),  # Adjusted for the CSV header
            "instalment": float(row['instalment (Rp|Monthly)']),  # Adjusted for the CSV header
            "image_url": row['image_url'],
        }
        Car.objects.create(**car_data)

print("Created car entries successfully.")
