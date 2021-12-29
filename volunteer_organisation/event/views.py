from django.http.response import HttpResponse
from django.shortcuts import render
from django.db import connection

from collections import namedtuple

# Create your views here.

def fetchall(cursor):
    "Return all rows from a cursor as a namedtuple"
    desc = cursor.description
    nt_result = namedtuple('Result', [col[0] for col in desc])
    return [nt_result(*row) for row in cursor.fetchall()]

def index(request):

    return render(request, "event/index.html")

def details(request, event_id):

    with connection.cursor() as cursor:

        cursor.execute("SELECT * FROM event_event AS e WHERE e.id = %d" % event_id) 

        event = fetchall(cursor)[0]

        print("EVENT: ", event)

    context = {"event" : event}

    return render(request, "event/details.html", context=context)
