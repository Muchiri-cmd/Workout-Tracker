from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.utils import timezone
from django.contrib import messages
from django.db.models import Count, Sum, F
from django.template.loader import render_to_string
from datetime import timedelta
from .models import Workout, Goal, Progress
from .forms import WorkoutForm, GoalForm, ProgressForm
import json 
from django.views import View

def calculate_workout_stats(user):
    """Calculate workout statistics for a user"""
    today = timezone.now().date()
    
    total_workouts = Workout.objects.filter(user=user).count()
    total_calories = Workout.objects.filter(user=user).aggregate(
        total=Sum('calories_burned'))['total'] or 0
    total_duration = Workout.objects.filter(user=user).aggregate(
        total=Sum('duration'))['total'] or 0
    
    active_goals = Goal.objects.filter(
        user=user,
        deadline__gte=today
    ).count()
    
    return {
        'total_workouts': total_workouts,
        'total_calories': total_calories,
        'total_duration': total_duration,
        'active_goals': active_goals
    }

@login_required
def dashboard(request):
    today = timezone.now().date()

    workouts = Workout.objects.filter(user=request.user).order_by('-date')[:5]
    
    goals = Goal.objects.filter(
        user=request.user,
        deadline__gte=today
    ).order_by('deadline')

    try:
        latest_progress = Progress.objects.filter(user=request.user).latest('date')
    except Progress.DoesNotExist:
        latest_progress = None
    

    stats = calculate_workout_stats(request.user)

    progress_records = Progress.objects.filter(
        user=request.user,
        date__gte=today - timedelta(days=30)
    ).order_by('date')

    progress_data = {
    'labels': [record.date.strftime('%Y-%m-%d') for record in progress_records],
    'weight': [float(record.weight) for record in progress_records],
    'bmi': [float(record.bmi) for record in progress_records],
    'values': [float(record.weight) for record in progress_records]
    }


    context = {
        'workouts': workouts,
        'goals': goals,
        'latest_progress': latest_progress,
        'progress_data': json.dumps(progress_data),
        'total_workouts': stats['total_workouts'],
        'total_calories': stats['total_calories'],
        'total_duration': stats['total_duration'],
        'active_goals': stats['active_goals']
    }
    
    return render(request, 'workouts/dashboard.html', context)

@login_required
def workout_list(request):
    workouts = Workout.objects.filter(user=request.user).order_by('-date')
    stats = calculate_workout_stats(request.user)
    
    context = {
        'workouts': workouts,
        'total_calories': stats['total_calories'],
        'total_duration': stats['total_duration'],
        'total_workouts': stats['total_workouts'],
    }
    
    if request.headers.get('HX-Request'):
        if request.headers.get('HX-Trigger') == 'statsUpdated':
            return render(request, 'workouts/partials/workout_stats.html', context)
        return render(request, 'workouts/partials/workout_list.html', context)
    
    return render(request, 'workouts/workout_list.html', context)

@login_required
def workout_add(request):
    if request.method == 'POST':
        form = WorkoutForm(request.POST)
        if form.is_valid():
            workout = form.save(commit=False)
            workout.user = request.user
            workout.save()
            messages.success(request, 'Workout added successfully!')
            
            if request.headers.get('HX-Request'):
                context = {
                    'workouts': Workout.objects.filter(user=request.user).order_by('-date')[:5],
                    **calculate_workout_stats(request.user)
                }
                return render(request, 'workouts/partials/workout_list.html', context)
            return redirect('workouts:dashboard')
    else:
        form = WorkoutForm()
    
    context = {'form': form, 'title': 'Add Workout'}
    template = 'workouts/partials/workout_form.html' if request.headers.get('HX-Request') else 'workouts/workout_form.html'
    return render(request, template, context)

