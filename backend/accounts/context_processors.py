from .models import Task

def task_metrics(request):
    if not request.user.is_authenticated:
        return {}

    tasks = Task.objects.all()

    total_tasks = tasks.count()
    in_progress = tasks.filter(status="In Progress").count()
    pending = tasks.filter(status="Pending").count()
    completed = tasks.filter(status="Completed").count()
    completion_rate = int((completed / total_tasks) * 100) if total_tasks > 0 else 0

    return {
        'total_tasks': total_tasks,
        'in_progress': in_progress,
        'pending': pending,
        'completion_rate': completion_rate,
    }
