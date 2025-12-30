from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView
from . import views 
from .views import CustomLoginView

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('register/', views.register, name='register'),
    path('login/', CustomLoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('audit-log/', views.audit_log, name='audit_log'),

    # Task CRUD
    path('tasks/create/', views.create_task, name='create_task'),
    path('tasks/edit/<int:task_id>/', views.edit_task, name='edit_task'),
    path('tasks/delete/<int:task_id>/', views.delete_task, name='delete_task'),
]
