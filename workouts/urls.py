from django.urls import path
from . import views
from .views import (
    StatsUpdateView,
)

app_name = 'workouts'

urlpatterns = [
    # Dashboard
    path('', views.dashboard, name='dashboard'),
    
    # Workout URLs
    path('workouts/', views.workout_list, name='workout_list'),
    path('workouts/add/', views.workout_add, name='workout_add'),
    path('workouts/<int:pk>/edit/', views.workout_edit, name='workout_edit'),
    path('workouts/<int:pk>/delete/', views.workout_delete, name='workout_delete'),
    
    # Goal URLs
    path('goals/', views.goal_list, name='goal_list'),
    path('goals/add/', views.goal_add, name='goal_add'),
    path('goals/<int:pk>/edit/', views.goal_edit, name='goal_edit'),
    path('goals/<int:pk>/delete/', views.goal_delete, name='goal_delete'),
    
    # Progress URLs
    path('progress/', views.progress_list, name='progress_list'),
    path('progress/add/', views.progress_add, name='progress_add'),
    path('progress/<int:pk>/edit/', views.progress_edit, name='progress_edit'),
    path('progress/<int:pk>/delete/', views.progress_delete, name='progress_delete'),
    
    # Stats URLs
    path('stats-overview/', views.stats_overview, name='stats_overview'),
    path('stats-update/', StatsUpdateView.as_view(), name='stats_update')
]
