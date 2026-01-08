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

class AdminLoanForm(forms.ModelForm):
    borrower = forms.ModelChoiceField(queryset=User.objects.all(), widget=forms.Select(attrs={'class': 'form-control'}))
    
    class Meta:
        model = Loan
        fields = ['borrower', 'amount', 'term_days', 'status']
        widgets = {
            'amount': forms.NumberInput(attrs={'class': 'form-control'}),
            'term_days': forms.NumberInput(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
        }

class AdminUserForm(UserCreationForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class': 'form-control'}))
    is_staff = forms.BooleanField(required=False, label='Admin User')
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2', 'is_staff']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({'class': 'form-control'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control'})
