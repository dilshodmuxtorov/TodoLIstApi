from django.urls import path


from .views import (
    TodoListView,
    TodoRetrieveView,
    IsFinishedSetTrueView,
    TodoCreateView,
    DeleteApiView,
    EditTodoApiView,
)

urlpatterns = [
    path("todolist/", TodoListView.as_view()),
    path("todolist/<int:pk>/", TodoRetrieveView.as_view()),
    path("<int:pk>/finish/", IsFinishedSetTrueView.as_view()),
    path("create/", TodoCreateView.as_view()),
    path("<int:pk>/delete/", DeleteApiView.as_view()),
    path("<int:pk>/edit/", EditTodoApiView.as_view()),
]
