from django.shortcuts import redirect 
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import RegisterForm
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render 
from django.contrib.auth.models import User
from .models import AuditLog
from django.contrib.auth.views import LoginView
from .forms import TaskForm
from .models import Task
from django.shortcuts import get_object_or_404
from django.core.exceptions import PermissionDenied


def is_admin(user):
    return user.is_authenticated and user.is_staff

def register(request):
    # if request.user.is_authenticated:
    #     return redirect('dashboard')

    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            AuditLog.objects.create(user=user, action="Registered new account")
            messages.success(request, "Account created. You are now logged in.")
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = RegisterForm()

    return render(request, "register.html", {"form": form})

class CustomLoginView(LoginView):
    def form_valid(self, form):
        response = super().form_valid(form)
        AuditLog.objects.create(user=self.request.user, action="Logged in")
        return response



@login_required
def dashboard(request):
    users = User.objects.all() if request.user.is_staff else None
    tasks = Task.objects.filter(owner=request.user)  # Fetch tasks for logged-in user
    return render(request, "dashboard.html", {"users": users, "tasks": tasks})


@login_required
def audit_log(request):
    if not is_admin(request.user):
        raise PermissionDenied  # This triggers your 403.html
    logs = AuditLog.objects.all().order_by('-timestamp')
    return render(request, "audit_log.html", {"logs": logs})



@login_required
def logout_view(request):
    AuditLog.objects.create(user=request.user, action="Logged out")
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect("login")


# CRUD for Tasks
@login_required
def create_task(request):
    if request.method == "POST":
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.owner = request.user
            task.save()
            AuditLog.objects.create(user=request.user, action=f"Created task: {task.title}")
            messages.success(request, "Task created successfully.")
            return redirect("dashboard")
    else:
        form = TaskForm()
    return render(request, "create_task.html", {"form": form})

@login_required
def edit_task(request, task_id):
    task = get_object_or_404(Task, id=task_id, owner=request.user)
    if request.method == "POST":
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            form.save()
            AuditLog.objects.create(user=request.user, action=f"Edited task: {task.title}")
            messages.success(request, "Task updated successfully.")
            return redirect("dashboard")
    else:
        form = TaskForm(instance=task)
    return render(request, "edit_task.html", {"form": form})

@login_required
def delete_task(request, task_id):
    task = get_object_or_404(Task, id=task_id, owner=request.user)
    AuditLog.objects.create(user=request.user, action=f"Deleted task: {task.title}")
    task.delete()
    messages.success(request, "Task deleted successfully.")
    return redirect("dashboard")

