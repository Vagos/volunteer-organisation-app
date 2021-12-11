from django.db import models
from django.utils import timezone
import datetime

import member
#from volunteer.models import Team
# Create your models here.

class Employee(member.models.Member):

    compensation = models.PositiveIntegerField()
    position_name = models.CharField(max_length = 200)

    def __str__(self):
        return "Name: {} Surname: {}  ".format(self.name, self.surname)

class Management(models.Model):

    start_date = models.DateField()
    end_date = models.DateField()
    employee_id = models.ForeignKey('Employee', on_delete = models.CASCADE)
    #team_name   = models.ForeignKey('Team', on_delete = models.CASCADE)

    def __str__(self):
        return "Manager ID: {}  ".format(self.employee_id)

class EventOrganisation(models.Model):

    reason = models.CharField(max_length = 30)
    entry_date = models.DateField()
    event_id = models.ForeignKey('Event', on_delete = models.CASCADE)
    organiser_id = models.ForeignKey('Employee', on_delete = models.CASCADE)

    def __str__(self):
        return "Event ID: {} ".format(self.event_id)

class EventCategory(models.Model):

    category_name = models.CharField(max_length=20, unique = True)

    def __str__(self):
        return "Category Name: {}".format(self.category_name)

class EventParticipation(models.Model):

    date = models.DateField()
    member_id = models.ForeignKey(member.models.Member, on_delete = models.CASCADE)
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
