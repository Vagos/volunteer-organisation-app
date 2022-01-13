from django.urls import path

from . import views

app_name = "member"

urlpatterns = [
    path('', views.index, name = "index"),
    path('join', views.join, name = "join"),

    path('login', views.login, name = "login"),
    path('support', views.support, name="support"),
    path('support_add', views.support_add, name="support_add"),
]
