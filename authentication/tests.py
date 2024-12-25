from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.conf import settings
from authentication.models import UserProfile, UserRole
from django.contrib.messages import get_messages

class AuthenticationTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.register_url = reverse('authentication:register')
        self.login_url = reverse('authentication:login')
        self.logout_url = reverse('authentication:logout')
        self.main_url = reverse('main:main')
        self.next_url = reverse('forum:show_forum')
        
        self.user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password1': 'testpass123',
            'password2': 'testpass123',
            'name': 'Test User',
            'no_telp': '081234567890',
            'role': UserRole.BUYER
        }
        
        self.seller_data = {
            'username': 'testseller',
            'email': 'seller@example.com',
            'password1': 'testpass123',
            'password2': 'testpass123',
            'name': 'Test Seller',
            'no_telp': '081234567891',
            'role': UserRole.SELLER
        }
        
        self.admin_data = {
            'username': 'testadmin',
            'email': 'admin@example.com',
            'password1': settings.ADMIN_ACCOUNT_SECRET_TOKEN,
            'password2': settings.ADMIN_ACCOUNT_SECRET_TOKEN,
            'name': 'Test Admin',
            'no_telp': '081234567892',
            'role': UserRole.ADMIN
        }

    def test_register_page_load(self):
        response = self.client.get(self.register_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'register.html')

    def test_register_buyer_success(self):
        response = self.client.post(self.register_url, self.user_data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, self.login_url)
        
        user = User.objects.get(username='testuser')
        profile = UserProfile.objects.get(user=user)
        self.assertEqual(profile.role, UserRole.BUYER)
        self.assertEqual(profile.email, self.user_data['email'])
        self.assertEqual(profile.no_telp, self.user_data['no_telp'])
        self.assertFalse(profile.is_verified)

    def test_register_seller_success(self):
        response = self.client.post(self.register_url, self.seller_data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, self.login_url)
        
        user = User.objects.get(username='testseller')
        profile = UserProfile.objects.get(user=user)
        self.assertEqual(profile.role, UserRole.SELLER)
        self.assertFalse(profile.is_verified)

    def test_register_admin_success(self):
        response = self.client.post(self.register_url, self.admin_data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, self.login_url)
        
        user = User.objects.get(username='testadmin')
        profile = UserProfile.objects.get(user=user)
        self.assertEqual(profile.role, UserRole.ADMIN)

    def test_register_admin_wrong_token(self):
        invalid_admin_data = self.admin_data.copy()
        invalid_admin_data['password1'] = 'wrongtoken'
        invalid_admin_data['password2'] = 'wrongtoken'
        
        response = self.client.post(self.register_url, invalid_admin_data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, self.register_url)
        
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any(message.message == 'Invalid Admin Credentials' for message in messages))

    def test_register_password_mismatch(self):
        invalid_data = self.user_data.copy()
        invalid_data['password2'] = 'differentpassword'
        
        response = self.client.post(self.register_url, invalid_data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, self.register_url)

    def test_login_page_load(self):
        response = self.client.get(self.login_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'login.html')

    def test_login_success(self):
        self.client.post(self.register_url, self.user_data)
        
        login_data = {
            'username': self.user_data['username'],
            'password': self.user_data['password1']
        }
        response = self.client.post(self.login_url, login_data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, self.main_url)
        self.assertTrue('user_login' in response.cookies)

    def test_login_failure(self):
        login_data = {
            'username': 'nonexistent',
            'password': 'wrongpassword'
        }
        response = self.client.post(self.login_url, login_data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, self.login_url)
        
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any(message.message == 'Invalid username or password' for message in messages))

    def test_login_redirect_next(self):
        self.client.post(self.register_url, self.user_data)
        
        login_data = {
            'username': self.user_data['username'],
            'password': self.user_data['password1']
        }
        response = self.client.post(f'{self.login_url}?next={self.next_url}', login_data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, self.next_url)

    def test_logout_success(self):
        self.client.post(self.register_url, self.user_data)
        response = self.client.post(self.login_url, {
            'username': self.user_data['username'],
            'password': self.user_data['password1']
        })
        
        self.assertTrue('user_login' in response.cookies)
        initial_cookie = self.client.cookies.get('user_login')
        
        response = self.client.get(self.logout_url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, self.main_url)
        
        final_cookie = self.client.cookies.get('user_login')
        self.assertTrue(
            final_cookie is None or
            final_cookie.value == '' or  
            final_cookie.value != initial_cookie.value 
        )

    def test_authenticated_user_cant_access_register(self):
        self.client.post(self.register_url, self.user_data)
        self.client.post(self.login_url, {
            'username': self.user_data['username'],
            'password': self.user_data['password1']
        })
        
        response = self.client.get(self.register_url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, self.main_url)

    def test_authenticated_user_cant_access_login(self):
        self.client.post(self.register_url, self.user_data)
        self.client.post(self.login_url, {
            'username': self.user_data['username'],
            'password': self.user_data['password1']
        })
        
        response = self.client.get(self.login_url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, self.main_url)