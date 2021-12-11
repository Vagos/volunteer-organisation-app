from django.db import models
from django.utils import timezone
import datetime

# Event Models

class EventCategory(models.Model):

    category_name = models.CharField(max_length=20, unique = True)

    def __str__(self):
        return "Category Name: {}".format(self.category_name)

class Event(models.Model):

    name = models.CharField(max_length = 20)

    start_date = models.DateField()
    end_date = models.DateField()
    
    place = models.CharField(max_length=20)
    description = models.CharField(max_length = 200)
    category = models.ForeignKey('EventCategory', on_delete = models.CASCADE)

    def __str__(self):
        return "Event Name: {}". format(self.name)
