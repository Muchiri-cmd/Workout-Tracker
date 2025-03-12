from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from PIL import Image
import os

# Create your models here.

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(max_length=500, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    height = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, help_text="Height in cm")
    weight = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, help_text="Weight in kg")
    profile_picture = models.ImageField(default='default.jpg', upload_to='profile_pics')
    fitness_level = models.CharField(max_length=20, choices=[
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced')
    ], default='beginner')
    
    def __str__(self):
        return f'{self.user.username} Profile'
    
    def save(self, *args, **kwargs):
        # If this is a new profile, ensure it has the default image
        if not self.pk and not self.profile_picture:
            self.profile_picture = 'default.jpg'
            
        super().save(*args, **kwargs)
        
        if self.profile_picture:
            try:
                img_path = self.profile_picture.path
                if os.path.exists(img_path):
                    img = Image.open(img_path)
                    if img.height > 300 or img.width > 300:
                        output_size = (300, 300)
                        img.thumbnail(output_size)
                        img.save(img_path)
            except Exception as e:
                # If there's any error processing the image, set to default
                if not self.profile_picture or not os.path.exists(self.profile_picture.path):
                    self.profile_picture = 'default.jpg'
                    self.save(update_fields=['profile_picture'])

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()
