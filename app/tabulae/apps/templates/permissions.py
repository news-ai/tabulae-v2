# -*- coding: utf-8 -*-
# Third-party app imports
from rest_framework import permissions


class TemplatePermission(permissions.BasePermission):

    def has_permission(self, request, view):
        # If user is only trying to do GET, HEAD, or OPTIONS
        if request.method == 'DELETE':
            return False
        # If user is admin then let user POST/etc.
        return True
