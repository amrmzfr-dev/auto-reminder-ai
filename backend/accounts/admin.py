from django.contrib import admin
from .models import Task, Notification

admin.site.register(Task)

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'message', 'is_read', 'created_at', 'related_installation')
    list_filter = ('is_read', 'created_at', 'user')
    search_fields = ('message', 'user__username')
    readonly_fields = ('created_at',)
    ordering = ('-created_at',)
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'related_installation')
