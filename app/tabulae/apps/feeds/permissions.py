# -*- coding: utf-8 -*-
# Third-party app imports
from rest_framework import permissions


class FeedPermission(permissions.BasePermission):

    def has_permission(self, request, view):
        return True
