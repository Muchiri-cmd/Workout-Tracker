function updateCalories() {
    const duration = parseInt(document.getElementById('id_duration').value) || 0;
    const intensity = document.getElementById('id_intensity').value;
    const type = document.getElementById('id_type').value;
    
    let caloriesPerMinute = 0;
    const calorieRates = {
        'running': { low: 8, medium: 11, high: 14 },
        'cycling': { low: 6, medium: 8, high: 10 },
        'swimming': { low: 7, medium: 10, high: 13 },
        'weight_training': { low: 5, medium: 7, high: 9 },
        'yoga': { low: 3, medium: 5, high: 7 },
        'hiit': { low: 10, medium: 13, high: 16 },
        'other': { low: 5, medium: 7, high: 9 }
    };
    
    if (type && intensity && duration) {
        caloriesPerMinute = calorieRates[type][intensity];
        const totalCalories = Math.round(caloriesPerMinute * duration);
        document.getElementById('id_calories_burned').value = totalCalories;
    }
}

function animateProgress() {
    const progressBars = document.querySelectorAll('.progress-bar');
    progressBars.forEach(bar => {
        const target = bar.getAttribute('aria-valuenow');
        bar.style.width = target + '%';
    });
}

document.addEventListener('DOMContentLoaded', function() {
    const modals = document.querySelectorAll('.modal');
    modals.forEach(modal => {
        new bootstrap.Modal(modal);
    });
    
    
    animateProgress();
    

    const tooltips = document.querySelectorAll('[data-bs-toggle="tooltip"]');
    tooltips.forEach(tooltip => {
        new bootstrap.Tooltip(tooltip);
    });
});


document.addEventListener('htmx:afterSwap', function(event) {
    if (event.detail.target.id === 'workout-list' || 
        event.detail.target.id === 'goal-list' || 
        event.detail.target.id === 'progress-list') {
        animateProgress();
    }
 
});


function validateForm(formId) {
    const form = document.getElementById(formId);
    if (!form.checkValidity()) {
        event.preventDefault();
        event.stopPropagation();
    }
    form.classList.add('was-validated');
}

function showNotification(message, type = 'success') {
    const toast = document.createElement('div');
    toast.className = `toast align-items-center text-white bg-${type} border-0`;
    toast.setAttribute('role', 'alert');
    toast.setAttribute('aria-live', 'assertive');
    toast.setAttribute('aria-atomic', 'true');
    
    toast.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">
                ${message}
            </div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
        </div>
    `;
    
    const container = document.getElementById('toast-container');
    container.appendChild(toast);
    
    const bsToast = new bootstrap.Toast(toast);
    bsToast.show();
    
    toast.addEventListener('hidden.bs.toast', function() {
        toast.remove();
    });
}