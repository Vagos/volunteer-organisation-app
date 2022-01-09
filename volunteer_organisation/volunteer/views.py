from django.shortcuts import redirect, render
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

        cursor.execute("""SELECT T.name, T.description, M.name as mgr_name, M.surname as mgr_surname, M.id as mgr_id 
                       FROM team as T JOIN team_management as TM ON T.name = TM.team LEFT JOIN member as M on M.id = TM.employee
                       WHERE T.name = '%s' AND TM.end_date is NULL ORDER BY TM.start_date DESC LIMIT 1""" % (team_name))

        team = fetchall(cursor)[0]

        cursor.execute(f"""SELECT volunteer_id, name, surname, 
        (
            SELECT volunteer_id IN 
            (SELECT id FROM active_team_members as ATM WHERE ATM.team_name = '{team_name}')
        ) as active
        FROM team_members WHERE team_name = '{team_name}' 
                       """)

        members = fetchall(cursor)

        cursor.execute("""SELECT *
        FROM volunteer_task_assigned AS VTA WHERE VTA.volunteer_id IN 
        (SELECT id FROM active_team_members WHERE team_name = '%s')
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

            print("WOW: ",request.session["id"])

            if not is_completed:
                cursor.execute("""
                INSERT INTO works_on (evaluation, task, volunteer) VALUES('%s', %d, %s)
                """ % ("no evaluation", task_id, request.session["id"]))
        
        # cursor.execute("SELECT * FROM task")
        # print(fetchall(cursor))
    
        cursor.execute("""
        SELECT VT.id, VT.name, E.id AS event_id, E.name as event_name, VT.difficulty, VT.creator as creator_id, VT.completed,
        M.name as creator_name, M.surname as creator_surname, VT.due_date
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
        SELECT task_name, task_id FROM volunteer_task_assigned JOIN task ON task_id = task.id
        WHERE volunteer_id = %d AND task.completed = false """ % (volunteer_id))

        tasks = fetchall(cursor);

        cursor.execute(f"""
SELECT TM.team_name as name, (
SELECT {volunteer_id} IN (SELECT id FROM active_team_members as ATM WHERE ATM.team_name = TM.team_name)
) as active FROM team_members as TM WHERE volunteer_id = {volunteer_id}
        """)
        teams = fetchall(cursor)

        cursor.execute("""
        SELECT E.id, E.name FROM event as E WHERE organiser = %d
        """ % (volunteer_id))

        organised_events = fetchall(cursor)

    context = {"volunteer":volunteer, "tasks":tasks, "organised_events": organised_events, "teams":teams}

    return render(request, "volunteer/volunteer.html", context=context)

def join(request):

    try:
        with connection.cursor() as cursor:

            cursor.execute("INSERT INTO volunteer (id, join_date) VALUES(%s, %s)" % (request.session["id"], "date('now')"))
    except IntegrityError:
        print("This user is already a volunteer!")

    return redirect("volunteer:profile", volunteer_id = request.session["id"])

