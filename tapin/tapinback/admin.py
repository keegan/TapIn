from django.contrib import admin

from .models import Client, TapUser

# Register your models here.

admin.site.register(Client)
admin.site.register(TapUser)
