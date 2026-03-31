import uuid
from django.db import models

class Company(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    country = models.CharField(max_length=100, default="Nigeria")
    timezone = models.CharField(max_length=50, default="Africa/Lagos")
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
         return self.name