@login_required
def workout_edit(request, pk):
    workout = get_object_or_404(Workout, pk=pk, user=request.user)
    if request.method == 'POST':
        form = WorkoutForm(request.POST, instance=workout)
        if form.is_valid():
 
            duration = form.cleaned_data['duration']
            intensity = form.cleaned_data['intensity']
            type = form.cleaned_data['type']

            print(f"Updating workout: Duration={duration}, Intensity={intensity}, Type={type}")

            calorieRates = {
                'running': { 'low': 8, 'medium': 11, 'high': 14 },
                'cycling': { 'low': 6, 'medium': 8, 'high': 10 },
                'swimming': { 'low': 7, 'medium': 10, 'high': 13 },
                'weight_training': { 'low': 5, 'medium': 7, 'high': 9 },
                'yoga': { 'low': 3, 'medium': 5, 'high': 7 },
                'hiit': { 'low': 10, 'medium': 13, 'high': 16 },
                'cardio': { 'low': 8, 'medium': 10, 'high': 12 },
                'other': { 'low': 5, 'medium': 7, 'high': 9 }
            }
            
            if type in calorieRates and intensity in calorieRates[type]:
                caloriesPerMinute = calorieRates[type][intensity]
                workout.calories_burned = round(caloriesPerMinute * duration)
                print(f"Calories burned calculated: {workout.calories_burned}")
            
            form.save() 
            messages.success(request, 'Workout updated successfully!')
            
            if request.headers.get('HX-Request'):
                context = {'workouts': Workout.objects.filter(user=request.user).order_by('-date')}
                return render(request, 'workouts/partials/workout_list.html', context)
            return redirect('workouts:workout_list')
    else:
        form = WorkoutForm(instance=workout)

    context = {'form': form, 'title': 'Edit Workout', 'workout': workout}
    if request.headers.get('HX-Request'):
        return render(request, 'workouts/partials/workout_form.html', context)
    return render(request, 'workouts/workout_form.html', context)

@login_required
def workout_delete(request, pk):
    if request.method == 'POST':
        workout = get_object_or_404(Workout, pk=pk, user=request.user)
        workout.delete()
        messages.success(request, 'Workout deleted successfully!')
        
        if request.headers.get('HX-Request'):
            context = {
                'workouts': Workout.objects.filter(user=request.user).order_by('-date'),
                **calculate_workout_stats(request.user)
            }
            return render(request, 'workouts/partials/workout_list.html', context)
    
    return redirect('workouts:workout_list')

@login_required
def goal_list(request):
    today = timezone.now().date()
    active_goals = Goal.objects.filter(user=request.user, deadline__gte=today).order_by('deadline')
    completed_goals = Goal.objects.filter(user=request.user, deadline__lt=today).order_by('-deadline')
    return render(request, 'workouts/goal_list.html', {
        'active_goals': active_goals,
        'completed_goals': completed_goals
    })

@login_required
def goal_add(request):
    if request.method == 'POST':
        form = GoalForm(request.POST)
        if form.is_valid():
            goal = form.save(commit=False)
            goal.user = request.user
            goal.save()
            messages.success(request, 'Goal added successfully!')
            
            if request.headers.get('HX-Request'):
                goals = Goal.objects.filter(user=request.user, deadline__gte=timezone.now().date()).order_by('deadline')
                return render(request, 'workouts/partials/goal_list.html', {'goals': goals})
            return redirect('workouts:dashboard')
    else:
        form = GoalForm()
    
    context = {'form': form, 'title': 'Set New Goal'}
    template = 'workouts/partials/goal_form.html' if request.headers.get('HX-Request') else 'workouts/goal_form.html'
    return render(request, template, context)

@login_required
def goal_edit(request, pk):
    goal = get_object_or_404(Goal, pk=pk, user=request.user)
    if request.method == 'POST':
        form = GoalForm(request.POST, instance=goal)
        if form.is_valid():
            form.save()
            messages.success(request, 'Goal updated successfully!')
            
            if request.headers.get('HX-Request'):
                context = {
                    'goals': Goal.objects.filter(user=request.user),
                    'active_goals': Goal.objects.filter(user=request.user, deadline__gte=timezone.now().date()).count()
                }
                return render(request, 'workouts/partials/goal_list.html', context)
            return redirect('workouts:dashboard')
    else:
        form = GoalForm(instance=goal)
    return render(request, 'workouts/partials/goal_form.html', {'form': form, 'title': 'Edit Goal', 'goal': goal})

@login_required
def goal_delete(request, pk):
    if request.method == 'POST':
        goal = get_object_or_404(Goal, pk=pk, user=request.user)
        goal.delete()
        messages.success(request, 'Goal deleted successfully!')
        
        if request.headers.get('HX-Request'):
            context = {
                'goals': Goal.objects.filter(user=request.user),
                'total_goals': Goal.objects.filter(user=request.user).count()
            }
            return render(request, 'workouts/partials/goal_list.html', context)
    
    return redirect('workouts:dashboard')

