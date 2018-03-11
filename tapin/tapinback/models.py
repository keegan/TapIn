from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser
import secrets
import uuid

def gen_token():
    return secrets.token_urlsafe(672)

def gen_keys():
    return secrets.token_urlsafe(84)

def gen_client_token():
    return secrets.token_urlsafe(64)

class TapUser(models.Model):
    token = models.CharField(default=gen_token, max_length=1024)
    keys = models.CharField(default=gen_keys, max_length=144)
    pin = models.CharField(max_length=6)
    id = models.UUIDField(default=uuid.uuid4, primary_key=True)
    userid = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

class Client(models.Model):
    token = models.CharField(default=gen_client_token, max_length=96)
    hostname = models.CharField(max_length=30)
    status = models.CharField(default="nothing", max_length=20)
    username = models.CharField(default="", max_length=20)
