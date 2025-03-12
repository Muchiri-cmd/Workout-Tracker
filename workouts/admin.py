from django.contrib import admin
from .models import Workout, Goal, Progress

# Register your models here.

@admin.register(Workout)
class WorkoutAdmin(admin.ModelAdmin):
    list_display = ('user', 'type', 'duration', 'calories_burned', 'date')
    list_filter = ('type', 'date', 'user')
    search_fields = ('user__username', 'notes')
    date_hierarchy = 'date'

@admin.register(Goal)
class GoalAdmin(admin.ModelAdmin):
    list_display = ('user', 'goal_type', 'target_value', 'current_progress', 'deadline')
    list_filter = ('goal_type', 'deadline', 'user')
    search_fields = ('user__username',)
    date_hierarchy = 'deadline'

@admin.register(Progress)
class ProgressAdmin(admin.ModelAdmin):
    list_display = ('user', 'weight', 'height', 'bmi', 'date')
    list_filter = ('date', 'user')
    search_fields = ('user__username', 'notes')
    date_hierarchy = 'date'
    readonly_fields = ('bmi', 'bmi_category')
