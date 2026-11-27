from django.db import models
import uuid

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models.signals import post_save
from django.dispatch import receiver



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

    is_active = models.BooleanField(default=False)
    email_verification_code = models.CharField(max_length=128, blank=True)
    email_verification_code_expires_at = models.DateTimeField(null=True, blank=True)

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

class Profile(models.Model):
    user = models.OneToOneField(
        User,
        related_name="profile",
        on_delete=models.CASCADE
    )

    reset_password_token = models.CharField(
        max_length=50,
        default="",
        blank=True
    )

    reset_password_expire = models.DateTimeField(
        null=True,
        blank=True
    )

    def __str__(self):
        return f"{self.user.username}'s Profile"

#NOTE: علشان لما تعمل register لل user جديد يعمل profile جديد ليه اوتوماتيك
@receiver(post_save, sender=User)
def save_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

