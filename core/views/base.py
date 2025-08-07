from django.contrib.auth.mixins import UserPassesTestMixin


class RoleRequiredMixin(UserPassesTestMixin):
    """Mixin to require specific user roles"""
    required_role = None

    def test_func(self):
        if not self.request.user.is_authenticated:
            return False
        if not hasattr(self.request.user, 'userprofile'):
            return False
        return self.request.user.userprofile.role == self.required_role


class ClientRequiredMixin(RoleRequiredMixin):
    """Mixin to require client role"""
    required_role = 'client'


class EmployeeRequiredMixin(RoleRequiredMixin):
    """Mixin to require employee role"""
    required_role = 'employee'


class ManagerRequiredMixin(RoleRequiredMixin):
    """Mixin to require manager role"""
    required_role = 'manager'


def is_manager(user):
    """Helper function to check if user is a manager"""
    return (
        user.is_authenticated and
        hasattr(user, 'userprofile') and
        user.userprofile.role == 'manager'
    )


def is_client(user):
    """Helper function to check if user is a client"""
    return (
        user.is_authenticated and
        hasattr(user, 'userprofile') and
        user.userprofile.role == 'client'
    )


def is_employee(user):
    """Helper function to check if user is an employee"""
    return (
        user.is_authenticated and
        hasattr(user, 'userprofile') and
        user.userprofile.role == 'employee'
    )
