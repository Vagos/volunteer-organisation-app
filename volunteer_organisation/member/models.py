from django.db import models
from django.utils import timezone
import datetime

# Create your models here.


class Member(models.Model):

    name = models.CharField(max_length = 200)
    surname = models.CharField(max_length = 200)
    password = models.CharField(max_length=200)

    dob = models.DateField(default=None, blank=True, null=True)
    email = models.CharField(max_length = 200, default=None, blank=True, null=True)
    cor = models.CharField(max_length =200, blank=True, default='', null=True)
    phone_number = models.CharField(max_length =13, blank=True, default='', null=True)

    def __str__(self):
        return "Name: {} Surname: {}".format(self.name, self.surname)
