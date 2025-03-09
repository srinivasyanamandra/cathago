from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

class User(AbstractUser):
    ROLE_CHOICES = (
        ('user', 'User'),
        ('admin', 'Admin'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='user')
    credits = models.IntegerField(default=20)
    last_reset = models.DateTimeField(default=timezone.now)
    
    def reset_credits_if_needed(self):
        now = timezone.now()
        # Check if last reset was before today's midnight
        today_midnight = timezone.datetime.combine(now.date(), timezone.datetime.min.time())
        today_midnight = timezone.make_aware(today_midnight)

        if self.last_reset < today_midnight:
            # Calculate the difference to add, ensuring the total does not exceed 20
            difference = 20 - self.credits
            if difference > 0:
                self.credits += difference
            self.last_reset = now
            self.save()
        return self.credits

# models.py
class Scan(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='scans')
    scan_date = models.DateTimeField(auto_now_add=True)
    scan_type = models.CharField(max_length=100)
    result = models.TextField()
    document_content = models.TextField(default='')  # Store the uploaded document's content

    class Meta:
        ordering = ['-scan_date']

class CreditRequest(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('denied', 'Denied'),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='credit_requests')
    requested_credits = models.IntegerField()
    request_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    reviewed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='reviewed_requests')
    review_date = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-request_date']
