from rest_framework.permissions import BasePermission

from .models import Role


class HasRole(BasePermission):
    """
    Factory-style DRF permission gating a view to users holding one of the
    given role codes (see TS section 8 role/permission matrix).

    Usage: permission_classes = [HasRole(Role.CHIEF_EDITOR, Role.TECH_EDITOR)]
    """

    def __init__(self, *role_codes: str):
        self.role_codes = role_codes

    def __call__(self):
        # DRF instantiates permission_classes entries; returning self lets
        # this be used both as a class-style and parametrized permission.
        return self

    def has_permission(self, request, view):
        user = request.user
        if not (user and user.is_authenticated):
            return False
        if not self.role_codes:
            return True
        return user.roles.filter(code__in=self.role_codes).exists()
