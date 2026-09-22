from rest_framework.pagination import PageNumberPagination

class CustomPagination(PageNumberPagination):
    page_size = 5  # Количество элементов на страницу по умолчанию
    page_size_query_param = 'page_size'  # Параметр в URL для кастомного размера страницы
    max_page_size = 50  # Максимально разрешенный размер страницы