from django.shortcuts import render, redirect, HttpResponse
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from todos.models import Todo
from django.contrib.auth.models import User
import json


# Create your views here.
def index(request):
    if not request.user.is_authenticated:
        return render(request, 'todos/login.html')
    elif request.user.is_authenticated:
        username = request.user.username
        todos = Todo.objects.filter(user=request.user)
        context = {
            'username': username,
            'todos': todos,
        }
        return render(request, 'todos/index.html', context=context)
    else:
        return HttpResponse("Invalid request method", status=405)


def login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            auth_login(request, user)
            return redirect('index')
        else:
            return render(request, 'todos/login.html', {'error': 'Invalid username or password'})
    if request.method == 'GET':
        return render(request, 'todos/login.html')
    return render(request, 'todos/login.html')

def logout(request):
    if request.method == 'DELETE':
        auth_logout(request)
        return render(request, 'todos/login.html', {'message': 'Logged out successfully'})

def create_todo(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        if not request.user.is_authenticated:
            return redirect('login')
        if title:
            todo = Todo.objects.create(title=title, user=request.user, description=description)
            return redirect('index')
    return render(request, 'todos/index.html', {'error': 'Invalid request method'})

def delete_todo(request, todo_id):
    if request.method == 'DELETE':
        try:
            todo = Todo.objects.get(id=todo_id, user=request.user)
            todo.delete()
            return HttpResponse(status=204)  # No Content
        except Todo.DoesNotExist:
            return HttpResponse(status=404)  # Not Found
    return HttpResponse("Invalid request method", status=405)

def edit_todo(request, todo_id):
    if request.method == 'POST':
        try:
            todo = Todo.objects.get(id=todo_id, user=request.user)
            title = request.POST.get('title')
            description = request.POST.get('description')
            completed = request.POST.get('completed')
            if title:
                todo.title = title
            if description:
                todo.description = description
            if completed is not None:
                todo.completed = True
            if completed is None:
                todo.completed = False  
            todo.save()
            return redirect('index')
        except Todo.DoesNotExist:
            return HttpResponse(status=404) 
    if request.method == 'GET':
        try:
            todo = Todo.objects.get(id=todo_id, user=request.user)
            context = {
                'todo': todo,
            }
            return render(request, 'todos/edit_todo.html', context=context)
        except Todo.DoesNotExist:
            return HttpResponse(status=404)  # Not Found
    return HttpResponse("Invalid request method", status=405)

def toggle_todo_completion(request, todo_id):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            completed = data.get('completed')
            todo = Todo.objects.get(id=todo_id, user=request.user)
            todo.completed = bool(completed)  # Toggle the completed status
            todo.save()
            return HttpResponse(status=200)  # OK
        except Todo.DoesNotExist:
            return HttpResponse(status=404)  # Not Found
    return HttpResponse("Invalid request method", status=405)

def register(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']
        context = {
            'username': username,
            'email': email
        }
        if password != confirm_password:
            context['error'] = 'Passwords do not match'
            return render(request, 'todos/register.html', context=context)
        if User.objects.filter(username=username).exists():
            context['error'] = 'Username already exists'
            return render(request, 'todos/register.html', context=context)
        if User.objects.filter(email=email).exists():
            context['error'] = 'Email already exists'
            return render(request, 'todos/register.html', context=context)
        if len(password) < 8:
            context['error'] = 'Password must be at least 8 characters long'
            return render(request, 'todos/register.html', context=context)
        if not email or not username or not password:
            context['error'] = 'All fields are required'
            return render(request, 'todos/register.html', context=context)
        user = User.objects.create_user(username=username, email=email, password=password)
        user.save()
        login_user = authenticate(request, username=username, password=password)
        if login_user is not None:
            auth_login(request, login_user)
        return redirect('index')
    if request.method == 'GET':
        return render(request, 'todos/register.html')
