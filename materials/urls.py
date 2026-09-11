from django.urls import path
from rest_framework.routers import SimpleRouter
from materials.apps import MaterialsConfig
from materials.views import (CourseViewSet, LessonCreateAPIView, LessonListAPIView,
                             LessonRetrieveAPIView, LessonUpdateAPIView, LessonDestroyAPIView)

app_name = MaterialsConfig.name

# Роутер автоматически создаст пути только для курсов: /materials/courses/
router = SimpleRouter()
router.register('', CourseViewSet)

urlpatterns = [
    # Раздельные эндпоинты для Generic-классов уроков
    path('lessons/create/', LessonCreateAPIView.as_view(), name='lesson-create'),
    path('lessons/', LessonListAPIView.as_view(), name='lesson-list'),
    path('lessons/<int:pk>/', LessonRetrieveAPIView.as_view(), name='lesson-get'),
    path('lessons/update/<int:pk>/', LessonUpdateAPIView.as_view(), name='lesson-update'),
    path('lessons/delete/<int:pk>/', LessonDestroyAPIView.as_view(), name='lesson-delete'),
] + router.urls