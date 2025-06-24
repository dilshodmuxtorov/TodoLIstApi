from django.contrib import admin


from .models import TodoModel


class TodoModelAdmin(admin.ModelAdmin):
    list_display = ["title", "user_id", "deadline", "id", "is_finished"]


admin.site.register(TodoModel, TodoModelAdmin)
