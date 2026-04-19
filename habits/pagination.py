# habits/pagination.py
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class HabitPagination(PageNumberPagination):
    """
    Пагинация для списка привычек.
    Выводит 5 привычек на страницу.
    """

    # Количество элементов на странице
    page_size = 5

    # Параметр запроса для изменения размера страницы
    page_size_query_param = 'page_size'

    # Максимальный размер страницы (защита от перегрузки)
    max_page_size = 100

    # Параметр запроса для номера страницы
    page_query_param = 'page'  # ?page=2

    def get_paginated_response(self, data):
        """
        Кастомизируем ответ пагинации.
        Добавляем дополнительную информацию.
        """
        return Response({
            # Ссылки на下一页 и предыдущую страницу
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),

            # Общее количество элементов
            'count': self.page.paginator.count,

            # Количество страниц
            'total_pages': self.page.paginator.num_pages,

            # Текущая страница
            'current_page': self.page.number,

            # Есть ли следующая страница
            'has_next': self.page.has_next(),

            # Есть ли предыдущая страница
            'has_previous': self.page.has_previous(),

            # Результаты на текущей странице
            'results': data
        })
