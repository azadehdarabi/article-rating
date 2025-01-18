from rest_framework.pagination import CursorPagination, PageNumberPagination
from rest_framework.response import Response


class BasePaginator(CursorPagination):
    ordering = ['-created_at']


class CustomPageNumberPagination(PageNumberPagination, BasePaginator):
    page_size_query_param = 'page_size'
    page_query_param = 'page'

    def get_paginated_response(self, data):
        return Response({
            'links': {
                'next': self.get_next_link(),
                'previous': self.get_previous_link()
            },
            'count': self.page.paginator.count,
            'total_pages': self.page.paginator.num_pages,
            'results': data
        })


class ResponsePaginator(CustomPageNumberPagination):
    page_size = 12
    max_page_size = 20
