from django.shortcuts import render
from django.db import connection

# Create your views here.

from collections import namedtuple

def fetchall(cursor):
    "Return all rows from a cursor as a namedtuple"
    desc = cursor.description
    nt_result = namedtuple('Result', [col[0] for col in desc])

    r = [nt_result(*row) for row in cursor.fetchall()]

    return r

def index(request):

    with connection.cursor() as cursor:

        cursor.execute("SELECT * FROM volunteer_team")

        teams = fetchall(cursor)

        cursor.execute("""SELECT name FROM volunteer_task WHERE 
                       DATE('now') - entry_date > 10
                       """)

        recent_tasks = fetchall(cursor)

    context = {"teams":teams, "recent_tasks":recent_tasks}

    return render(request, "volunteer/index.html", context=context)

def team(request, team_name):

    with connection.cursor() as cursor:

        cursor.execute("SELECT * FROM volunteer_team WHERE name = '%s'" % (team_name))
        
        team = fetchall(cursor)[0]

    context = {"team":team}

    print(context)

    return render(request, "volunteer/team.html", context=context)
