from django.contrib import admin
from .models import Profile, Loan, Repayment

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'national_id', 'phone_number', 'monthly_income', 'verified_status')
    list_filter = ('verified_status',)
    search_fields = ('user__username', 'national_id', 'phone_number')

@admin.register(Loan)
class LoanAdmin(admin.ModelAdmin):
    list_display = ('id', 'borrower', 'amount', 'status', 'created_at', 'due_date')
    list_filter = ('status', 'created_at')
    search_fields = ('borrower__username',)

@admin.register(Repayment)
class RepaymentAdmin(admin.ModelAdmin):
    list_display = ('loan', 'amount', 'date')
    list_filter = ('date',)
