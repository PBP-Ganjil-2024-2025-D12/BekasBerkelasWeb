from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from authentication.models import UserProfile, UserRole
from user_dashboard.models import SellerProfile, BuyerProfile, AdminProfile
from django.contrib.messages import get_messages
import json

class DashboardTests(TestCase):
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
        self.admin_extended = AdminProfile.objects.create(
            user_profile=self.admin_profile
        )

        self.login_url = '/auth/login'
        self.dashboard_url = '/dashboard'
        self.biodata_url = reverse('dashboard:biodata')
        self.change_password_url = reverse('dashboard:change_password')
        self.update_profile_url = reverse('dashboard:update_profile')
        self.upload_picture_url = reverse('dashboard:upload_profile_picture')
        self.rating_list_url = reverse('dashboard:rating_list')
        self.verifikasi_url = reverse('dashboard:verifikasi_penjual')
        self.get_user_url = reverse('dashboard:get_user')

    def test_biodata_access(self):
        response = self.client.get(self.biodata_url)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith(self.login_url))

        self.client.login(username='testbuyer', password='testpass123')
        response = self.client.get(self.biodata_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'biodata.html')

        self.client.login(username='testseller', password='testpass123')
        response = self.client.get(self.biodata_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'biodata.html')

        self.client.login(username='testadmin', password='testpass123')
        response = self.client.get(self.biodata_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'biodata.html')

    def test_profile_picture_upload(self):
        response = self.client.post(self.upload_picture_url)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith(self.login_url))

        self.client.login(username='testbuyer', password='testpass123')
        response = self.client.post(self.upload_picture_url, {
            'profile_picture_url': 'https://example.com/pic.jpg',
            'profile_picture_id': 'test123'
        })
        self.assertRedirects(response, self.biodata_url)
        updated_profile = UserProfile.objects.get(user=self.buyer_user)
        self.assertEqual(updated_profile.profile_picture, 'https://example.com/pic.jpg')
        self.assertEqual(updated_profile.profile_picture_id, 'test123')

    def test_update_profile_validation(self):
        self.client.login(username='testbuyer', password='testpass123')

        response = self.client.post(self.update_profile_url, {
            'no_telp': '081234567899'
        })
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data['status'], 'success')
        self.assertEqual(data['data'], '081234567899')

    def test_change_password_validation(self):
        self.client.login(username='testbuyer', password='testpass123')

        response = self.client.post(self.change_password_url, {
            'old_password': 'wrongpass',
            'new_password1': 'newpass123',
            'new_password2': 'newpass123'
        })
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'change_password.html')
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any('error' in message.message.lower() for message in messages))

    def test_verifikasi_penjual_invalid(self):
        self.client.login(username='testadmin', password='testpass123')
        
        response = self.client.post(self.verifikasi_url, {
            'idUser': 9999
        })
        self.assertRedirects(response, self.verifikasi_url)
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any('gagal' in message.message.lower() for message in messages))

    def test_get_user_formats(self):
        self.client.login(username='testadmin', password='testpass123')

        self.seller_profile.is_verified = True
        self.seller_profile.save()

        response = self.client.post(
            self.get_user_url,
            json.dumps({'id': self.seller_profile.id}),
            content_type='application/json'
        )
        data = json.loads(response.content)
        self.assertEqual(data['status'], 'Sudah Verifikasi')

    def test_rating_list(self):
        response = self.client.get(self.rating_list_url)
        expected_login_url = f'{self.login_url}?next={self.rating_list_url}'
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, expected_login_url)

        self.client.login(username='testbuyer', password='testpass123')
        response = self.client.get(self.rating_list_url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, self.dashboard_url)

        self.client.login(username='testseller', password='testpass123')
        response = self.client.get(self.rating_list_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'seller_rating_list.html')