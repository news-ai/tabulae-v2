# -*- coding: utf-8 -*-
# Third-party app imports
from rest_framework import permissions


class MediaListPermission(permissions.BasePermission):

    def has_permission(self, request, view):
        return True
