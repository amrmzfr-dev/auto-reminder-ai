from .models import Task
from .models import Installation

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


def installer_task_metrics(request):
    if not request.user.is_authenticated:
        return {}

    try:
        installer_profile = request.user.installerprofile
    except AttributeError:
        return {}

    installations = Installation.objects.filter(installer=installer_profile)

    total_tasks = installations.count()
    in_progress = installations.filter(status="In Progress").count()
    pending = installations.filter(status="Scheduled").count()
    completed = installations.filter(status="Completed").count()

    completion_rate = int((completed / total_tasks) * 100) if total_tasks > 0 else 0

    return {
        'total_tasks': total_tasks,
        'in_progress': in_progress,
        'pending': pending,
        'completion_rate': completion_rate,
    }