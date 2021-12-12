from django.shortcuts import render
from django.http.response import Http404, HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.db import connection

# Create your views here.

def index(request):

    return render(request, "member/index.html")

def join(request):

    return render(request, "member/login.html")


def profile(request, name = None):

    name = name if name else request.session["name"]

    return render(request, "member/profile.html", {"name" : name})


def login(request): # This logs users in and creates their account if they don't exist yet.

    username = request.POST["username"]
    password = request.POST["password"]

    if not authenticate(request, username, password): add_user(username, password)

    request.session["name"] = username

    return HttpResponseRedirect(reverse("member:profile"))

def authenticate(request, username, password):
    
    with connection.cursor() as cursor:

        cursor.execute("SELECT * FROM member_member") # WHERE name = %s AND password = %s" % (username, password))

        r = cursor.fetchone()

        print(r)

        return r != None

def add_user(username, password):

    with connection.cursor() as cursor:
        
        cursor.execute("INSERT INTO member_member(name, surname, password) VALUES ('%s', '%s', '%s')" % (username, "lastnametest", password))

