from django.conf.urls import url

from .views import register, activate


urlpatterns = [
    url(r'^register/', register),
    url(r'^activate/(?P<code>\w+)$', activate), 
]

