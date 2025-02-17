from django.db import models
from django.contrib.auth.models import AbstractUser

# Extending Django's User Model
class CustomUser(AbstractUser):
    USER_TYPES = [
        ('client', 'Client'),
        ('service', 'Service Provider'),
    ]
    user_type = models.CharField(max_length=10, choices=USER_TYPES, default='client')

    def is_client(self):
        return self.user_type == 'client'

    def is_service_provider(self):
        return self.user_type == 'service'



from django.db import models
from django.contrib.auth.models import User
from django.conf import settings



# Department model to categorize complaints
class Department(models.Model):
    name = models.CharField(max_length=100)
    
    def __str__(self):
        return self.name

# Complaint model to store user complaints
class Complaint(models.Model):
    STATUS_CHOICES = [
        ('open', 'Open'),
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    description = models.TextField()
    category = models.ForeignKey(Department, on_delete=models.CASCADE)  # Categorize complaint by department
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    date_submitted = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Complaint by {self.user.username} in {self.category.name} - Status: {self.status}"

