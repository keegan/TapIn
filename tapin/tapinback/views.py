from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse

from .models import Client, TapUser

import json
import random
import secrets

def status(request):
    if request.method == 'GET':
        request.session.set_expiry(30)
        request.session['temptoken'] = str(secrets.token_urlsafe(64))
        res = {}
        hostname = request.GET.get('hostname', None)
        if hostname is None:
            return HttpResponse(status=400)
        client = Client.objects.get(hostname=hostname)
        token = request.GET.get('token', None)
        if token is None:
            return HttpResponse(status=400)
        print(token)
        print(client.token)
        if client.token != token:
            return HttpResponse(status=401)
        #res['status'] = client.status 
        res['status'] = "success"
        res['username'] = client.username
        res['token'] = str(request.session['temptoken'])
        return HttpResponse(json.dumps(res), content_type='application/json')
    else:
        return HttpResponse(status=400)

def pinauth(request):
    if request.method == 'POST':
        if request.session.get_expiry_age() <= 0:
            return HttpResponse(status=408)
        params = request.content_params
        if request.session['temptoken'] != params['temptoken']:
            return HttpResponse(status=401)
        user = TapUser.objects.get(id = params['user'])

def tapd(request):
    if request.method == 'GET':
        hostname = request.GET.get('hostname', None)
        if hostname is None:
            return HttpResponse(status=400)
        client = Client.objects.get(hostname=hostname)
        
    elif request.method == 'POST':
        return HttpResponse(status=200)
    return HttpResponse(status=400)

#from .forms import AuthForm
# Create your views here.
#def formRequest(request): 
	#if request.method == "POST":
		#form = AuthForm(request.POST)
		#if form.isValid():
			#process data
			#return to another url v
			#return HTTPResponseDirect(insert url here)
	#else:
	#	form = AuthForm()

	#return render(request, "backui.html", {'form':form})
