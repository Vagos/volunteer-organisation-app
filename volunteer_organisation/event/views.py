from django.http.response import Http404, HttpResponseRedirect
from django.shortcuts import redirect, render
from django.db import connection
from django.urls import reverse
import django.db
from django.contrib.staticfiles import finders

from collections import namedtuple

# Create your views here.

def fetchall(cursor):
    "Return all rows from a cursor as a namedtuple"
    desc = cursor.description
    nt_result = namedtuple('Result', [col[0] for col in desc])
    return [nt_result(*row) for row in cursor.fetchall()]

def create_report_graph(report):

    import matplotlib.pyplot as plt

    incomes = [r.total for r in report] # y axis
    month = [r.month for r in report] # x axis
    plt.plot(month, incomes)

    print(incomes, month)


    # Save the plot file
    APP_LABEL = 'event'
    FILE_NAME = '{}.png'.format("report_graph")
    stores = finders.AppDirectoriesFinder(app_names={APP_LABEL}).storages
    file_path = stores[APP_LABEL].path(FILE_NAME)

    print("PATH: ", file_path)

    plt.savefig(file_path)

    

def index(request):

    with connection.cursor() as cursor:

        cursor.execute("SELECT name FROM event_category")
        event_categories = fetchall(cursor)

        cursor.execute("SELECT date, value, event.name as event_name, event.id as event_id FROM expense JOIN event ON expense.event = event.id ORDER BY date DESC")
        expenses = fetchall(cursor)

        cursor.execute("""SELECT I.date, I.value, M.name as member_name, M.surname as member_surname, 
        (
            SELECT IIF(I.id IN (SELECT income FROM donation), "Donation", IIF(I.id IN ( SELECT income FROM service ), "Service", IIF(I.id IN ( SELECT income FROM sale ), "Sale", "None")))
        ) as type
        FROM 
        income as I JOIN event_participation as P ON I.participation = P.id JOIN member as M on P.member = M.id
        ORDER BY DATE DESC""")
        incomes = fetchall(cursor)

        report = cursor.execute("""
        SELECT SUM(value) as total, strftime('%Y %m', date) AS month FROM income GROUP BY month;
        """)
        report = fetchall(cursor)
        create_report_graph(report)

        cursor.execute("SELECT * FROM active_event")
        active_events = fetchall(cursor)

    context = { "event_categories":event_categories, "expenses":expenses, "incomes":incomes, "active_events":active_events }

    return render(request, "event/index.html", context=context)

def details(request, event_id):

    with connection.cursor() as cursor:

        cursor.execute("""SELECT E.name, E.id, E.start_date, E.end_date, E.category, 
                       (
                           SELECT M.name FROM member as M where M.id = E.organiser
                       ) as organiser_name, 
                       (
                           SELECT M.surname FROM member as M where M.id = E.organiser
                       ) as organiser_surname,
                       E.organiser as organiser_id
                       FROM event AS E WHERE e.id = %d""" % event_id) 
        event = fetchall(cursor)[0]

        cursor.execute("SELECT id, name, completed FROM task WHERE event = %d" % event_id)
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

def add_task(request):

    if not request.POST: return HttpResponseRedirect(reverse("event:index"))
    
    with connection.cursor() as cursor:

        t_n = request.POST["name"]
        t_e = request.POST["event"]
        t_dd = request.POST["due"]
        t_d = request.POST["difficulty"]

        cursor.execute("INSERT INTO task (name, event, due_date, difficulty, entry_date, creator) VALUES('%s', %s, '%s', %s, date('now'), %d)" 
                       % (t_n, t_e, t_dd, t_d, 1))
    
    return HttpResponseRedirect(reverse("event:index"))

def add_team(request):

    if not request.POST: return HttpResponseRedirect(reverse("event:index"))

    t_n = request.POST["name"]
    t_d = request.POST["description"]

    with connection.cursor() as cursor:
        cursor.execute("INSERT INTO team (name, description) VALUES('%s', '%s')" % (t_n, t_d))

        cursor.execute("INSERT INTO team_management (employee, description, team, start_date) (%s, %s, %s, date('now'))" %
                       ("1", t_n, t_d))
    
    return HttpResponseRedirect(reverse("event:index"))

def join_event(request, event_id):

    
    with connection.cursor() as cursor:
        try:
            cursor.execute("INSERT INTO event_participation (event, member) VALUES(%d, %s)" % (event_id, request.session["id"]))
        except django.db.IntegrityError:
            pass

    return redirect(("event:details"), event_id=event_id)

def add_expense(request):

    if not request.POST: return HttpResponseRedirect(reverse("event:index"))

    e_a = request.POST["value"]
    e_e = request.POST["event"]
    e_d = request.POST["description"]


    with connection.cursor() as cursor:
        cursor.execute("INSERT INTO expense (event, value, description, date) VALUES(%s, %s, '%s', %s)" % (e_e, e_a, e_d, "date('now')"))

    return HttpResponseRedirect(reverse("event:index"))
