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
        ('yoga', 'Yoga/Flexibility'),
        ('hiit', 'HIIT'),
        ('cardio', 'Cardio'),
        ('other', 'Other'),
    ]

    INTENSITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='workouts')
    type = models.CharField(max_length=20, choices=WORKOUT_TYPES)
    duration = models.IntegerField(validators=[MinValueValidator(1)], help_text='Duration in minutes')
    intensity = models.CharField(max_length=10, choices=INTENSITY_CHOICES, default='medium')
    calories_burned = models.IntegerField(validators=[MinValueValidator(0)])
    date = models.DateTimeField(default=timezone.now)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-date']

    def save(self, *args, **kwargs):
        if not self.calories_burned:  # Only calculate if not manually set
            self.calories_burned = self.calculate_calories()
        super().save(*args, **kwargs)

    def calculate_calories(self):
        # Base calorie rates per minute
        calorie_rates = {
            'strength': 8,      # 7-9 calories per minute
            'cardio': 11,       # 10-12 calories per minute
            'hiit': 13.5,       # 12-15 calories per minute
            'yoga': 5,          # 4-6 calories per minute
            'calisthenics': 9,  # 8-10 calories per minute
        }

        # Intensity multipliers
        intensity_factors = {
            'low': 0.8,
            'medium': 1.0,
            'high': 1.2,
        }

        base_rate = calorie_rates.get(self.type, 8)  # Default to 8 if type not found
        intensity_multiplier = intensity_factors.get(self.intensity, 1.0)
        
        return int(base_rate * self.duration * intensity_multiplier)

    def __str__(self):
        return f"{self.user.username}'s {self.get_type_display()} workout on {self.date.strftime('%Y-%m-%d')}"

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
