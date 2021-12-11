from django.shortcuts import render
from django.http.response import Http404, HttpResponseRedirect, HttpResponse

# Create your views here.

def index(request):

    return HttpResponse("Welcome!")
