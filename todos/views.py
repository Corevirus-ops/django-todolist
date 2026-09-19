from django.shortcuts import render

# Create your views here.
def index(request):
    if request.user.is_authenticated:
        return render(request, 'todos/login.html')
    return render(request, 'todos/index.html')


