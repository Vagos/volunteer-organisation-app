from django.shortcuts import render

# Create your views here.

def index(request):

    return render(request, "volunteer/index.html")

def teams(request, team_name):

    return render(request, "volunteer/teams.html", { "team_name" : team_name })
