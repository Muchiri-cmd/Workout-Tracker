from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.db import models
from django.utils import timezone
from .forms import UserRegisterForm, UserUpdateForm, ProfileUpdateForm

# Create your views here.
def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  
            messages.success(request, f'Welcome to FitTrack Pro, {user.first_name}! Your account has been created.')
            return redirect('workouts:dashboard')
    else:
        form = UserRegisterForm()
    return render(request, 'users/register.html', {'form': form})

@login_required
def profile(request):
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)
        
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, 'Your profile has been updated successfully!')
            return redirect('users:profile') 
    
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)
        
    latest_progress = request.user.progress_records.order_by('-date').first()
    
    context = {
        'u_form': u_form,
        'p_form': p_form,
        'latest_progress': latest_progress,
        'user_stats': {
            'total_workouts': request.user.workouts.count(),
            'total_calories': request.user.workouts.aggregate(total=models.Sum('calories_burned'))['total'] or 0,
            'active_goals': request.user.goals.filter(deadline__gte=timezone.now()).count(),
            'completed_goals': request.user.goals.filter(deadline__lt=timezone.now()).count(),
        }
    }
    return render(request, 'users/profile.html', context)