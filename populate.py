import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bekas_berkelas.settings')
django.setup()

from django.contrib.auth.models import User
from authentication.models import UserProfile, UserRole 
from user_dashboard.models import SellerProfile

names = [
    "Ramy", "Ultramy", "UltraRamy", "Naufal", "Muhammad",
    "Ramadhan", "Steven", "Setiawan", "Wida", "Putri",
    "Deanita", "Chip", "Skylar", "Case", "Shino",
    "Nadia", "Rahmadina", "Aristawati", "Okin", "Niko"
]
password = 'BekasBerkelas'
admin_username = 'admin'
admin_email = 'admin@example.com'
admin_password = 'ab53a3cad15f9fe403ca9afc2b8fcfcf50adb1513d9ba921fe280eb581279e363e0dcc32'

admin_user = User.objects.create_superuser(username=admin_username, email=admin_email, password=admin_password)

UserProfile.objects.create(
    user=admin_user,
    name='Administrator',
    email=admin_email,
    no_telp='1234567890',
    role=UserRole.ADMIN,
    profile_picture=None,
    profile_picture_id=None,
    is_verified=True
)

print("Administrator profile created.")

for name in names:
    username = name.lower()  
    email = f"{username}@gmail.com"

    user = User.objects.create_user(username=username, email=email, password=password)

    userprofile = UserProfile.objects.create(
        user=user,
        name=name,
        email=email,
        no_telp='1234567890',
        role=UserRole.SELLER,  
        profile_picture=None,
        profile_picture_id=None,
        is_verified=True 
    )

    SellerProfile.objects.create(user_profile = userprofile, total_sales=0, rating=0)

print("Created user profiles with all verified and role as Seller.")
