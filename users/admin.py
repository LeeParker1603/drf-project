from django.contrib import admin

from django.contrib import admin
from django.contrib.auth import get_user_model

User = get_user_model()


@admin.register(User)
class CustomUserAdmin(admin.ModelAdmin):
    # Автоматически берем ВСЕ поля, которые есть в модели
    list_display = [field.name for field in User._meta.fields]

    # Добавляем возможность кликнуть на любое поле для перехода к редактированию
    list_display_links = [field.name for field in User._meta.fields if field.name != 'password']

    # Добавляем поиск по ключевым текстовым полям
    search_fields = ('username', 'email', 'first_name', 'last_name')
