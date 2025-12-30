from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('register/', views.register, name='register'),
    path('verify/', views.verify_profile, name='verify_profile'),
    path('apply/', views.apply_loan, name='apply_loan'),
    path('repay/', views.repay_loan, name='repay_loan'),
]
