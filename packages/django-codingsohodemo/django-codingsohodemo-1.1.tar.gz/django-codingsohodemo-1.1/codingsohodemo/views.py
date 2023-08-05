from django.shortcuts import render

# Create your views here.
def pgwshow(request):
    return render(request, 'codingsohodemo/pgwshow.html', {})