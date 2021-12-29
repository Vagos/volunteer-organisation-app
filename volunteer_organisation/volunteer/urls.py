from django.urls import path

from . import views

app_name = "volunteer"

urlpatterns = [
    path('', views.index, name = "index"),
    path("team/<str:team_name>/", views.team, name = "team")
]
