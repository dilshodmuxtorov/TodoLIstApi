import datetime
from django.db import models


from users.models import UserModel


class TodoModel(models.Model):
    title = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    deadline = models.DateTimeField(default=datetime.datetime.now)
    is_finished = models.BooleanField(default=False)
    is_urgent = models.BooleanField(default=False)
    user_id = models.ForeignKey(UserModel, on_delete=models.CASCADE)

    class Meta:
        db_table = "todos"
        verbose_name = "Todo"
        verbose_name_plural = "Todolar"

    def __str__(self):
        return self.title
