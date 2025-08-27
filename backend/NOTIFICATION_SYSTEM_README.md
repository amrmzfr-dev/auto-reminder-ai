# 🔔 Admin Notification System

## Overview
This Django application now includes a fully functional notification system for admin users. When one admin creates, edits, or deletes tasks, all other admin users receive real-time notifications.

## ✨ Features

### 🔔 Notification Bell Icon
- **Location**: Header (top-right, between Feedback button and Profile button)
- **Badge**: Shows unread notification count with red badge
- **Dropdown**: Click to view recent notifications

### 📱 Real-time Updates
- **WebSocket**: Instant notifications via Django Channels
- **Live Badge**: Notification count updates in real-time
- **Toast Messages**: Pop-up notifications for new messages

### 📊 Dashboard Integration
- **Notification Card**: Shows recent notifications on admin dashboard
- **Unread Count**: Displays total unread notifications
- **Refresh Button**: Manual refresh of notifications

## 🚀 How It Works

### 1. Automatic Notifications
When an admin performs these actions, notifications are automatically created:

- **Create Task**: `✅ New Task Added: [Task Title] by [Username]`
- **Edit Task**: `✏️ Task Updated: [Task Title] by [Username]`
- **Delete Task**: `🗑️ Task Deleted: [Task Title] by [Username]`

### 2. Notification Delivery
- **Database**: Stored in `Notification` model
- **Real-time**: Sent via WebSocket to all connected admins
- **Badge Update**: Header badge updates automatically

### 3. User Experience
- **Click Bell**: Opens notification dropdown
- **Mark Read**: Individual or bulk mark as read
- **View All**: Access to complete notification history

## 🛠️ Technical Implementation

### Backend Components
- **Models**: `Notification` model with user, message, read status
- **Views**: API endpoints for notification CRUD operations
- **WebSocket**: Real-time communication via Django Channels
- **Admin**: Django admin interface for notification management

### Frontend Components
- **Bell Icon**: SVG icon with notification badge
- **Dropdown**: Notification list with read/unread status
- **Dashboard**: Integrated notification display
- **JavaScript**: Real-time updates and interaction

### API Endpoints
```
GET  /admin/notifications/                    # List notifications
POST /admin/notifications/{id}/mark-read/     # Mark single as read
POST /admin/notifications/mark-all-read/      # Mark all as read
```

## 🔧 Setup Requirements

### 1. Django Channels
Make sure Django Channels is properly configured in your project:

```python
# settings.py
INSTALLED_APPS = [
    'channels',
    # ... other apps
]

ASGI_APPLICATION = 'your_project.asgi.application'
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels.layers.InMemoryChannelLayer'
    }
}
```

### 2. WebSocket Consumer
The WebSocket consumer is already configured in `accounts/consumer.py` and `accounts/routing.py`.

### 3. Database Migration
Run migrations to create the notification table:

```bash
python manage.py makemigrations
python manage.py migrate
```

## 📱 Usage Examples

### For Admin Users
1. **View Notifications**: Click the bell icon in the header
2. **Check Dashboard**: See recent notifications on admin dashboard
3. **Mark as Read**: Click "Mark read" on individual notifications
4. **Mark All Read**: Use "Mark all read" button in dropdown

### For Developers
1. **Add New Notification Types**: Modify the admin views
2. **Customize Messages**: Update notification message formats
3. **Extend Functionality**: Add notifications for other admin actions

## 🎨 Customization

### Notification Messages
Edit the message format in `admin_views.py`:

```python
Notification.objects.create(
    user=admin_user,
    message=f"✅ New Task Added: {task.title} by {request.user.username}",
    related_installation=None
)
```

### Styling
Modify the CSS classes in `base.html` and `admin_dashboard.html` to match your design system.

### Badge Colors
Change the notification badge color by modifying the `bg-red-500` class in the bell icon.

## 🐛 Troubleshooting

### Common Issues
1. **Notifications not showing**: Check WebSocket connection in browser console
2. **Badge not updating**: Verify notification count API endpoint
3. **Real-time not working**: Ensure Django Channels is properly configured

### Debug Steps
1. Check browser console for JavaScript errors
2. Verify WebSocket connection status
3. Check Django server logs for backend errors
4. Confirm notification objects are being created in database

## 🔮 Future Enhancements

### Potential Features
- **Email Notifications**: Send email alerts for important notifications
- **Push Notifications**: Browser push notifications
- **Notification Preferences**: User-configurable notification settings
- **Rich Notifications**: Include images, links, and actions
- **Notification History**: Paginated notification archive
- **Mobile App**: Native mobile notification support

## 📚 Dependencies

- Django 3.2+
- Django Channels 3.0+
- Python 3.8+
- WebSocket support in browser

## 🤝 Contributing

To add new notification types or modify the system:

1. Update the relevant admin view
2. Add notification creation logic
3. Test the notification flow
4. Update this documentation

---

**Note**: This notification system is designed for admin users only. Regular users (installers) do not receive these notifications. 