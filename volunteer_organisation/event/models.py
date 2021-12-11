from django.db import models
from django.utils import timezone
import datetime

# Event Models

class EventCategory(models.Model):

    category_name = models.CharField(max_length=20, unique = True)

    def __str__(self):
        return "Category Name: {}".format(self.category_name)

class EventParticipation(models.Model):

    date = models.DateField()
    member_id = models.ForeignKey('member.Member', on_delete = models.CASCADE)
    duration = models.DateTimeField(blank=True, default='')
    impressions = models.CharField(max_length =200, blank=True, default='')
    event_id = models.ForeignKey('Event', on_delete = models.CASCADE)

    def __str__(self):
        pass


class Event(models.Model):

    #event_participation = models.ManyToManyField('Member', through = 'EventParticipation')
    #event_organisation = models.ManyToManyField('Employee', through = 'EventOrganisation')

    name = models.CharField(max_length = 20)
    start_date = models.DateField()
    end_date = models.DateField()
    place = models.CharField(max_length=20)
    description = models.CharField(max_length = 200)
    category = models.ForeignKey('EventCategory', on_delete = models.CASCADE)

    def __str__(self):
        return "Event Name: {}". format(self.name)
