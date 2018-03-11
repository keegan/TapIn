from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.views.decorators.csrf import csrf_exempt

from .models import Client, TapUser

import json
import random
import secrets
import uuid
import base64


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
        res['status'] = client.status
        if client.status == "failure":
            client.status = "nothing"
            client.save()
        res['username'] = client.username
        res['session_token'] = str(request.session['session_token'])
        res['uid'] = str(client.uid)
        return HttpResponse(json.dumps(res), content_type='application/json')
    else:
        return HttpResponse(status=400)


def pinauth(request):
    if request.method == 'POST':
        if request.session.get_expiry_age() <= 0:
            return HttpResponse(status=408)
        session_token = request.POST.get('session_token', None)
        if session_token is None:
            return HttpResponse(status=400)
        if request.session['session_token'] != session_token:
            return HttpResponse(status=401)
        uid = request.POST.get('uid', None)
        if uid is None:
            return HttpResponse(status=400)
        print(uid)
        print(uuid.UUID(uid))
        user = TapUser.objects.get(id=uuid.UUID(uid))
        pin = request.POST.get('pin', None)
        hostname = request.POST.get('hostname', None)
        if hostname is None:
            return HttpResponse(status=400)
        client = Client.objects.get(hostname=hostname)
        if pin is None:
            return HttpResponse(status=400)
        if user.pin != pin:
            client.status = "failure"
            client.save()
            return render(request, 'failure.html')
        client.status = "nothing"
        client.save()
        return render(request, "success.html")

@csrf_exempt
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
        uid = request.GET.get('uid', None)
        if uid is None:
            return HttpResponse(status=400)
        user = TapUser.objects.get(id=uid)
        client.status = "in progress"
        client.username = user.userid.username
        client.uid = uid
        token_bytes = base64.urlsafe_b64decode(user.token + ("=" * (-len(user.token) % 4)))
        key_bytes = base64.urlsafe_b64decode(user.keys + ("=" * (-len(user.keys) % 4)))
        token_segments = [base64.urlsafe_b64encode(token_bytes[(i - 1) * 48:i * 48]).decode("UTF-8").replace('=', '') for i in
                          range(1, 15)]
        token_keys = [base64.urlsafe_b64encode(key_bytes[(i - 1) * 6:i * 6]).decode("UTF-8").replace('=', '') for i in range(1, 15)]
        segments = [{'key': token_keys[i], 'contents': token_segments[i]} for i in range(14)]
        res = {'segments': segments}
        client.save()
        return HttpResponse(json.dumps(res), content_type='application/json')
    elif request.method == 'POST':
        hostname = request.POST.get('hostname', None)
        if hostname is None:
            return HttpResponse(status=400)
        client = Client.objects.get(hostname=hostname)
        token = request.POST.get('token', None)
        if token is None:
            return HttpResponse(status=400)
        if client.token != token:
            return HttpResponse(status=401)
        success = request.POST.get('success', None)
        if success is None:
            return HttpResponse(status=400)
        if success == "True":
            client.status = "success"
        else:
            client.status = "failure"
        client.save()
        return HttpResponse(status=200)
    return HttpResponse(status=400)

# from .forms import AuthForm
# Create your views here.
# def formRequest(request):
# if request.method == "POST":
# form = AuthForm(request.POST)
# if form.isValid():
# process data
# return to another url v
# return HTTPResponseDirect(insert url here)
# else:
#	form = AuthForm()

# return render(request, "backui.html", {'form':form})
