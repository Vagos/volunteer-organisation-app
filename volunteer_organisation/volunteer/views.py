from django.shortcuts import render
from django.db import connection

# Volunteer views

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
                       DATE('now') - entry_date < 1
                       """)

        recent_tasks = fetchall(cursor)

    context = {"teams":teams, "recent_tasks":recent_tasks}

    return render(request, "volunteer/index.html", context=context)

def team(request, team_name):

    with connection.cursor() as cursor:

        cursor.execute("SELECT * FROM volunteer_team WHERE name = '%s'" % (team_name))

        team = fetchall(cursor)[0]

        cursor.execute("""SELECT name, surname FROM  team_members
                       WHERE team_name = '%s' 
                       """ % (team_name))

        members = fetchall(cursor)

        cursor.execute("""SELECT volunteer_name, volunteer_surname, task_name 
        FROM volunteer_task_assigned AS VTA WHERE VTA.volunteer_id IN 
        (SELECT volunteer_id FROM team_members WHERE team_name = '%s')
        """ % (team_name))

        tasks = fetchall(cursor)

    context = {"team":team, "members":members, "tasks":tasks}

    print(context)

    return render(request, "volunteer/team.html", context=context)
