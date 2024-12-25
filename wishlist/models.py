from django.db import models
from django.contrib.auth.models import User
from product_catalog.models import Car
import uuid

class Wishlist(models.Model):
    
    PRIORITY_CHOICES = [
        (1, 'Rendah'),
        (2, 'Sedang'),
        (3, 'Tinggi')
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    car = models.ForeignKey(Car, on_delete=models.CASCADE, null=True)
    priority = models.IntegerField(choices=PRIORITY_CHOICES, default=1)
    
    class Meta:
        unique_together = ('user', 'car')
        ordering = ['-priority']

    def __str__(self):
        return f"{self.user.username}'s wishlist - {self.car.name} (Priority: {self.get_priority_display()})"
