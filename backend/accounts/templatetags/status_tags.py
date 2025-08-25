# accounts/templatetags/status_tags.py
from django import template
from django.utils.safestring import mark_safe

register = template.Library()


@register.filter
def get_status_classes(status):
    """
    Get CSS classes for status badges to eliminate duplicate logic in templates.
    
    Args:
        status (str): The installation status
        
    Returns:
        str: CSS classes for the status badge
    """
    status_classes = {
        'COMPLETED': 'bg-[#006239] text-green-100',
        'IN_PROGRESS': 'bg-yellow-600 text-yellow-100',
        'SCHEDULED': 'bg-gray-500 text-gray-100',
        'ON_HOLD': 'bg-orange-600 text-orange-100',
        'SUBMITTED': 'bg-indigo-600 text-indigo-100',
        'PENDING_ACCEPTANCE': 'bg-purple-600 text-purple-100',
        'ACCEPTED': 'bg-teal-600 text-teal-100',
        'REJECTED': 'bg-red-600 text-red-100',
        'EXPIRED': 'bg-red-700 text-red-100',
    }
    return status_classes.get(status, 'bg-gray-600 text-gray-100')


@register.filter
def get_status_display_name(status):
    """
    Get human-readable display name for status.
    
    Args:
        status (str): The installation status
        
    Returns:
        str: Human-readable status name
    """
    status_names = {
        'COMPLETED': 'Completed',
        'IN_PROGRESS': 'In Progress',
        'SCHEDULED': 'Scheduled',
        'ON_HOLD': 'On Hold',
        'SUBMITTED': 'Submitted',
        'PENDING_ACCEPTANCE': 'Pending Acceptance',
        'ACCEPTED': 'Accepted',
        'REJECTED': 'Rejected',
        'EXPIRED': 'Expired',
    }
    return status_names.get(status, status.title())


@register.filter
def render_status_badge(status, size='text-xs'):
    """
    Render a complete status badge with proper styling.
    
    Args:
        status (str): The installation status
        size (str): CSS class for text size
        
    Returns:
        str: HTML for the status badge
    """
    classes = get_status_classes(status)
    display_name = get_status_display_name(status)
    
    return mark_safe(f'<span class="inline-block px-3 py-1 {size} font-semibold {classes} rounded-full">{display_name}</span>')
