from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
import json


class AuditLog(models.Model):
    """Track important actions for security and compliance"""
    ACTION_CHOICES = [
        ('pet_approved', 'Pet Approved'),
        ('pet_rejected', 'Pet Rejected'),
        ('appointment_approved', 'Appointment Approved'),
        ('appointment_rejected', 'Appointment Rejected'),
        ('appointment_reassigned', 'Appointment Reassigned'),
        ('appointment_cancelled', 'Appointment Cancelled'),
        ('login_attempt', 'Login Attempt'),
    ]
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        help_text="User who performed the action"
    )
    target_user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='audit_target',
        help_text="User affected by the action (if applicable)"
    )
    action = models.CharField(max_length=50, choices=ACTION_CHOICES)
    details = models.JSONField(
        default=dict,
        help_text="Additional details about the action"
    )
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['action', 'timestamp']),
            models.Index(fields=['user', 'timestamp']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.action} at {self.timestamp}"


# UserProfile model (used for roles)
class UserProfile(models.Model):
    USER_ROLES = [
        ('pending', 'Pending Approval'),
        ('client', 'Client'),
        ('employee', 'Employee'),
        ('manager', 'Manager'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=10, choices=USER_ROLES)
    start_date = models.DateField(null=True, blank=True)  # Only for employees
    salary = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user.username


# Pet Profile model (linked to client)
class PetProfile(models.Model):
    SIZE_CHOICES = [
        ('small', 'Small'),
        ('medium', 'Medium'),
        ('large', 'Large'),
    ]
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('verified', 'Verified'),
        ('rejected', 'Rejected'),
    ]
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="pets"
    )
    name = models.CharField(max_length=100)
    breed = models.CharField(max_length=100)
    size = models.CharField(
                            max_length=10,
                            choices=SIZE_CHOICES,
                            null=True,
                            blank=True
                            )
    grooming_preferences = models.TextField(null=True, blank=True)
    date_of_birth = models.DateField()
    profile_status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='pending'
    )
    verified_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


# Service model (simplified grooming services)
class Service(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)
    duration = models.DurationField()
    slot_interval = models.PositiveIntegerField(
        default=30,
        help_text="Interval between available start times (in minutes)."
    )
    allowed_start_times = models.CharField(
        max_length=200,
        help_text="Comma-separated start times (e.g., '09:00,11:30,14:00')",
        default=""
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this service is currently available for booking"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def get_allowed_times(self):
        return [t.strip() for t in self.allowed_start_times.split(",")]

    def __str__(self):
        return self.name

    def get_price_for_size(self, size):
        return self.prices.get(size=size).price


# Model for pricing
class ServicePrice(models.Model):
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name="prices")
    size = models.CharField(choices=[('small', 'Small'), ('medium', 'Medium'), ('large', 'Large')], max_length=10)
    price = models.DecimalField(max_digits=6, decimal_places=2)

    class Meta:
        unique_together = ('service', 'size')


# Appointment model (for booking)
class Appointment(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('completed', 'Completed'),
        ('canceled', 'Canceled'),
    ]
    pet_profile = models.ForeignKey(
        PetProfile,
        on_delete=models.CASCADE,
        null=True
    )
    service = models.ForeignKey(Service, on_delete=models.CASCADE, null=True)
    appointment_time = models.DateTimeField()  # Appointment date and time
    employee = models.ForeignKey(
        UserProfile,
        on_delete=models.SET_NULL,
        null=True,
        limit_choices_to={'role': 'employee'}
    )
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='pending'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        # Prevent double-booking
        unique_together = ('pet_profile', 'appointment_time')

    def __str__(self):
        return f"{self.pet_profile.name} - {self.service.name} at {self.appointment_time}"
    
    def get_end_time(self):
        """Calculate the end time of this appointment based on service duration"""
        if self.service and self.service.duration:
            return self.appointment_time + self.service.duration
        return self.appointment_time  # Fallback if no duration is set


# Employee calendar (for tracking appointments per employee)
class EmployeeCalendar(models.Model):
    user_profile = models.ForeignKey(
        UserProfile,
        on_delete=models.CASCADE,
        null=True
        )
    appointment = models.ForeignKey(Appointment, on_delete=models.CASCADE)
    scheduled_time = models.DateTimeField()
    available_time = models.BooleanField(default=True)
    unavailability_reason = models.CharField(
        max_length=100,
        null=True,
        blank=True
        )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user_profile.user.username} - {self.appointment.pet_profile.name} at {self.scheduled_time}"


# Employee Time-Off Requests (pending approval for more than 1 hour)
class TimeOffRequest(models.Model):
    user_profile = models.ForeignKey(
        UserProfile,
        on_delete=models.CASCADE,
        null=True
        )
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    approved = models.BooleanField(default=False)  # Approval status
    status = models.CharField(max_length=10, choices=[
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected')
    ], default='pending')  # Time off request status
    requested_at = models.DateTimeField(auto_now_add=True)

    def duration(self):
        return self.end_time - self.start_time  # Returns a timedelta object

    def __str__(self):
        return f"{self.user_profile.user.username} - Time Off Request"


class Voucher(models.Model):
    code = models.CharField(max_length=10, unique=True)  # Unique voucher code
    discount_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=10
    )  # Discount value, e.g., 10%
    expiry_date = models.DateField()  # Expiry date for the voucher
    is_redeemed = models.BooleanField(default=False)
    used_by_user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
        )  # Track who redeemed it
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.code

    def is_valid(self):
        # Check if the voucher is valid (not expired and not redeemed)
        return not self.is_redeemed and self.expiry_date >= timezone.now().date()
