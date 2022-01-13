from django.http.response import Http404, HttpResponseRedirect
from django.shortcuts import redirect, render
from django.db import connection
from django.urls import reverse
import django.db
from django.contrib.staticfiles import finders

from member.utilities import *

# Create your views here.

def create_report_graph(report):

    print(report)


    import matplotlib.pyplot as plt

    incomes = [r.total for r in report] # y axis
    month = [f"{r.year}:{r.quarter}" for r in report] # x axis

    plt.rcParams["font.size"] = 7.0
    plt.rcParams["text.usetex"] = True
    
    plt.title("Volunteer Organisation Incomes")
    plt.xlabel("Year/Month")
    plt.ylabel("Incomes")
    

    plt.plot(month, incomes)

    # Save the plot file
    APP_LABEL = 'event'
    FILE_NAME = '{}.png'.format("report_graph")
    stores = finders.AppDirectoriesFinder(app_names={APP_LABEL}).storages
    file_path = stores[APP_LABEL].path(FILE_NAME)

    plt.savefig(file_path)


def index(request):

    with connection.cursor() as cursor:
        
        if not logged_in(request): return redirect("member:index")

        cursor.execute("SELECT %s IN (SELECT id FROM employee) as is_employee" % request.session["id"])
        if (not fetchall(cursor)[0].is_employee): return redirect("member:index")

        cursor.execute("SELECT name, surname, member.id as id FROM employee JOIN member ON employee.id = member.id")
        employees = fetchall(cursor)

        cursor.execute("SELECT name FROM event_category")
        event_categories = fetchall(cursor)

        cursor.execute("""SELECT date, value, expense.description, event.name as event_name, event.id as event_id FROM expense JOIN event ON expense.event = event.id 
                       ORDER BY date DESC LIMIT 10""")
        expenses = fetchall(cursor)

        cursor.execute("""SELECT I.date, I.value, M.name as member_name, M.surname as member_surname, 
        (
            SELECT IIF(I.id IN (SELECT income FROM donation), "Donation", IIF(I.id IN ( SELECT income FROM service ), "Service", IIF(I.id IN ( SELECT income FROM sale ), "Sale", "None")))
        ) as type
        FROM 
        income as I JOIN event_participation as P ON I.participation = P.id JOIN member as M on P.member = M.id
        ORDER BY DATE DESC LIMIT 10""")
        incomes = fetchall(cursor)

        report = cursor.execute("""
        SELECT SUM(value) as total, strftime('%Y', date) AS year, strftime('%m', date) / 3 + 1 as quarter FROM income GROUP BY year, quarter ORDER BY year;
        """)
        report = fetchall(cursor)
        create_report_graph(report)

        cursor.execute("SELECT * FROM active_event")
        active_events = fetchall(cursor)

        cursor.execute("SELECT T.id, T.name, E.name as event_name  FROM task as T join event as E on T.event = E.id WHERE T.completed = false AND T.creator = %s", (request.session["id"], ))
        created_tasks = fetchall(cursor)

    context = { "event_categories":event_categories, "employees":employees, "expenses":expenses, 
               "incomes":incomes, "active_events":active_events, "created_tasks":created_tasks }

    return render(request, "event/index.html", context=context)

def details(request, event_id):

    with connection.cursor() as cursor:

        cursor.execute("""SELECT E.name, E.id, E.start_date, E.end_date, E.category, 
                        (
                            SELECT E.id IN (SELECT id from  active_event)
                        ) as active,
                       (
                           SELECT M.name FROM member as M where M.id = E.organiser
                       ) as organiser_name, 
                       (
                           SELECT M.surname FROM member as M where M.id = E.organiser
                       ) as organiser_surname,
                       E.organiser as organiser_id
                       FROM event AS E WHERE E.id = %d""" % event_id) 
        event = fetchall(cursor)[0]

        cursor.execute("SELECT id, name, completed FROM task WHERE event = %d" % event_id)
        tasks = fetchall(cursor)

        cursor.execute("""SELECT M.id, M.name, M.surname from event_participation AS EP
                        JOIN member AS M ON EP.member = M.id
                       WHERE EP.event = %d""" % (event_id))
        participants = fetchall(cursor)

        has_participated = None

        if logged_in(request):
            cursor.execute("""SELECT 
            EXISTS 
            (
            SELECT id FROM event_participation WHERE member = %s AND event = %s
            ) as exist
                           """, (request.session["id"], event_id))

            has_participated = fetchall(cursor)[0]

    context = {"event":event, "tasks":tasks, "participants":participants, "has_participated":has_participated}

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

        cursor.execute(""" INSERT INTO event 
                           (name, start_date, end_date, place, description, category, organiser)
                           VALUES('%s', '%s','%s','%s','%s','%s', %s)
                       """ % 
                       (event_name, start_date, end_date, place, description, category, request.session["id"]))
        
    return HttpResponseRedirect(reverse("event:index"))


def add_eventcategory(request):

    if not request.POST: return HttpResponseRedirect(reverse("event:index"))

    with connection.cursor() as cursor:

        c_n = request.POST["name"]

        cursor.execute("INSERT INTO event_category (name) VALUES ('%s')" \
                       % (c_n))

    return HttpResponseRedirect(reverse("event:index"))

def task_add(request):

    if not request.POST: return HttpResponseRedirect(reverse("event:index"))
    
    with connection.cursor() as cursor:

        t_n = request.POST["name"]
        t_e = request.POST["event"]
        t_dd = request.POST["due"]
        t_d = request.POST["difficulty"]

        cursor.execute("INSERT INTO task (name, event, due_date, difficulty, entry_date, creator) VALUES('%s', %s, '%s', %s, date('now'), %s)" 
                       % (t_n, t_e, t_dd, t_d, request.session["id"]))
    
    return redirect("event:index")

def task_delete(request):

    t = request.POST["task"]


    with connection.cursor() as cursor:

        cursor.execute("DELETE FROM task WHERE task.id = %s", (t,))

    return redirect("event:index")

def remove_task(request):

    return redirect("event:index")

def add_team(request):

    if not request.POST: return HttpResponseRedirect(reverse("event:index"))

    t_n = request.POST["name"]
    t_d = request.POST["description"]

    with connection.cursor() as cursor:

        cursor.execute("INSERT INTO team (name, description) VALUES('%s', '%s')" % (t_n, t_d) )
        cursor.execute("INSERT INTO team_management (employee, team, start_date) VALUES(%s, '%s', date('now'))" % (request.session["id"], t_n) )
    
    return HttpResponseRedirect(reverse("event:index"))

def join_event(request, event_id):

    with connection.cursor() as cursor:
        try:
            cursor.execute("INSERT INTO event_participation (event, member) VALUES(%d, %s)" % (event_id, request.session["id"]))
        except django.db.IntegrityError:
            redirect("member:join")

    return redirect(("event:details"), event_id=event_id)

def add_expense(request):

    if not request.POST: return HttpResponseRedirect(reverse("event:index"))

    e_a = request.POST["value"]
    e_e = request.POST["event"]
    e_d = request.POST["description"]


    with connection.cursor() as cursor:
        cursor.execute("INSERT INTO expense (event, value, description, date) VALUES(%s, %s, '%s', %s)" % (e_e, e_a, e_d, "date('now')"))

    return HttpResponseRedirect(reverse("event:index"))
