from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from django.utils import timezone

class Workout(models.Model):
    WORKOUT_TYPES = [
        ('running', 'Running'),
        ('cycling', 'Cycling'),
        ('swimming', 'Swimming'),
        ('weight_training', 'Weight Training'),
        ('yoga', 'Yoga'),
        ('hiit', 'HIIT'),
        ('cardio', 'Cardio'),
        ('other', 'Other')
    ]

    INTENSITY_LEVELS = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High')
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='workouts')
    type = models.CharField(max_length=20, choices=WORKOUT_TYPES)
    duration = models.IntegerField(validators=[MinValueValidator(1)], help_text="Duration in minutes")
    intensity = models.CharField(max_length=10, choices=INTENSITY_LEVELS, default='medium')
    calories_burned = models.IntegerField(default=0)
    notes = models.TextField(blank=True)
    date = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-date']

    def save(self, *args, **kwargs):
        # Calculate calories based on workout type, duration, and intensity
        calorie_rates = {
            'running': 10,
            'cycling': 10,
            'swimming': 11,
            'weight_training': 8,
            'yoga': 5,
            'hiit': 13,
            'cardio': 10,
            'other': 7
        }

        intensity_factors = {
            'low': 0.8,
            'medium': 1.0,
            'high': 1.2
        }

        base_rate = calorie_rates.get(self.type, 7)
        factor = intensity_factors.get(self.intensity, 1.0)
        
        self.calories_burned = int(base_rate * self.duration * factor)
        
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.get_type_display()} - {self.duration} minutes - {self.date.strftime('%Y-%m-%d')}"

class Goal(models.Model):
    GOAL_TYPES = [
        ('distance', 'Distance'),
        ('weight_loss', 'Weight Loss'),
        ('workout_frequency', 'Workout Frequency'),
        ('strength', 'Strength'),
        ('endurance', 'Endurance'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='goals')
    goal_type = models.CharField(max_length=20, choices=GOAL_TYPES)
    target_value = models.DecimalField(max_digits=8, decimal_places=2)
    current_progress = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    deadline = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['deadline']

    def __str__(self):
        return f"{self.user.username}'s {self.goal_type} goal"

    @property
    def progress_percentage(self):
        if self.target_value == 0:
            return 0
        return (self.current_progress / self.target_value) * 100

class Progress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='progress_records')
    weight = models.DecimalField(max_digits=5, decimal_places=2, help_text='Weight in kg')
    height = models.DecimalField(max_digits=5, decimal_places=2, help_text='Height in cm')
    date = models.DateField(default=timezone.now)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-date']
        verbose_name_plural = 'Progress'

    def __str__(self):
        return f"{self.user.username}'s progress on {self.date}"

    @property
    def bmi(self):
        """Calculate BMI: weight(kg) / height(m)²"""
        height_in_meters = self.height / 100
        return round(self.weight / (height_in_meters ** 2), 2)

    @property
    def bmi_category(self):
        bmi = self.bmi
        if bmi < 18.5:
            return 'Underweight'
        elif 18.5 <= bmi < 25:
            return 'Normal'
        elif 25 <= bmi < 30:
            return 'Overweight'
        else:
            return 'Obese'
