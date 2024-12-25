from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from authentication.models import UserProfile, UserRole
from user_dashboard.models import SellerProfile
from product_catalog.models import Car
from product_catalog.forms import CarForm
from decimal import Decimal
import uuid
import json

class ProductCatalogTests(TestCase):
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

        self.seller_user = User.objects.create_user(
            username='testseller',
            password='testpass123'
        )
        self.seller_profile = UserProfile.objects.create(
            user=self.seller_user,
            name='Test Seller',
            email='seller@test.com',
            no_telp='081234567891',
            role=UserRole.SELLER,
            is_verified=True
        )
        self.seller_extended = SellerProfile.objects.create(
            user_profile=self.seller_profile
        )

        self.admin_user = User.objects.create_user(
            username='testadmin',
            password='testpass123'
        )
        self.admin_profile = UserProfile.objects.create(
            user=self.admin_user,
            name='Test Admin',
            email='admin@test.com',
            no_telp='081234567892',
            role=UserRole.ADMIN
        )

        self.test_car = Car.objects.create(
            seller=self.seller_user,
            seller_buat_dashboard=self.seller_extended,
            car_name='Test Car',
            brand='Test Brand',
            year=2020,
            mileage=50000,
            location='Test Location',
            transmission='Manual',
            plate_type='Even',
            price=Decimal('100000.00'),
            instalment=Decimal('2000.00')
        )

        self.car_data = {
            'car_name': 'New Test Car',
            'brand': 'New Brand',
            'year': 2021,
            'mileage': 30000,
            'location': 'New Location',
            'transmission': 'Automatic',
            'plate_type': 'Odd',
            'price': '150000.00',
            'instalment': '3000.00',
            'rear_camera': True,
            'sun_roof': True
        }

    def test_car_list_view(self):
        response = self.client.get(reverse('product_catalog:car_list'))
        self.assertEqual(response.status_code, 302)
        
        self.client.login(username='testbuyer', password='testpass123')
        response = self.client.get(reverse('product_catalog:car_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'car_list.html')
        self.assertTrue('cars' in response.context)
        self.assertTrue('form' in response.context)

    def test_mobil_saya_view(self):
        self.client.login(username='testbuyer', password='testpass123')
        response = self.client.get(reverse('product_catalog:mobil_saya'))
        self.assertRedirects(response, reverse('product_catalog:car_list'))

        self.client.login(username='testseller', password='testpass123')
        response = self.client.get(reverse('product_catalog:mobil_saya'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'mobil_saya.html')

    def test_create_car(self):
        self.client.login(username='testseller', password='testpass123')
        response = self.client.get(reverse('product_catalog:create_car'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'create_car.html')

        response = self.client.post(reverse('product_catalog:create_car'), self.car_data)
        self.assertRedirects(response, reverse('product_catalog:mobil_saya'))
        self.assertTrue(Car.objects.filter(car_name='New Test Car').exists())

    def test_delete_car(self):
        car = Car.objects.create(
            seller=self.seller_user,
            seller_buat_dashboard=self.seller_extended,
            car_name='Car to Delete',
            brand='Test Brand',
            year=2020,
            mileage=50000,
            location='Test Location',
            transmission='Manual',
            plate_type='Even',
            price=Decimal('100000.00'),
            instalment=Decimal('2000.00')
        )

        self.client.login(username='testbuyer', password='testpass123')
        response = self.client.post(reverse('product_catalog:delete_car', args=[car.id]))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Car.objects.filter(id=car.id).exists())

        self.client.login(username='testseller', password='testpass123')
        response = self.client.post(reverse('product_catalog:delete_car', args=[car.id]))
        self.assertRedirects(response, reverse('product_catalog:mobil_saya'))
        self.assertFalse(Car.objects.filter(id=car.id).exists())

    def test_contact_seller(self):
        self.client.login(username='testbuyer', password='testpass123')
        response = self.client.post(reverse('product_catalog:contact_seller', args=[self.test_car.id]))
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data['email'], self.seller_profile.email)
        self.assertEqual(data['phone'], self.seller_profile.no_telp)

    def test_view_details(self):
        self.client.login(username='testbuyer', password='testpass123')
        response = self.client.get(reverse('product_catalog:view_details', args=[self.test_car.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'detail.html')
        self.assertEqual(response.context['car'], self.test_car)

    def test_car_filter(self):
        self.client.login(username='testbuyer', password='testpass123')
        
        filter_params = {
            'car_name': 'Test',
            'brand': 'Brand',
            'year': 2020,
            'mileage': 50000,
            'location': 'Location',
            'transmission': 'Manual',
            'plate_type': 'Even',
            'price_min': '50000',
            'price_max': '200000',
            'rear_camera': True
        }
        
        response = self.client.get(reverse('product_catalog:car_list'), filter_params)
        self.assertEqual(response.status_code, 200)
        self.assertTrue('cars' in response.context)

    def test_unverified_seller(self):
        unverified_seller = User.objects.create_user(
            username='unverifiedseller',
            password='testpass123'
        )
        unverified_profile = UserProfile.objects.create(
            user=unverified_seller,
            name='Unverified Seller',
            email='unverified@test.com',
            role=UserRole.SELLER,
            is_verified=False
        )
        seller_extended = SellerProfile.objects.create(
            user_profile=unverified_profile
        )

        self.client.login(username='unverifiedseller', password='testpass123')
        response = self.client.get(reverse('product_catalog:create_car'))
        self.assertRedirects(response, reverse('product_catalog:mobil_saya'))

    def test_invalid_car_creation(self):
        self.client.login(username='testseller', password='testpass123')
        invalid_data = self.car_data.copy()
        invalid_data['year'] = 'invalid'
        
        response = self.client.post(reverse('product_catalog:create_car'), invalid_data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'create_car.html')
        self.assertFalse(Car.objects.filter(car_name='New Test Car').exists())

    def test_car_model_str(self):
        car = Car.objects.create(
            seller=self.seller_user,
            seller_buat_dashboard=self.seller_extended,
            car_name='Test Car String',
            brand='Test Brand',
            year=2020,
            mileage=50000,
            location='Test Location',
            transmission='Manual',
            plate_type='Even',
            price=Decimal('100000.00'),
            instalment=Decimal('2000.00')
        )
        self.assertEqual(str(car.car_name), 'Test Car String')