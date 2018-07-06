# -*- coding: utf-8 -*-
# Third-party app imports
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response


def get_pagination(request):
    limit = request.GET.get('limit', 20)
    offset = request.GET.get('offset', 0)

    return (limit, offset)


class GlobalPagination(LimitOffsetPagination):

    def get_paginated_response(self, data, included=[]):
        current_count = self.get_limit(self.request)
        total = self.count
        if total < current_count:
            current_count = total

        return Response({
            'paging': {
                'next': self.get_next_link(),
                'previous': self.get_previous_link(),
                'cursors': {
                    'before': '',
                        'after': '',
                        },
            },
            'count': len(data),
            'summary': {
                'total': total,
            },
            'data': data,
            'included': included,
        })
