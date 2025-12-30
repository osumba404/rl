from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Profile, Loan, Repayment

class UserRegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email']

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['national_id', 'phone_number', 'monthly_income']

class LoanForm(forms.ModelForm):
    class Meta:
        model = Loan
        fields = ['amount', 'term_days']

class RepaymentForm(forms.ModelForm):
    class Meta:
        model = Repayment
        fields = ['amount']
