from django.db import models
from django.utils import timezone
import datetime

from member.models import Member

# Volunteer Models

class Volunteer(Member):

    join_date = models.DateField(max_length = 200)

    def __str__(self):
        return "Name: {} Surname: {} (Volunteer)".format( self.name, self.surname )

class TeamParticipation(models.Model):

    start_date = models.DateField()
    end_date = models.DateField()
    volunteer_id = models.ForeignKey('Volunteer', on_delete = models.CASCADE)
    team_name = models.ForeignKey('Team', on_delete = models.CASCADE)

    def __str__(self):
        return "ID: {}, Team Name: {}".format(self.volunteer_id, self.team_name)

class Employee(Member):

    compensation = models.PositiveIntegerField()
    position_name = models.CharField(max_length = 200)

    def __str__(self):
        return "Name: {} Surname: {}  ".format(self.name, self.surname)

class Management(models.Model):

    start_date = models.DateField()
    end_date = models.DateField()
    employee_id = models.ForeignKey('Employee', on_delete = models.CASCADE)
    team_name   = models.ForeignKey('Team', on_delete = models.CASCADE)

    def __str__(self):
        return "Manager ID: {}  ".format(self.employee_id)


class Team(models.Model):

    team_participation = models.ManyToManyField('Volunteer', through = 'Participation')
    team_management = models.ManyToManyField('Employee', through = 'Management')

    name = models.CharField(max_length = 200, unique = True)
    description = models.CharField(max_length = 300)

    def __str__(self):
        return "Team Name: {}".format(self.name)

class WorksOn(models.Model):

    evaluation = models.CharField(max_length = 300)
    volunteer_id = models.ForeignKey('Volunteer', on_delete = models.CASCADE)
    task_id = models.ForeignKey('Task', on_delete = models.CASCADE)

    def __str__(self):
        return "volunteer_id: {}, task_id: {}".format(self.volunteer_id, self.task_id)

class Task(models.Model):

    volunteer_work = models.ManyToManyField('Volunteer', through = 'WorksOn')

    name = models.CharField(max_length = 20)
    due_date = models.DateField()
    entry_date = models.DateField()
    difficulty = models.IntegerField()
    completed = models.BooleanField(default = False)

    creator = models.ForeignKey('Employee', on_delete = models.CASCADE)
    event   = models.ForeignKey('event.Event', on_delete = models.CASCADE)

    def __str__(self):
        return "Task Name: {} Volunteers in task: {}".format(self.name, self.volunteer_work)

class EventOrganisation(models.Model):

    reason = models.CharField(max_length = 30)
    entry_date = models.DateField()
    event_id = models.ForeignKey('event.Event', on_delete = models.CASCADE)
    organiser_id = models.ForeignKey('Employee', on_delete = models.CASCADE)
    
    class Meta:
        unique_together = ('event_id', 'organiser_id')

    def __str__(self):
        return "Event ID: {} ".format(self.event_id)

class EventParticipation(models.Model):

    date = models.DateField()
    duration = models.DateTimeField(blank=True, default='', null = True)
    impressions = models.CharField(max_length =200, blank=True, default='', null = True)

    member_id = models.ForeignKey('member.Member', on_delete = models.CASCADE)
    event_id = models.ForeignKey('event.Event', on_delete = models.CASCADE)

    def __str__(self):
        return "Date: {} Member ID{} Event ID {}".format(self.date, self.member_id, self.event_id)
