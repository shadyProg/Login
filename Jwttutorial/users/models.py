from django.db import models
import uuid

from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):

    class Role(models.TextChoices):
        CUSTOMER = "CUSTOMER", "Customer"
        PROVIDER = "PROVIDER", "Provider"
        ADMIN = "ADMIN", "Admin"

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    
    #NOTE: The username field is already unique by default in Django's AbstractUser model.
    #! no  is not True
    # that username for account not really name , if you want to add name field you can add it as a separate field and make it not unique.
    # that also know as firstname and lastname isnot unique by default in Django's AbstractUser model.
    email = models.EmailField(
        unique=True
    )

    phone_number = models.CharField(
        max_length=13,
        unique=True,
        null=True,
        
    )
    #TODO migrate
    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.CUSTOMER
    )

    def __str__(self):
        return self.username
