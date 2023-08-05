from django.conf.urls import url
from django.views.decorators.csrf import csrf_exempt

from . import views

urlpatterns = [
    url(r'^saml/$', csrf_exempt(views.IndexView.as_view())),
    url(r'^saml/metadata/$', views.serve_metadata),
    url(r'^saml/isSamlUser/$', views.is_saml_user),
]
