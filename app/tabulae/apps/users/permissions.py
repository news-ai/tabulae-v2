# -*- coding: utf-8 -*-
# Third-party app imports
from rest_framework import permissions
from rest_framework.permissions import BasePermission


class IsAdminOrIsSelf(BasePermission):

    def has_object_permission(self, request, view, obj):
        return (obj.pk == request.user.pk or
                request.user.is_staff, request.user.is_superuser)


class UserPermission(permissions.BasePermission):

    def has_permission(self, request, view):
        if request.user and request.user.is_authenticated():
            return True
        return False

    def has_object_permission(self, request, view, obj):
        if request.user and request.user.is_authenticated():
            if obj.pk == request.user.pk:
                return True
        return False


class AgencyPermission(permissions.BasePermission):

    def has_permission(self, request, view):
        if request.method == 'DELETE':
            return False
        return True


class ClientPermission(permissions.BasePermission):

    def has_permission(self, request, view):
        if request.method == 'DELETE':
            return False
        return True


class TeamPermission(permissions.BasePermission):

    def has_permission(self, request, view):
        if request.method == 'DELETE':
            return False
        return True


class InvitePermission(permissions.BasePermission):

    def has_permission(self, request, view):
        if request.method == 'DELETE':
            return False
        return True
