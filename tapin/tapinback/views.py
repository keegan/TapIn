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
        params = request.content_params
        client = Client.objects.get(hostname=params['hostname'])
        res['status'] = client.status 
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
    return HttpResponse(status=500)

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
