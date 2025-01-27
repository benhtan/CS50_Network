
from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("user/<str:username>", views.user_profile, name="user"),
    path("follow_unfollow", views.follow_unfollow, name="follow_unfollow"),
    path("following", views.following, name="following"),
    path("edit_save", views.edit_save, name="edit_save"),
    path("like_unlike", views.like_unlike, name="like_unlike"),
]
