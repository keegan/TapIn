from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse

from .models import Client, TapUser

import json
import random
import secrets

def status(request):
    if request.method == 'GET':
        request.session.set_expiry(30)
        request.session['session_token'] = str(secrets.token_urlsafe(64))
        res = {}
        hostname = request.GET.get('hostname', None)
        if hostname is None:
            return HttpResponse(status=400)
        client = Client.objects.get(hostname=hostname)
        token = request.GET.get('token', None)
        if token is None:
            return HttpResponse(status=400)
        if client.token != token:
            return HttpResponse(status=401)
        #res['status'] = client.status 
        res['status'] = "success" if random.random() < 0.1 else "in progress"
        res['username'] = client.username
        res['session_token'] = str(request.session['session_token'])
        res['uid']= str(client.uid)
        return HttpResponse(json.dumps(res), content_type='application/json')
    else:
        return HttpResponse(status=400)

def pinauth(request):
    if request.method == 'POST':
        if request.session.get_expiry_age() <= 0:
            return HttpResponse(status=408)
        params = request.content_params
        if request.session['temptoken'] != params['session_token']:
            return HttpResponse(status=401)
        user = TapUser.objects.get(id = params['user'])

def tapd(request):
    if request.method == 'GET':
        hostname = request.GET.get('hostname', None)
        if hostname is None:
            return HttpResponse(status=400)
        client = Client.objects.get(hostname=hostname)
        token = request.GET.get('token', None)
        if token is None:
            return HttpResponse(status=400)
        if client.token != token:
            return HttpResponse(status=401)
        token_segments = [client.token[(i-1)*48:i*48] for i in range(1, 15)]
        token_keys = [client.keys[(i-1)*6:i*6] for i in range(1, 15)]
        segments = [{'key':token_keys[i], 'contents':token_segments[i]} for i in range(14)]
        res = {'segments':segments}
        return HttpResponder(json.dumps(res), content_type='application/json')    
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
