from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from forum.models import Question, Reply, Category
from forum.forms import ForumForm, ReplyForm
from authentication.models import UserProfile, UserRole
from product_catalog.models import Car
from user_dashboard.models import SellerProfile, BuyerProfile, AdminProfile
import uuid

class ForumTests(TestCase):
    def setUp(self):
        self.buyer = User.objects.create_user(
            username='testbuyer',
            password='testpass123',
            email='buyer@example.com'
        )
        self.buyer_profile = UserProfile.objects.create(
            user=self.buyer,
            name='Test Buyer',
            email='buyer@example.com',
            role=UserRole.BUYER,
            no_telp='081234567890'
        )
        
        self.buyer_dashboard_profile = BuyerProfile.objects.create(
            user_profile=self.buyer_profile
        )
        
        self.seller = User.objects.create_user(
            username='testseller',
            password='testpass123',
            email='seller@example.com'
        )
        self.seller_profile = UserProfile.objects.create(
            user=self.seller,
            name='Test Seller',
            email='seller@example.com',
            role=UserRole.SELLER,
            no_telp='081234567891',
            is_verified=True
        )
        
        self.seller_dashboard_profile = SellerProfile.objects.create(
            user_profile=self.seller_profile,
            total_sales=0,
            rating=0.0
        )
        
        self.admin = User.objects.create_user(
            username='testadmin',
            password='testpass123',
            email='admin@example.com'
        )
        self.admin_profile = UserProfile.objects.create(
            user=self.admin,
            name='Test Admin',
            email='admin@example.com',
            role=UserRole.ADMIN,
            no_telp='081234567892',
            is_verified=True
        )
        
        self.admin_dashboard_profile = AdminProfile.objects.create(
            user_profile=self.admin_profile
        )
        
        self.car = Car.objects.create(
            seller=self.seller,
            seller_buat_dashboard=self.seller_dashboard_profile,
            car_name='Test Car',
            brand='Test Brand',
            year=2020,
            mileage=50000,
            location='Test Location',
            transmission='Manual',
            plate_type='Even',
            price=100000000,
            instalment=2000000
        )
        
        self.buyer_question = Question.objects.create(
            user=self.buyer,
            title='Buyer Question',
            content='Buyer Content',
            category=Category.UMUM
        )
        
        self.seller_question = Question.objects.create(
            user=self.seller,
            title='Seller Question',
            content='Seller Content',
            category=Category.JUAL_BELI
        )
        
        self.buyer_reply = Reply.objects.create(
            question=self.seller_question,
            user=self.buyer,
            content='Buyer Reply'
        )
        
        self.seller_reply = Reply.objects.create(
            question=self.buyer_question,
            user=self.seller,
            content='Seller Reply'
        )
        
        self.client = Client()

    def test_show_forum(self):
        response = self.client.get(reverse('forum:show_forum'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'show_forum.html')
        self.assertIn('cars', response.context)

    def test_get_questions_json(self):
        response = self.client.get(reverse('forum:get_questions_json'))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('questions', data)
        self.assertIn('total_pages', data)
        self.assertIn('current_page', data)

        response = self.client.get(reverse('forum:get_questions_json'), {'sort': 'populer'})
        self.assertEqual(response.status_code, 200)

        response = self.client.get(reverse('forum:get_questions_json'), 
                                 {'category': Category.JUAL_BELI})
        self.assertEqual(response.status_code, 200)
        data = response.json()
        questions = data['questions']
        self.assertTrue(all(q['fields']['category'] == Category.JUAL_BELI 
                          for q in questions))

        response = self.client.get(reverse('forum:get_questions_json'), 
                                 {'search': 'Buyer'})
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(len(data['questions']) > 0)

    def test_create_question(self):
        self.client.login(username='testbuyer', password='testpass123')
        
        question_data = {
            'title': 'Test Question',
            'content': 'Test Content',
            'category': Category.UMUM,
            'car_id': str(self.car.id)
        }
        response = self.client.post(reverse('forum:create_question'), question_data)
        self.assertEqual(response.status_code, 201)

        question_data['car_id'] = str(uuid.uuid4()) 
        response = self.client.post(reverse('forum:create_question'), question_data)
        self.assertEqual(response.status_code, 400)

        question_data = {
            'title': '',
            'content': '',
            'category': Category.UMUM
        }
        response = self.client.post(reverse('forum:create_question'), question_data)
        self.assertEqual(response.status_code, 302)

    def test_create_reply(self):
        self.client.login(username='testbuyer', password='testpass123')
        
        reply_data = {
            'content': 'Test Reply Content'
        }
        response = self.client.post(
            reverse('forum:create_reply', kwargs={'pk': self.seller_question.id}),
            reply_data
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Reply.objects.filter(content='Test Reply Content').exists())

        reply_data = {
            'content': ''
        }
        response = self.client.post(
            reverse('forum:create_reply', kwargs={'pk': self.seller_question.id}),
            reply_data
        )
        self.assertEqual(response.status_code, 302) 
        random_uuid = uuid.uuid4()
        response = self.client.post(
            reverse('forum:create_reply', kwargs={'pk': random_uuid}),
            {'content': 'Test Reply'}
        )
        self.assertEqual(response.status_code, 404)
        
    def test_delete_question(self):
        self.client.login(username='testbuyer', password='testpass123')
        response = self.client.post(
            reverse('forum:delete_question', kwargs={'pk': self.buyer_question.id})
        )
        self.assertEqual(response.status_code, 403)
        self.assertTrue(Question.objects.filter(pk=self.buyer_question.id).exists())

        response = self.client.post(
            reverse('forum:delete_question', kwargs={'pk': self.seller_question.id})
        )
        self.assertEqual(response.status_code, 403)
        self.assertTrue(Question.objects.filter(pk=self.seller_question.id).exists())

        self.client.login(username='testadmin', password='testpass123')
        response = self.client.post(
            reverse('forum:delete_question', kwargs={'pk': self.seller_question.id})
        )
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Question.objects.filter(pk=self.seller_question.id).exists())
        
    def test_delete_reply(self):
        self.client.login(username='testbuyer', password='testpass123')
        response = self.client.post(
            reverse('forum:delete_reply', 
                   kwargs={'question_pk': self.seller_question.id,
                          'reply_pk': self.buyer_reply.id})
        )
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Reply.objects.filter(pk=self.buyer_reply.id).exists())

        self.client.login(username='testseller', password='testpass123')
        new_reply = Reply.objects.create(
            question=self.seller_question,
            user=self.buyer,
            content='New Buyer Reply'
        )
        response = self.client.post(
            reverse('forum:delete_reply',
                   kwargs={'question_pk': self.seller_question.id,
                          'reply_pk': new_reply.id})
        )
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Reply.objects.filter(pk=new_reply.id).exists())

        random_uuid1 = uuid.uuid4()
        random_uuid2 = uuid.uuid4()
        response = self.client.post(
            reverse('forum:delete_reply',
                   kwargs={'question_pk': random_uuid1,
                          'reply_pk': random_uuid2})
        )
        self.assertEqual(response.status_code, 404)

    def test_forum_detail(self):
        response = self.client.get(
            reverse('forum:forum_detail', kwargs={'pk': self.buyer_question.id})
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'forum_detail.html')
        self.assertIn('question', response.context)
        self.assertIn('replies', response.context)
        
        self.assertTrue(hasattr(response.context['question'], 'formatted_time'))
        for reply in response.context['replies']:
            self.assertTrue(hasattr(reply, 'formatted_time'))

        random_uuid = uuid.uuid4()
        response = self.client.get(
            reverse('forum:forum_detail', kwargs={'pk': random_uuid})
        )
        self.assertEqual(response.status_code, 404)

    def test_forum_form(self):
        form_data = {
            'title': 'Test Title',
            'content': 'Test Content',
            'category': Category.UMUM,
            'car': self.car.id
        }
        form = ForumForm(data=form_data)
        self.assertTrue(form.is_valid())

        form_data = {
            'title': '<script>alert("XSS")</script>Test Title',
            'content': '<p>Test Content</p>',
            'category': Category.UMUM,
            'car': self.car.id
        }
        form = ForumForm(data=form_data)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['title'].replace('\n', ''), 
                        'alert("XSS")Test Title')
        self.assertEqual(form.cleaned_data['content'].replace('\n', ''), 
                        'Test Content')

    def test_reply_form(self):
        form_data = {
            'content': 'Test Reply Content'
        }
        form = ReplyForm(data=form_data)
        self.assertTrue(form.is_valid())

        form_data = {
            'content': '<p>Test Reply Content</p><script>alert("XSS")</script>'
        }
        form = ReplyForm(data=form_data)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['content'].replace('\n', ''), 
                        'Test Reply Contentalert("XSS")')

        form_data = {
            'content': ''
        }
        form = ReplyForm(data=form_data)
        self.assertFalse(form.is_valid())