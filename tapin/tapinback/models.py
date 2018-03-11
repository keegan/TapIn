from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser
import secrets
import uuid

def gen_token():
    return secrets.token_bytes(672)

class TapUser(models.Model):
    token = models.BinaryField(default=gen_token)
    pin = models.CharField(max_length=6)
    id = models.UUIDField(default=uuid.uuid4, primary_key=True)
    userid = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
