from django import forms
from .models import Workout, Goal, Progress

class WorkoutForm(forms.ModelForm):
    class Meta:
        model = Workout
        fields = ['type', 'duration', 'intensity', 'notes']
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 3}),
            'duration': forms.NumberInput(attrs={'min': 1}),
        }

class GoalForm(forms.ModelForm):
    class Meta:
        model = Goal
        fields = ['goal_type', 'target_value', 'current_progress', 'deadline']
        widgets = {
            'deadline': forms.DateInput(attrs={'type': 'date'}),
        }

class ProgressForm(forms.ModelForm):
    class Meta:
        model = Progress
        fields = ['weight', 'height', 'notes']
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 3}),
        }