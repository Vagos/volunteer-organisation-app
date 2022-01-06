from django.shortcuts import render
from django.http.response import Http404, HttpResponseRedirect
from django.db import connection, IntegrityError
from django.urls import reverse

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

        cursor.execute("SELECT * FROM team")

        teams = fetchall(cursor)

        cursor.execute("""SELECT id, name FROM task WHERE 
                       DATE('now') - entry_date < 1
                       """)

        recent_tasks = fetchall(cursor)

    context = {"teams":teams, "recent_tasks":recent_tasks}

    return render(request, "volunteer/index.html", context=context)


def team(request, team_name):

    with connection.cursor() as cursor:

        cursor.execute("SELECT * FROM team WHERE name = '%s'" % (team_name))

        team = fetchall(cursor)[0]

        cursor.execute("""SELECT volunteer_id, name, surname FROM  team_members
                       WHERE team_name = '%s' 
                       """ % (team_name))

        members = fetchall(cursor)

        cursor.execute("""SELECT *
        FROM volunteer_task_assigned AS VTA WHERE VTA.volunteer_id IN 
        (SELECT volunteer_id FROM team_members WHERE team_name = '%s')
        """ % (team_name))

        tasks = fetchall(cursor)

    context = {"team":team, "members":members, "tasks":tasks}

    print(context)

    return render(request, "volunteer/team.html", context=context)

def task(request, task_id):

    with connection.cursor() as cursor:

        if request.POST: # Ask if this is correct.

            cursor.execute("SELECT completed from task WHERE id = %d" % (task_id))

            is_completed = fetchall(cursor)[0].completed

            if not is_completed:
                try:
                    cursor.execute("""
                    INSERT INTO works_on (evaluation, task, volunteer) VALUES('%s', %d, %d)
                    """ % ("no evaluation", task_id, 2))
                except IntegrityError:
                    pass
        
        # cursor.execute("SELECT * FROM task")
        # print(fetchall(cursor))
    
        cursor.execute("""
        SELECT VT.id, VT.name, E.id AS event_id, E.name as event_name, VT.difficulty, VT.creator as creator_id, VT.completed,
        M.name as creator_name, M.surname as creator_surname 
        FROM task AS VT JOIN event AS E
        ON VT.event = E.id JOIN member as M ON M.id = VT.creator
        WHERE VT.id = %d
        """ % (task_id))

        task = fetchall(cursor)[0]

        cursor.execute("""
        SELECT * FROM volunteer_task_assigned WHERE task_id = %d
        """ % (task_id))

        working_on = fetchall(cursor)

    context = {"task":task, "working_on":working_on}

    return render(request, "volunteer/task.html", context=context)

def task_done(request, task_id):

    with connection.cursor() as cursor:

        cursor.execute("""
        UPDATE task SET completed = True
        WHERE id = %d
        """ % (task_id))

    return HttpResponseRedirect(reverse("volunteer:task", args=(task_id,)))


def profile(request, volunteer_id):

    with connection.cursor() as cursor:

        cursor.execute("""
        SELECT name, surname, join_date, 
        (
            SELECT COUNT(*) FROM works_on WHERE volunteer = M.id
        ) AS tasks_working_on, 
        (
            SELECT category FROM 
            (
                SELECT E.category, COUNT(*) as event_cnt FROM volunteer_task_assigned as VTA, task as VT, event as E 
                WHERE VTA.volunteer_id = M.id AND VT.id = VTA.task_id AND E.id = VT.event
                GROUP BY E.category
                ORDER BY event_cnt DESC LIMIT 1
            )
        ) AS favorite_event_category

        FROM member as M LEFT JOIN volunteer AS V USING(id)
        WHERE M.id = %d
        """ % (volunteer_id))

        volunteer = fetchall(cursor)[0]

        cursor.execute("""
        SELECT task_name, task_id FROM volunteer_task_assigned
        WHERE volunteer_id = %d """ % (volunteer_id))

        tasks = fetchall(cursor);

        cursor.execute("""
        SELECT E.id, E.name FROM event as E WHERE organiser = %d
        """ % (volunteer_id))

        organised_events = fetchall(cursor)

    context = {"volunteer":volunteer, "tasks":tasks, "organised_events": organised_events}

    return render(request, "volunteer/volunteer.html", context=context)
