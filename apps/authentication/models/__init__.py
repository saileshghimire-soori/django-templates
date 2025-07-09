from .roles_permissions import CustomPermission, PermissionCategory, Roles
from .user import CustomUser

User = CustomUser
__all__ = [
    "CustomPermission",
    "PermissionCategory",
    "Roles",
    "CustomUser",
]
