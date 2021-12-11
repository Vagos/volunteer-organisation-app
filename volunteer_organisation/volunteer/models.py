from django.db import models
from django.utils import timezone
import datetime

from member.models import Member

# Create your models here.

class Volunteer(Member):

    join_date = models.DateField(max_length = 200)

    def __str__(self):
        return "Name: {} Surname: {} (Volunteer)".format( self.name, self.surname )

class Participation(models.Model):

    start_date = models.DateField()
    end_date = models.DateField()
    volunteer_id = models.ForeignKey('Volunteer', on_delete = models.CASCADE)
    team_name = models.ForeignKey('Team', on_delete = models.CASCADE)

    def __str__(self):
        return "ID: {}(volunter), Team Name: {}".format(self.volunteer_id, self.team_name)


class Team(models.Model):

    team_participation = models.ManyToManyField('Volunteer', through = 'Participation')
    #team_management = models.ManyToManyField('Employee', through = 'Management')

    name = models.CharField(max_length = 200, unique = True)
    description = models.CharField(max_length = 300)

    def __str__(self):
        return "Participants: {}(volunters), Team Name: {}".format(self.participation, self.team_name)

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

    creator = models.ForeignKey('event.Employee', on_delete = models.CASCADE)
    # event_name = models.ForeignKey('Event', on_delete = models.CASCADE)

    def __str__(self):
        return "Task Name: {} Volunteers in task: {}".format(self.name, self.vol_work)
