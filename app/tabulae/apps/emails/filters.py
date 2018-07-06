# -*- coding: utf-8 -*-
from datetime import datetime, timedelta, time

# Third-party app imports
from rest_framework.filters import BaseFilterBackend

from .models import Email


class FilterBetweenField(BaseFilterBackend):

    def filter_queryset(self, request, queryset, view):
        # Values
        _date = request.GET.get('date')
        if _date and _date != '':
            now = datetime.strptime(_date, '%Y-%m-%d')
            tomorrow = now + timedelta(1)
            today_start = datetime.combine(now, time())
            today_end = datetime.combine(tomorrow, time())

            # Contains
            lte = view.filter_field + '__lte'
            gte = view.filter_field + '__gte'

            _min = today_start
            _max = today_end

            # Query
            if _min and _max:
                return queryset.filter(**{gte: _min, lte: _max})
        return queryset
