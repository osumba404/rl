from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('register/', views.register, name='register'),
    path('verify/', views.verify_profile, name='verify_profile'),
    path('apply/', views.apply_loan, name='apply_loan'),
    path('repay/', views.repay_loan, name='repay_loan'),
    
    # Admin
    path('staff/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('staff/loan/<int:pk>/approve/', views.approve_loan, name='approve_loan'),
    path('staff/loan/<int:pk>/reject/', views.reject_loan, name='reject_loan'),
]
