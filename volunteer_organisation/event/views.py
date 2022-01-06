from django.http.response import Http404, HttpResponseRedirect
from django.shortcuts import render
from django.db import connection
from django.urls import reverse

from collections import namedtuple

# Create your views here.

def fetchall(cursor):
    "Return all rows from a cursor as a namedtuple"
    desc = cursor.description
    nt_result = namedtuple('Result', [col[0] for col in desc])
    return [nt_result(*row) for row in cursor.fetchall()]

def index(request):

    with connection.cursor() as cursor:

        cursor.execute("SELECT name FROM event_category")
        event_categories = fetchall(cursor)

        cursor.execute("SELECT * FROM expense")
        expenses = fetchall(cursor)

        cursor.execute("SELECT * FROM income")
        incomes = fetchall(cursor)

    context = { "event_categories":event_categories, "expenses":expenses, "incomes":incomes }

    return render(request, "event/index.html", context=context)

def details(request, event_id):

    with connection.cursor() as cursor:

        cursor.execute("SELECT * FROM event AS e WHERE e.id = %d" % event_id) 
        event = fetchall(cursor)[0]

        cursor.execute("SELECT id, name FROM task WHERE event = %d" % event_id)
        tasks = fetchall(cursor)

        cursor.execute("""SELECT M.id, M.name, M.surname from event_participation AS EP
                        JOIN member AS M ON EP.member = M.id
                       WHERE EP.event = %d""" % (event_id))
        participants = fetchall(cursor)

    context = {"event":event, "tasks":tasks, "participants":participants}

    return render(request, "event/details.html", context=context)

def add_event(request):
    
    if not request.POST: return HttpResponseRedirect(reverse("event:index"))

    with connection.cursor() as cursor:
        
        event_name = request.POST["name"]

        start_date = request.POST["start"]
        end_date = request.POST["end"]

        
        place = request.POST["place"]
        description = request.POST["description"]
        category = request.POST["category"]

        reason = request.POST["reason"]

        cursor.execute(""" INSERT INTO event 
                           (name, start_date, end_date, place, description, category)
                           VALUES('%s', '%s','%s','%s','%s','%s')
                       """ % 
                       (event_name, start_date, end_date, place, description, category))
        
    return HttpResponseRedirect(reverse("event:index"))


def add_eventcategory(request):

    if not request.POST: return HttpResponseRedirect(reverse("event:index"))

    with connection.cursor() as cursor:

        c_n = request.POST["name"]

        cursor.execute("INSERT INTO event_category (name) VALUES ('%s')" \
                       % (c_n))

    return HttpResponseRedirect(reverse("event:index"))
