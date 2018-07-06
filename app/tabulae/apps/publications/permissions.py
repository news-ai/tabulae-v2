# -*- coding: utf-8 -*-
# Third-party app imports
from rest_framework import permissions


class PublicationPermission(permissions.BasePermission):

    def has_permission(self, request, view):
        # If user is only trying to do GET, HEAD, or OPTIONS
        if request.method in permissions.SAFE_METHODS:
            return True
        elif request.method == 'DELETE':
            return False
        # If user is admin then let user POST/etc.
        return True
