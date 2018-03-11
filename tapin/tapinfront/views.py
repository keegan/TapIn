from django.shortcuts import render

from django.http import HttpResponse, HttpResponseBadRequest

# Create your views here.

def index(request):
    return render(request, 'index.html')

def login(request):
    return render(request, 'login.html')
#def api(request):
    #if request.method == 'GET':
       
