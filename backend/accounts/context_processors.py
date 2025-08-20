from .models import Task
from .models import Installation
from .models import InstallerProfile

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
    # Ensure the user is authenticated before proceeding.
    if not request.user.is_authenticated:
        # If not authenticated, return an empty dictionary.
        return {}

    try:
        # Attempt to retrieve the installer profile associated with the user.
        installer_profile = request.user.installerprofile
    except AttributeError:
        # If the user does not have an installer profile, return an empty dictionary.
        return {}

    # Filter installations by the current installer's profile.
    installations = Installation.objects.filter(installer=installer_profile)

    # Calculate the total number of tasks assigned to the installer.
    total_tasks = installations.count()

    # Count tasks with 'IN_PROGRESS' status.
    # This aligns with ('IN_PROGRESS', 'In Progress') in STATUS_CHOICES.
    in_progress = installations.filter(status="IN_PROGRESS").count()

    # Count tasks with 'PENDING_ACCEPTANCE' status for 'pending' tasks.
    # This replaces the old "Scheduled" which wasn't in STATUS_CHOICES and
    # assumes 'PENDING_ACCEPTANCE' is the new equivalent for tasks awaiting action.
    pending = installations.filter(status="PENDING_ACCEPTANCE").count()

    # Count tasks with 'COMPLETED' status.
    # This aligns with ('COMPLETED', 'Completed') in STATUS_CHOICES.
    completed = installations.filter(status="COMPLETED").count()

    # Calculate the completion rate. Avoid division by zero.
    completion_rate = int((completed / total_tasks) * 100) if total_tasks > 0 else 0

    # Return a dictionary containing the calculated metrics.
    return {
        'total_tasks': total_tasks,
        'in_progress': in_progress,
        'pending': pending,
        'completed' : completed,
        'completion_rate': completion_rate,
    }

def current_company(request):
    if not request.user.is_authenticated:
        return {"current_company": "Company"}

    if getattr(request.user, "role", None) == 1:
        # Admin fallback
        return {"current_company": "Admin"}

    try:
        installer = InstallerProfile.objects.get(user=request.user)
        company_name = installer.company_name or "Company"
    except InstallerProfile.DoesNotExist:
        company_name = "Company"

    initial = company_name[0].upper() if company_name else "C"

    return {"current_company": company_name, "company_initial": initial}

def user_company_info(request):
    if not request.user.is_authenticated:
        return {
            "username": "Guest",
            "company_name": "Company",
            "company_initial": "C"
        }
 
    username = request.user.username
    if getattr(request.user, "role", None) == 1:
        company_name = "Admin"
    else:
        try:
            installer = InstallerProfile.objects.get(user=request.user)
            company_name = installer.company_name or "Company"
        except InstallerProfile.DoesNotExist:
            company_name = "Company"

    company_initial = company_name[0].upper() if company_name else "C"

    return {
        "username": username,
        "company_name": company_name,
        "company_initial": company_initial,
    }