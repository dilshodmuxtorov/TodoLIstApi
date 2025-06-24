from django.urls import path


from .views import LoginView, MyInfoView, UserCreateView, VerifyUserView


urlpatterns = [
    path("login/", LoginView.as_view()),
    path("myinfo/", MyInfoView.as_view()),
    path("create/", UserCreateView.as_view()),
    path("verify/", VerifyUserView.as_view()),
]
