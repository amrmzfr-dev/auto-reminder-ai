from django.shortcuts import render, redirect
from ..forms import TestFileForm
from ..models import TestFile

def upload_file(request):
    if request.method == 'POST':
        form = TestFileForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('upload_file')  # Redirect to clear form and refresh list
    else:
        form = TestFileForm()

    files = TestFile.objects.order_by('-uploaded_at')

    return render(request, 'accounts/test/upload.html', {'form': form, 'files': files})
