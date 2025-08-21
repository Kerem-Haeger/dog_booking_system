from django.contrib import admin
from .models import (
    UserProfile,
    PetProfile,
    Service,
    ServicePrice,
    Appointment,
    EmployeeCalendar,
    TimeOffRequest,
    Voucher
)


# Register models for the admin interface
admin.site.register(UserProfile)
admin.site.register(EmployeeCalendar)
admin.site.register(ServicePrice)


class PetProfileAdmin(admin.ModelAdmin):
    """ Define which fields should appear in the list view in the admin """
    list_display = (
        'name',
        'user',
        'breed',
        'size',
        'profile_status',
        'created_at',
    )
    # Define which fields should be searchable in the admin interface
    search_fields = ['name', 'user__username']
    # Add filters to make it easier to filter the pet profiles
    list_filter = ('profile_status', 'size')
    # Display the verified_at timestamp
    readonly_fields = ('verified_at',)


admin.site.register(PetProfile, PetProfileAdmin)


class AppointmentAdmin(admin.ModelAdmin):
    """ Define which fields should appear in the list view in the admin """
    list_display = (
        'pet_profile',
        'service',
        'appointment_time',
        'employee',
        'status',
        'created_at'
        )

    # Add filters to filter by status or service
    list_filter = ('status', 'service')


admin.site.register(Appointment, AppointmentAdmin)  # Register Appointment with the customized admin


class TimeOffRequestAdmin(admin.ModelAdmin):
    """ Define which fields should appear in the list view in the admin """
    list_display = ('user_profile', 'start_time', 'end_time', 'status', 'requested_at', 'approved')
    list_filter = ('status', 'user_profile')


admin.site.register(TimeOffRequest, TimeOffRequestAdmin)


class VoucherAdmin(admin.ModelAdmin):
    """ Define which fields should appear in the list view in the admin """
    list_display = (
        'code',
        'discount_percentage',
        'expiry_date',
        'is_redeemed',
        'used_by_user',
        'created_at'
        )

    # Add filters to filter by is_redeemed
    list_filter = ('is_redeemed',)


admin.site.register(Voucher, VoucherAdmin)  # Register Voucher with the customized admin


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    """ Define which fields should appear in the list view in the admin """
    list_display = ('name', 'duration', 'slot_interval')
    list_filter = ('slot_interval',)
