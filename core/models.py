from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    national_id = models.CharField(max_length=20, null=True, blank=True)
    phone_number = models.CharField(max_length=15, null=True, blank=True)
    monthly_income = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    verified_status = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username}'s Profile"

class Loan(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Active', 'Active'),
        ('Paid', 'Paid'),
        ('Rejected', 'Rejected'),
    ]

    borrower = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    term_days = models.IntegerField(help_text="Term in days")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Pending')
    created_at = models.DateTimeField(auto_now_add=True)
    due_date = models.DateField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.id and not self.due_date and self.term_days:
            self.due_date = timezone.now().date() + timedelta(days=self.term_days)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Loan {self.id} - {self.borrower.username} - {self.status}"

    @property
    def total_repaid(self):
        return self.repayments.aggregate(total=models.Sum('amount'))['total'] or 0
    
    @property
    def balance(self):
        return self.amount - self.total_repaid

class Repayment(models.Model):
    loan = models.ForeignKey(Loan, related_name='repayments', on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Repayment of {self.amount} for Loan {self.loan.id}"
