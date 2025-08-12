# accounts/test_models.py
from django.db import models

class TestFile(models.Model):
    # Remove the 'storage=media_storage' argument.
    # Django will now use the default storage backend from settings.py.
    # The `upload_to='uploads/'` will now correctly be a path *inside* the bucket.
    uploaded_file = models.FileField(upload_to='uploads/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.uploaded_file.name