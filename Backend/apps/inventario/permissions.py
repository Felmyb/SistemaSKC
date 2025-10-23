from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsStaffOnly(BasePermission):
    """Allow access only to staff users for all methods.

    Inventory data is sensitive; restrict entirely to staff/admin.
    """

    def has_permission(self, request, view):
        user = request.user
        return bool(
            user and user.is_authenticated and (getattr(user, 'role', None) in ['STAFF', 'ADMIN'] or user.is_staff)
        )
