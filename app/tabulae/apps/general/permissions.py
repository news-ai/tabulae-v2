# -*- coding: utf-8 -*-
# Third-party app imports
from rest_framework.permissions import BasePermission


class IsAdminOrIsSelf(BasePermission):

    def has_object_permission(self, request, view, obj):
        return obj.created_by == request.user or request.user.is_staff, request.user.is_superuser
