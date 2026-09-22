from rest_framework import serializers
from materials.models import Course, Lesson
from materials.validators import validate_youtube_link


class LessonSerializer(serializers.ModelSerializer):
    # Добавляем валидатор на поле видео
    video_link = serializers.CharField(validators=[validate_youtube_link], required=False, allow_blank=True)

    class Meta:
        model = Lesson
        fields = "__all__"


class CourseSerializer(serializers.ModelSerializer):
    # Задание 1: Поле для подсчета количества уроков
    lessons_count = serializers.SerializerMethodField()
    # Задание 3: Вывод уроков через сериализатор связанной модели
    lessons = LessonSerializer(many=True, read_only=True)

    class Meta:
        model = Course
        fields = ['id', 'title', 'preview', 'description', 'lessons_count', 'lessons']

    def get_lessons_count(self, obj):
        return obj.lessons.count()  # Считаем количество уроков, связанных с курсом
