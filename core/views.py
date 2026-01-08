from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate
from django.contrib import messages
from .forms import UserRegisterForm, ProfileForm, LoanForm, RepaymentForm, AdminLoanForm, AdminUserForm
from .models import Loan, Profile, Repayment

def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}!')
            return redirect('login')
    else:
        form = UserRegisterForm()
    return render(request, 'core/register.html', {'form': form})

def register_admin(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_staff = True
            user.is_superuser = True
            user.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Admin account created for {username}!')
            return redirect('login')
    else:
        form = UserRegisterForm()
    return render(request, 'core/register_admin.html', {'form': form})

@login_required
def dashboard(request):
    # Ensure profile exists (handle cases where it might not)
    profile, created = Profile.objects.get_or_create(user=request.user)
    
    active_loan = Loan.objects.filter(borrower=request.user, status='Active').first()
    pending_loan = Loan.objects.filter(borrower=request.user, status='Pending').first()
    
    context = {
        'profile': profile,
        'active_loan': active_loan,
        'pending_loan': pending_loan,
    }
    return render(request, 'core/dashboard.html', context)

@login_required
def verify_profile(request):
    profile, created = Profile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=profile)
        if form.is_valid():
            prof = form.save(commit=False)
            prof.verified_status = True  # Simulate auto-verification
            prof.save()
            messages.success(request, 'Profile verified successfully!')
            return redirect('dashboard')
    else:
        form = ProfileForm(instance=profile)
    
    return render(request, 'core/verify.html', {'form': form})

@login_required
def apply_loan(request):
    profile, created = Profile.objects.get_or_create(user=request.user)
    
    if not profile.verified_status:
        messages.warning(request, 'You must verify your profile first.')
        return redirect('verify_profile')
    
    # prevent multiple active/pending loans
    if Loan.objects.filter(borrower=request.user, status__in=['Active', 'Pending']).exists():
         messages.info(request, 'You already have an active or pending loan.')
         return redirect('dashboard')

    if request.method == 'POST':
        form = LoanForm(request.POST)
        if form.is_valid():
            loan = form.save(commit=False)
            loan.borrower = request.user
            
            # Simple Logic
            if loan.amount < 1000:
                loan.status = 'Active'
                messages.success(request, 'Loan auto-approved!')
            else:
                loan.status = 'Pending'
                messages.info(request, 'Loan request submitted for review.')
            
            loan.save()
            return redirect('dashboard')
    else:
        form = LoanForm()
        
    return render(request, 'core/apply.html', {'form': form})

@login_required
def repay_loan(request):
    active_loan = Loan.objects.filter(borrower=request.user, status='Active').first()
    
    if not active_loan:
        messages.info(request, 'No active loan to repay.')
        return redirect('dashboard')
        
    if request.method == 'POST':
        form = RepaymentForm(request.POST)
        if form.is_valid():
            repayment = form.save(commit=False)
            repayment.loan = active_loan
            repayment.save()
            
            # Check balance
            if active_loan.balance <= 0:
                active_loan.status = 'Paid'
                active_loan.save()
                messages.success(request, 'Loan fully paid! Congratulations.')
            else:
                messages.success(request, f'Repayment of {repayment.amount} accepted.')
                
            return redirect('dashboard')
    else:
        form = RepaymentForm()
        
    return render(request, 'core/repay.html', {'form': form, 'loan': active_loan})

def admin_login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        
        if user and user.is_staff:
            login(request, user)
            return redirect('admin_dashboard')
        else:
            messages.error(request, 'Invalid credentials or insufficient permissions')
    
    return render(request, 'core/admin_login.html')

def admin_register_view(request):
    if request.method == 'POST':
        form = AdminUserForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_staff = True
            user.is_superuser = True
            user.save()
            Profile.objects.create(user=user, verified_status=True)
            messages.success(request, f'Admin account created for {user.username}!')
            return redirect('admin_login')
    else:
        form = AdminUserForm()
    return render(request, 'core/admin_register.html', {'form': form})

from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Sum, Count
from django.http import HttpResponseRedirect
from django.urls import reverse

@staff_member_required
def admin_dashboard(request):
    # Debug: Print to verify this view is being called
    print(f"Admin dashboard accessed by: {request.user.username}")
    
    # Stats
    total_users = Profile.objects.count()
    active_loans_count = Loan.objects.filter(status='Active').count()
    pending_loans_count = Loan.objects.filter(status='Pending').count()
    total_repaid = Repayment.objects.aggregate(Sum('amount'))['amount__sum'] or 0
    
    # Lists
    pending_loans = Loan.objects.filter(status='Pending').order_by('-created_at')
    recent_repayments = Repayment.objects.select_related('loan__borrower').order_by('-date')[:10]
    
    context = {
        'total_users': total_users,
        'active_loans_count': active_loans_count,
        'pending_loans_count': pending_loans_count,
        'total_repaid': total_repaid,
        'pending_loans': pending_loans,
        'recent_repayments': recent_repayments,
    }
    return render(request, 'core/admin_dashboard.html', context)

@staff_member_required
def approve_loan(request, pk):
    loan = get_object_or_404(Loan, pk=pk)
    if loan.status == 'Pending':
        loan.status = 'Active'
        loan.save()
        messages.success(request, f"Loan {loan.id} approved.")
    return redirect('admin_dashboard')

@staff_member_required
def reject_loan(request, pk):
    loan = get_object_or_404(Loan, pk=pk)
    if loan.status == 'Pending':
        loan.status = 'Rejected'
        loan.save()
        messages.warning(request, f"Loan {loan.id} rejected.")
    return redirect('admin_dashboard')

@staff_member_required
def admin_users(request):
    profiles = Profile.objects.select_related('user').all()
    return render(request, 'core/admin_users.html', {'profiles': profiles})

@staff_member_required
def verify_user_admin(request, pk):
    user = get_object_or_404(User, pk=pk)
    profile, created = Profile.objects.get_or_create(user=user)
    profile.verified_status = True
    profile.save()
    messages.success(request, f"User {user.username} verified.")
    return redirect('admin_users')

@staff_member_required
def admin_loans(request):
    status = request.GET.get('status')
    loans = Loan.objects.select_related('borrower').all().order_by('-created_at')
    
    if status:
        loans = loans.filter(status=status)
        
    return render(request, 'core/admin_loans.html', {
        'loans': loans,
        'current_status': status
    })

@staff_member_required
def admin_create_loan(request):
    if request.method == 'POST':
        form = AdminLoanForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Loan created successfully!')
            return redirect('admin_loans')
    else:
        form = AdminLoanForm()
    return render(request, 'core/admin_create_loan.html', {'form': form})

@staff_member_required
def admin_create_user(request):
    if request.method == 'POST':
        form = AdminUserForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            if form.cleaned_data['is_staff']:
                user.is_staff = True
                user.is_superuser = True
            user.save()
            Profile.objects.create(user=user, verified_status=True)
            messages.success(request, f'User {user.username} created successfully!')
            return redirect('admin_users')
    else:
        form = AdminUserForm()
    return render(request, 'core/admin_create_user.html', {'form': form})