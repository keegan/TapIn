from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse

import json
import random

def status(request):
    if request.method == 'GET':

        res = {}
        res['status'] = 'in progress' if random.random() < 0.8 else 'success'
        res['username'] = '2018wzhang'
        return HttpResponse(json.dumps(res), content_type='application/json')
    else:
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
