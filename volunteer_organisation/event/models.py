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

class Income(models.Model):

    value = models.PositiveIntegerField()
    date = models.DateField()
    member_id = models.PositiveIntegerField()

    def __str__(self):
        return "Value: {} Member: {}".format(self.value, self.member_id)

class Sale(models.Model):

    ammount = models.PositiveIntegerField()
    item_name = models.CharField(max_length=200)
    income_id = models.ForeignKey('Income', on_delete = models.CASCADE)

    def __str__(self):
        return "Ammount: {} Income ID: {}".format(self.ammount, self.income_id)

class Service(models.Model):

    description = models.CharField(max_length = 300)
    income_id = models.ForeignKey('Income', on_delete = models.CASCADE)

    def __str__(self):
        return "Income ID: {}".format(self.income_id)


class Donation(models.Model):

    message = models.CharField(max_length = 300)
    income_id = models.ForeignKey('Income', on_delete = models.CASCADE)

    def __str__(self):
        return "Income ID: {}".format(self.income_id)


class Expense(models.Model):

    date = models.DateField()
    value = models.PositiveIntegerField()
    description = models.CharField(max_length = 300)
    event_id = models.ForeignKey('Event', on_delete = models.CASCADE)

    def __str__(self):
        return "".format()


class IncomeToExpense(models.Model):

    income_id = models.ForeignKey('Income', on_delete = models.CASCADE)
    expense_id = models.ForeignKey('Expense', on_delete = models.CASCADE)

    def __str__(self):
        return "".format()
