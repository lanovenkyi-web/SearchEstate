from rest_framework import permissions
from .models import User


# OopCompanion:suppressRename


class IsAdminUser(permissions.BasePermission):

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.is_admin()


class IsLandlordUser(permissions.BasePermission):

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.is_landlord()


class IsTenantUser(permissions.BasePermission):

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.is_tenant()


class IsAdminOrLandlord(permissions.BasePermission):

    def has_permission(self, request, view):
        return (request.user and request.user.is_authenticated and 
                (request.user.is_admin() or request.user.is_landlord()))


class IsAdminOrOwner(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        return (request.user and request.user.is_authenticated and 
                (request.user.is_admin() or getattr(obj, 'user', None) == request.user))


class IsOwnerOrReadOnly(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return (request.user and request.user.is_authenticated and 
                getattr(obj, 'user', None) == request.user)
