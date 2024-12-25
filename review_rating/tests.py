from django.test import TestCase
from django.contrib.auth.models import User
from .models import ReviewRating
from user_dashboard.models import UserProfile, AdminProfile
from user_dashboard.models import SellerProfile, BuyerProfile
from django.urls import reverse

class ReviewRatingTests(TestCase):

    def setUp(self):
        self.seller_user = User.objects.create_user(username='seller', password='pass123')
        self.buyer_user = User.objects.create_user(username='buyer', password='pass123')
        self.admin_user = User.objects.create_user(username='admin', password='pass123')

        self.seller_profile = UserProfile.objects.create(user=self.seller_user, role='SEL')
        self.buyer_profile = UserProfile.objects.create(user=self.buyer_user, role='BUY')
        self.admin_profile = UserProfile.objects.create(user=self.admin_user, role='ADM')

        self.seller_profile = SellerProfile.objects.create(user_profile=self.seller_profile)
        self.buyer_profile = BuyerProfile.objects.create(user_profile=self.buyer_profile)
        self.admin_profile = AdminProfile.objects.create(user_profile=self.admin_profile)

        self.review = ReviewRating.objects.create(
            review="Great car!",
            rating=5,
            reviewer=self.buyer_profile,
            reviewee=self.seller_profile
        )

    def test_show_profile(self):
        self.client.login(username='seller', password='pass123')
        response = self.client.get(reverse('review_rating:show_profile', args=['seller']))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'seller')

    def test_show_profile_not_found(self):
        self.client.login(username='buyer', password='pass123')
        response = self.client.get(reverse('review_rating:show_profile', args=['nonexistent']))
        self.assertEqual(response.status_code, 404)

    def test_add_review_not_a_buyer(self):
        self.client.login(username='admin', password='pass123')
        response = self.client.post(reverse('review_rating:add_review', args=['seller']), {
            'review': 'Not a buyer!',
            'rating': '4',
        })
        self.assertEqual(response.status_code, 403)

    def test_add_review_invalid_rating(self):
        self.client.login(username='buyer', password='pass123')
        response = self.client.post(reverse('review_rating:add_review', args=['seller']), {
            'review': 'Great seller!',
            'rating': '6',
        })
        self.assertEqual(response.status_code, 400)

    def test_review_creation(self):
        review = ReviewRating.objects.get(id=self.review.id)
        self.assertEqual(review.review, "Great car!")
        self.assertEqual(review.rating, 5)
        self.assertEqual(review.reviewer, self.buyer_profile)
        self.assertEqual(review.reviewee, self.seller_profile)

    def test_review_rating_range(self):
        self.assertGreaterEqual(self.review.rating, 1)
        self.assertLessEqual(self.review.rating, 5)