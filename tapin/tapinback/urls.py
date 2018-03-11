from django.conf.urls import url

from . import views
urlpatterns = [
    url(r'status', views.status, name='status'),
    url(r'pinauth', views.pinauth, name='pinauth'),
    url(r'tapd', views.tapd, name='tapd')
]
