from django.urls import path

from . import views

app_name = "event"

urlpatterns = [
    path('', views.index, name = "index"),
    path('<int:event_id>/details', views.details, name = "details"),

    path('addevent', views.add_event, name = "add"),
    path('addeventcategory', views.add_eventcategory, name = "add_category"),
    path('addtask', views.add_task, name="add_task"),
    path('addexpense', views.add_expense, name="add_expense"),
    path('addteam', views.add_team, name="add_team"),
    path('<int:event_id>/join', views.join_event, name="join_event"),
]
