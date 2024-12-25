from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from wishlist.models import Wishlist
from authentication.models import UserProfile, UserRole
from user_dashboard.models import SellerProfile, BuyerProfile
from product_catalog.models import Car
import uuid
import json

class WishlistTests(TestCase):
    def setUp(self):
        self.client = Client()
        
        self.buyer_user = User.objects.create_user(
            username='testbuyer',
            password='testpass123'
        )
        
        self.buyer_profile = UserProfile.objects.create(
            user=self.buyer_user,
            name='Test Buyer',
            email='buyer@test.com',
            no_telp='081234567890',
            role=UserRole.BUYER
        )
        
        self.buyer_extended = BuyerProfile.objects.create(
            user_profile=self.buyer_profile
        )

        self.seller_user = User.objects.create_user(
            username='testseller',
            password='testpass123'
        )
        
        self.seller_profile = UserProfile.objects.create(
            user=self.seller_user,
            name='Test Seller',
            email='seller@test.com',
            no_telp='081234567891',
            role=UserRole.SELLER
        )
        
        self.seller_extended = SellerProfile.objects.create(
            user_profile=self.seller_profile,
            total_sales=0,
            rating=0.0
        )

        self.car = Car.objects.create(
            id=uuid.uuid4(),
            seller=self.seller_user,
            seller_buat_dashboard=self.seller_extended,
            car_name="Test Car",
            brand="Toyota",
            year=2020,
            mileage=5000,
            location="Jakarta",
            transmission="Manual",
            plate_type="Odd",
            rear_camera=True,
            price=25000000.00,
            instalment=2000000.00,
            image_url="http://example.com/image.jpg"
        )

        self.client.login(username='testbuyer', password='testpass123')

    def test_add_to_wishlist_item(self):
        response = self.client.post(reverse('wishlist:add_to_wishlist', args=[self.car.id]))
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.content)
        self.assertEqual(data['status'], 'success')
        self.assertEqual(data['action'], 'added')
        
        wishlist_item = Wishlist.objects.get(user=self.buyer_user, car=self.car)
        self.assertEqual(wishlist_item.priority, 1)
        
        response = self.client.post(reverse('wishlist:add_to_wishlist', args=[self.car.id]))
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.content)
        self.assertEqual(data['status'], 'success')
        self.assertEqual(data['action'], 'removed')

        self.assertEqual(Wishlist.objects.filter(user=self.buyer_user, car=self.car).count(), 0)

    def test_view_wishlist(self):
        Wishlist.objects.create(
            user=self.buyer_user,
            car=self.car,
            priority=1
        )
        
        response = self.client.get(reverse('wishlist:show_wishlist'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'wishlist.html')
        self.assertContains(response, "Test Car")
        self.assertContains(response, self.car.brand)
        
        response = self.client.get(f"{reverse('wishlist:show_wishlist')}?priority=1")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'wishlist.html')

    def test_edit_wishlist_item(self):
        wishlist = Wishlist.objects.create(
            user=self.buyer_user,
            car=self.car,
            priority=1
        )
        
        response = self.client.post(reverse('wishlist:edit_wishlist', args=[wishlist.id]), {'priority': 'Tinggi'})
        self.assertEqual(response.status_code, 302)
        
        wishlist.refresh_from_db()
        self.assertEqual(wishlist.priority, 3)

    def test_delete_wishlist_item(self):
        wishlist = Wishlist.objects.create(
            user=self.buyer_user,
            car=self.car,
            priority=1
        )
        
        response = self.client.post(reverse('wishlist:remove_from_wishlist', args=[wishlist.id]))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Wishlist.objects.filter(id=wishlist.id).count(), 0)
