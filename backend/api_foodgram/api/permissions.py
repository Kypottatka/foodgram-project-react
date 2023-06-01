from django.core.handlers.wsgi import WSGIRequest
from django.db.models import Model
from rest_framework.permissions import SAFE_METHODS, BasePermission


class BanPermission(BasePermission):
    def has_permission(
        self,
        request: WSGIRequest,
        view
    ) -> bool:
        return bool(
            request.method in SAFE_METHODS
            or request.user.is_authenticated
            and request.user.is_active
        )


class AuthorStaffOrReadOnly(BanPermission):
    def has_object_permission(
        self,
        request: WSGIRequest,
        view,
        obj: Model
    ) -> bool:
        return (
            request.method in SAFE_METHODS
            and request.user.is_active
            and (
                request.user == obj.author
                or request.user.is_staff
            )
        )


class AdminOrReadOnly(BanPermission):
    def has_object_permission(
        self,
        request: WSGIRequest,
        view
    ) -> bool:
        return (
            request.method in SAFE_METHODS
            or request.user.is_authenticated
            and request.user.is_active
            and request.user.is_staff
        )


class OwnerUserOrReadOnly(BanPermission):
    def has_object_permission(
        self,
        request: WSGIRequest,
        view,
        obj: Model
    ) -> bool:
        return (
            request.method in SAFE_METHODS
            or request.user.is_authenticated
            and request.user.is_active
            and request.user == obj.author
            or request.user.is_staff
        )
