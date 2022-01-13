from django.shortcuts import redirect, render
from django.http.response import Http404, HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.db import connection

# Create your views here.

from collections import namedtuple

from .utilities import *

def index(request):

    with connection.cursor() as cursor:

        cursor.execute("SELECT name, id FROM active_event")
        events = fetchall(cursor)
        
        cursor.execute("SELECT name, id FROM event as E WHERE E.id NOT IN (SELECT id FROM active_event) ORDER BY end_date DESC LIMIT 20")
        past_events = fetchall(cursor)

        # Fun facts
    
        cursor.execute("SELECT name, start_date FROM event ORDER BY start_date ASC LIMIT 1")
        first_event = fetchall(cursor)[0]

        cursor.execute("SELECT COUNT(*) as count FROM volunteer WHERE join_date > date('now', '-365 day')")
        vols_joined_last_days = fetchall(cursor)[0]

        cursor.execute("""SELECT member.name || ' ' || member.surname as name, COUNT(*) as participation_count 
                       FROM event_participation as ep join member on member.id = ep.member group by member.id 
                       ORDER by participation_count DESC LIMIT 1""")
        most_participations = fetchall(cursor)[0]

        cursor.execute("""
        SELECT m1.name || ' ' || m1.surname as name1, m2.name || ' ' || m2.surname as name2, 
        (
            SELECT COUNT(*) FROM 
            (
                SELECT event FROM event_participation WHERE member = m1.id
                INTERSECT
                SELECT event FROM event_participation WHERE member = m2.id
            )
        ) as common
         FROM member as m1, member as m2 WHERE m1.id != m2.id ORDER BY common DESC LIMIT 1
        """)
        most_common_events = fetchall(cursor)[0]

        cursor.execute("""
        SELECT MAX(value) as value, member.name || ' ' || member.surname as name, income.date 
        FROM income join event_participation as p on income.participation = p.id join member on p.member = member.id
        WHERE income.id IN 
        (
            SELECT income FROM donation
        )
        """)
        biggest_donation = fetchall(cursor)[0]

        cursor.execute("""
        SELECT count(*) as count FROM 
        (
            SELECT member.id, event.id, COUNT(DISTINCT event.category) as cat_cnt 
            FROM event_participation as ep join event on event.id = ep.event join member on ep.member = member.id 
            GROUP BY member.id
        ) 
        WHERE cat_cnt = 
        (
            SELECT COUNT(*) FROM event_category
        )
        """)
        every_category = fetchall(cursor)[0]

    facts = {"first_event": first_event, "vols_joined_last_days":vols_joined_last_days, 
             "most_participations":most_participations, "most_common_events":most_common_events, "biggest_donation":biggest_donation, "every_category":every_category}
        
    context = {"events": events, "past_events":past_events, "facts":facts}

    return render(request, "member/index.html", context=context)

def join(request):

    return render(request, "member/login.html")


def profile(request, name = None):

    name = name if name else request.session["name"]

    return render(request, "member/profile.html", {"name" : name})


def login(request): # This logs users in and creates their account if they don't exist yet.

    name = request.POST["username"]
    surname = request.POST["surname"]

    request.session["name"] = name
    request.session["surname"] = surname

    with connection.cursor() as cursor:

        cursor.execute(f"""SELECT id FROM member WHERE name = '{name}' AND surname = '{surname}'""") 

        if len(fetchall(cursor)) == 0:
            add_user(name, surname)
        
        cursor.execute(f"""SELECT id FROM member WHERE name = '{name}' AND surname = '{surname}'""") 
        member = fetchall(cursor)[0]

    request.session["id"] = member.id

    return redirect("volunteer:profile", volunteer_id=member.id)

def add_user(name, surname):

    with connection.cursor() as cursor:

        cursor.execute("INSERT INTO member(name, surname) VALUES ('%s', '%s')" % (name, surname))

def support(request):

    if not logged_in(request):
        return redirect("member:join")


    with connection.cursor() as cursor:

        cursor.execute(f"SELECT E.name, EP.id, E.start_date FROM event_participation as EP join event as E ON EP.event = E.id WHERE member = {request.session['id']}")

        participated_events = fetchall(cursor)

    context = {"participated_events":participated_events}

    return render(request, "member/support.html", context=context)

def support_add(request):

    d_p = request.POST["event"] # event_participation
    d_v = request.POST["value"]
    d_m = request.POST["message"]

    d_t = request.POST["type"]


    with connection.cursor() as cursor:

        cursor.execute(f"INSERT INTO income (value, date, participation) VALUES({d_v}, date('now'), {d_p})")

        if d_t == "donation":
            cursor.execute("INSERT INTO donation (message, income) VALUES(%s, LAST_INSERT_ROWID())", (d_m,))
        elif d_t == "service":
            cursor.execute(f"INSERT INTO service (description, income) VALUES(%s, LAST_INSERT_ROWID())", (d_m,))
        elif d_t == "sale":
            d_a = request.POST["ammount"]
            cursor.execute(f"INSERT INTO sale (ammount, item_name, income) VALUES(%s, %s, LAST_INSERT_ROWID())", (d_a, d_m))


    return redirect("member:support")
