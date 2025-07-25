from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User


# UserProfile model (used for roles)
class UserProfile(models.Model):
    USER_ROLES = [
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
    size = models.CharField(max_length=10, choices=SIZE_CHOICES)
    grooming_preferences = models.TextField(null=True, blank=True)
    date_of_birth = models.DateField()
    profile_status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='pending'
    )
    verified_at = models.DateTimeField(null=True, blank=True)  # Timestamp for verification
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


# Service model (simplified grooming services)
class Service(models.Model):
    name = models.CharField(max_length=100)  # E.g., Wash Only, Wash and Groom
    description = models.TextField(null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    duration = models.DurationField()  # Duration of the service

    def __str__(self):
        return self.name


# Appointment model (for booking)
class Appointment(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
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
        unique_together = ('pet_profile', 'appointment_time')  # Prevent double-booking

    def __str__(self):
        return f"{self.pet_profile.name} - {self.service.name} at {self.appointment_time}"


# Employee calendar (for tracking appointments per employee)
class EmployeeCalendar(models.Model):
    user_profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE, null=True)
    appointment = models.ForeignKey(Appointment, on_delete=models.CASCADE)
    scheduled_time = models.DateTimeField()
    available_time = models.BooleanField(default=True)
    unavailability_reason = models.CharField(max_length=100, null=True, blank=True)  # Reason for unavailability
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user_profile.user.username} - {self.appointment.pet_profile.name} at {self.scheduled_time}"


# Employee Time-Off Requests (pending approval for more than 1 hour)
class TimeOffRequest(models.Model):
    user_profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE, null=True)
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
    used_by_user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)  # Track who redeemed it
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.code

    def is_valid(self):
        # Check if the voucher is valid (not expired and not redeemed)
        return not self.is_redeemed and self.expiry_date >= timezone.now().date()
