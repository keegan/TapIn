from django.shortcuts import render

from django.http import HttpResponse, HttpResponseBadRequest

# Create your views here.

def index(request):
    return render(request, 'index.html')

def login(request):
    if request.method == "GET":
        token = request.GET.get('token', None)
        username = request.GET.get('username', None)
        status = request.GET.get('status', None)

        if token is None or username is None or status is None:
            return HttpResponse(status=400)

        return render(request, 'success.html')
    return HttpResponse(status=400)
#def api(request):
    #if request.method == 'GET':
       
