from django.db import models
from django.contrib.auth.models import User
from product_catalog.models import Car
import uuid

# Create your models here.
class Category(models.TextChoices) :
    UMUM = 'UM', 'Umum'
    JUAL_BELI = 'JB', 'Jual Beli'
    TIPS_TRICKS = 'TT', 'Tips & Trik'
    SANTAI = 'SA', 'Santai'
    
class Question(models.Model) :
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    car = models.ForeignKey(Car, on_delete=models.CASCADE, null=True, blank=True)
    title = models.CharField(max_length=300)
    content = models.TextField()
    category = models.CharField(default=Category.UMUM, choices=Category.choices, max_length=2, null=False, blank=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta :
        ordering = ['-created_at']
        
    def reply_count(self) :
        return self.reply_set.count()
    
    def latest_reply(self) :
        return self.reply_set.first()

class Reply(models.Model) :
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta :
        ordering = ['created_at']
        verbose_name_plural = 'replies'
        
    def __str__(self) :
        return f'Reply by {self.user.username} on {self.question.title}'