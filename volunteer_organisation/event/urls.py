from django.urls import path

from . import views

app_name = "event"

urlpatterns = [
    path('', views.index, name = "index"),
    path('<int:event_id>/details', views.details, name = "details"),
    path('addevent', views.add_event, name = "add"),
    path('addeventcategory', views.add_eventcategory, name = "add_category"),
]