@login_required
def progress_list(request):
    progress_records = Progress.objects.filter(user=request.user).order_by('date')
    progress_data = {
        'dates': [record.date.strftime('%Y-%m-%d') for record in progress_records],
        'weights': [float(record.weight) for record in progress_records],
        'bmis': [float(record.bmi) for record in progress_records]
    }
    return render(request, 'workouts/progress_list.html', {'progress_data': progress_data , 'progress_records' : progress_records })

@login_required
def progress_add(request):
    if request.method == 'POST':
        form = ProgressForm(request.POST)
        if form.is_valid():
            progress = form.save(commit=False)
            progress.user = request.user
            progress.save()
            messages.success(request, 'Progress logged successfully!')
            
            if request.headers.get('HX-Request'):
                context = {
                    'latest_progress': Progress.objects.filter(user=request.user).latest('date')
                }
                return render(request, 'workouts/partials/progress_stats.html', context)
            return redirect('workouts:dashboard')
    else:
        form = ProgressForm()
    
    context = {'form': form, 'title': 'Log Progress'}
    template = 'workouts/partials/progress_form.html' if request.headers.get('HX-Request') else 'workouts/progress_form.html'
    return render(request, template, context)

@login_required
def progress_edit(request, pk):
    progress = get_object_or_404(Progress, pk=pk, user=request.user)
    if request.method == 'POST':
        form = ProgressForm(request.POST, instance=progress)
        if form.is_valid():
            form.save()
            messages.success(request, 'Progress updated successfully!')
            return redirect('workouts:progress_list')
    else:
        form = ProgressForm(instance=progress)
    return render(request, 'workouts/progress_form.html', {'form': form, 'title': 'Edit Progress'})

@login_required
def progress_delete(request, pk):
    progress = get_object_or_404(Progress, pk=pk, user=request.user)
    progress.delete()
    messages.success(request, 'Progress record deleted successfully!')
    return redirect('workouts:progress_list')

@login_required
def stats_overview(request):
    if request.headers.get('HX-Request'):
        context = {
            'total_calories': Workout.objects.filter(user=request.user).aggregate(Sum('calories_burned'))['calories_burned__sum'] or 0,
            'total_duration': Workout.objects.filter(user=request.user).aggregate(Sum('duration'))['duration__sum'] or 0,
            'total_workouts': Workout.objects.filter(user=request.user).count(),
            'active_goals': Goal.objects.filter(user=request.user, deadline__gte=timezone.now().date()).count()
        }
        return render(request, 'workouts/partials/stats_overview.html', context)
    return redirect('workouts:dashboard')

@login_required
def profile(request):
    today = timezone.now().date()
    latest_progress = Progress.objects.filter(user=request.user).order_by('-date').first()
    active_goals = Goal.objects.filter(user=request.user, deadline__gte=today).order_by('deadline')
    workout_stats = Workout.objects.filter(user=request.user).aggregate(
        total_workouts=Count('id'),
        total_calories=Sum('calories_burned'),
        total_duration=Sum('duration')
    )
    
    context = {
        'latest_progress': latest_progress,
        'active_goals': active_goals,
        'workout_stats': workout_stats,
    }
    return render(request, 'workouts/profile.html', context)

class StatsUpdateView(View):
    def get(self, request, *args, **kwargs):
        # Calculate stats
        total_calories = Workout.objects.filter(user=request.user).aggregate(Sum('calories_burned'))['calories_burned__sum'] or 0
        total_duration = Workout.objects.filter(user=request.user).aggregate(Sum('duration'))['duration__sum'] or 0
        total_workouts = Workout.objects.filter(user=request.user).count()
        
        # Prepare stats data
        stats = [
            {
                'value': total_calories,
                'label': 'Total Calories Burned',
                'icon': 'fire-flame-curved'
            },
            {
                'value': total_duration,
                'label': 'Total Minutes',
                'icon': 'clock'
            },
            {
                'value': total_workouts,
                'label': 'Total Workouts',
                'icon': 'dumbbell'
            }
        ]
        
        html = render_to_string('workouts/partials/stats_overview.html', {
            'stats': stats
        }, request=request)
        
        return JsonResponse({'html': html})
