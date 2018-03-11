from django.db import models
import secrets

class TapUser(models.Model):
    token = models.BinaryField(default=secrets.token_bytes(896))
    pin = models.CharField(max_length=6)
    id = models.UUIDField(default=uuid.uuid4, primary_key=True)
    userid = models.ForeignKey(User)
