from molo.usermetadata import views

from django.conf.urls import url


urlpatterns = [
    url(r'^persona/$', views.PersonaView.as_view(), name='persona'),
    url(
        r'^persona/skip/$',
        views.skip_persona, name='skip_persona'),
    url(
        r'^persona/(?P<persona_slug>[\w-]+)/$',
        views.set_persona, name='set_persona'),
]
