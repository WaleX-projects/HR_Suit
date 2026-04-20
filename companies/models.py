import uuid
from django.db import models,transaction

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
         
         
         
class CompanySettings(models.Model):
    organization = models.OneToOneField(Company, on_delete=models.CASCADE, related_name="settings")
    date_format = models.CharField(max_length=20, default="YYYY-MM-DD")
    working_days = models.JSONField(default=list)       


class IDCounter(models.Model):
    name = models.CharField(max_length=100, unique=True) # e.g., "AutoSheck"
    last_value = models.PositiveIntegerField(default=0)

    def next_id(self):
        with transaction.atomic():
            # select_for_update() locks the row so two people 
            # can't get the same number at once
            counter, created = IDCounter.objects.select_for_update().get_or_create(name=self.name)
            counter.last_value += 1
            counter.save()
            return counter.last_value
