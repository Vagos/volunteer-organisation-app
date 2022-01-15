from django.shortcuts import redirect, render
from django.http.response import Http404, HttpResponseRedirect
from django.db import connection, IntegrityError, reset_queries
from django.urls import reverse

# Volunteer views

from member.utilities import *


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

        cursor.execute("""
        SELECT T.name, T.description, M.name as mgr_name, M.surname as mgr_surname, 
        (SELECT IIF(TM.end_date is NULL, M.id, NULL)) as mgr_id, 
        (
            SELECT name FROM 
            (
                SELECT atm.name || ' ' || atm.surname as name, COUNT(task.id) as task_cnt 
                FROM active_team_members as atm JOIN works_on ON atm.id = works_on.volunteer 
                JOIN task ON works_on.task = task.id
                WHERE atm.team_name = T.name and task.completed = true and task.due_date > DATETIME('now', '-30 day') GROUP BY atm.id ORDER BY task_cnt DESC
            )
        ) as best_volunteer
                       FROM team as T JOIN team_management as TM ON T.name = TM.team LEFT JOIN member as M on M.id = TM.employee
                       WHERE T.name = '%s' ORDER BY TM.start_date DESC LIMIT 1""" % (team_name))

        team = fetchall(cursor)[0]

        cursor.execute(f"""SELECT volunteer_id, name, surname, 
        (
            SELECT volunteer_id IN 
            (SELECT id FROM active_team_members as ATM WHERE ATM.team_name = '{team_name}')
        ) as active
        FROM team_members WHERE team_name = '{team_name}' GROUP BY volunteer_id
                       """)

        members = fetchall(cursor)

        cursor.execute("""SELECT *
        FROM volunteer_task_assigned AS VTA JOIN task ON VTA.task_id = task.id WHERE VTA.volunteer_id IN 
        (SELECT id FROM active_team_members WHERE team_name = %s) AND task.completed = false GROUP BY VTA.task_id ORDER BY RANDOM() LIMIT 15 
        """, (team_name,)) 

        tasks = fetchall(cursor)

        

    context = {"team":team, "members":members, "tasks":tasks}

    return render(request, "volunteer/team.html", context=context)

def team_join(request, team_name):

    if not logged_in(request): return redirect("volunteer:team", team_name=team_name)

    with connection.cursor() as cursor:

        try:
            cursor.execute(f"""INSERT INTO team_participation(start_date, end_date, team, volunteer) VALUES(date('now'), NULL, '{team_name}', {request.session['id']})""")
        except IntegrityError:
            return redirect("volunteer:team", team_name=team_name)

    return redirect("volunteer:team", team_name=team_name)

def team_leave(request, team_name):

    if not logged_in(request): return redirect("volunteer:team", team_name=team_name)

    with connection.cursor() as cursor:

        cursor.execute(f"SELECT id FROM team_participation WHERE volunteer = {request.session['id']} AND team = '{team_name}' AND end_date is NULL")
        
        participation = fetchall(cursor)
        if len(participation) == 0: return redirect("volunteer:team", team_name=team_name)
        
        cursor.execute(f"UPDATE team_participation SET end_date = date('now') WHERE id = {participation[0].id}")

    return redirect("volunteer:team", team_name=team_name)



def task(request, task_id):

    with connection.cursor() as cursor:

        if request.POST: # JOIN the task

            if  not logged_in(request):
                return redirect("member:join")

            cursor.execute("SELECT completed from task WHERE id = %d" % (task_id))

            is_completed = fetchall(cursor)[0].completed

            try:
                if not is_completed:
                    cursor.execute("""
                    INSERT INTO works_on (evaluation, task, volunteer) VALUES('%s', %d, %s)
                    """ % ("", task_id, request.session["id"]))
            except IntegrityError:
                return redirect("volunteer:task", task_id=task_id)
        
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

    if not logged_in(request): return redirect("volunteer:task", task_id=task_id)

    with connection.cursor() as cursor:

        cursor.execute(f"SELECT creator FROM task WHERE id = {task_id}")
        task_creator = fetchall(cursor)[0].creator

        if task_creator != request.session["id"]: return redirect("volunteer:task", task_id=task_id)

        cursor.execute("""
        UPDATE task SET completed = True
        WHERE id = %d
        """ % (task_id))

    return HttpResponseRedirect(reverse("volunteer:task", args=(task_id,)))


def profile(request, volunteer_id):

    with connection.cursor() as cursor:

        cursor.execute("""
        SELECT name, surname, join_date, position_name as position,
        (
            SELECT COUNT(*) FROM works_on JOIN task on works_on.task = task.id WHERE volunteer = M.id AND task.completed = false
        ) AS tasks_working_on, 
        (
            SELECT COUNT(*) FROM works_on JOIN task on works_on.task = task.id WHERE volunteer = M.id AND task.completed = true
        ) as tasks_completed,
        (
            SELECT category FROM 
            (
                SELECT E.category, COUNT(*) as event_cnt FROM volunteer_task_assigned as VTA, task as VT, event as E 
                WHERE VTA.volunteer_id = M.id AND VT.id = VTA.task_id AND E.id = VT.event 
                GROUP BY E.category
                ORDER BY event_cnt DESC LIMIT 1
            )
        ) AS favorite_event_category

        FROM member as M LEFT JOIN volunteer AS V USING(id) LEFT JOIN employee USING(id)
        WHERE M.id = %d
        """ % (volunteer_id))

        volunteer = fetchall(cursor)[0]

        cursor.execute("""
        SELECT task_name, task_id FROM volunteer_task_assigned JOIN task ON task_id = task.id
        WHERE volunteer_id = %d AND task.completed = false """ % (volunteer_id))

        tasks = fetchall(cursor);

        cursor.execute(f"""
        SELECT TM.team_name as name, 
        (
        SELECT {volunteer_id} IN (SELECT id FROM active_team_members as ATM WHERE ATM.team_name = TM.team_name)
        ) 
        as active FROM team_members as TM WHERE volunteer_id = {volunteer_id}
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


