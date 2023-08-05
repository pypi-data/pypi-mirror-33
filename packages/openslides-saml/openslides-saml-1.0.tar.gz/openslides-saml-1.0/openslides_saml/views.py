from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout
from django.contrib.auth import get_user_model
from django.http import (
    HttpResponse,
    HttpResponseRedirect,
    HttpResponseServerError,
)
from django.views.generic import View
from onelogin.saml2.auth import OneLogin_Saml2_Auth
from onelogin.saml2.utils import OneLogin_Saml2_Utils

from .settings import SamlSettings


class IndexView(View):
    """
    View for the SAML Interface.
    """
    state = {}

    def __init__(self, *args, **kwargs):
        return super().__init__(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.get(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        saml_request, auth = self.get_saml_auth(request)

        if 'sso' in request.GET:
            return HttpResponseRedirect(auth.login())

        elif 'sso2' in request.GET:
            return_to = OneLogin_Saml2_Utils.get_self_url(saml_request) + '/'
            return HttpResponseRedirect(auth.login(return_to))

        elif 'slo' in request.GET:
            name_id = request.session.get('samlNameId')
            session_index = request.session.get('samlSessionIndex')
            auth_logout(request)
            if name_id is None and session_index is None:
                return HttpResponseRedirect('/')
            else:
                request.session['samlNameId'] = None
                request.session['samlSessionIndex'] = None
                return HttpResponseRedirect(auth.logout(name_id=name_id, session_index=session_index))

        elif 'acs' in request.GET:
            auth.process_response()
            errors = auth.get_errors()

            if errors:
                return HttpResponseServerError(content=', '.join(errors))
            else:
                request.session['samlNameId'] = auth.get_nameid()
                request.session['samlSessionIndex'] = auth.get_session_index()
                self.login_user(request, auth.get_attributes())

                if 'RelayState' in request.POST and OneLogin_Saml2_Utils.get_self_url(saml_request) != request.POST['RelayState']:
                    return HttpResponseRedirect(auth.redirect_to(request.POST['RelayState']))
                else:
                    return HttpResponseRedirect('/')

        elif 'sls' in request.GET:
            url = auth.process_slo(delete_session_cb=lambda: request.session.flush())
            errors = auth.get_errors()

            if errors:
                return HttpResponseServerError(content=', '.join(errors))
            else:
                return HttpResponseRedirect(url or '/')

        else:
            return HttpResponseRedirect('/')

    def login_user(self, request, attributes):
        User = get_user_model()

        mapping = SamlSettings.get_attribute_mapping()

        queryargs = self.get_queryargs(mapping, attributes)
        user, created = User.objects.get_or_create(**queryargs)
        if not created:
            self.update_user(user, queryargs['defaults'])
        auth_login(request, user)

    def get_queryargs(self, mapping, attributes):
        queryargs = {}
        defaults = {}
        for key, (value, lookup) in mapping.items():
            attribute = attributes.get(key)
            if isinstance(attribute, list):
                attribute = ', '.join(attribute)

            if lookup:
                queryargs[value] = attribute
            else:
                defaults[value] = attribute

        queryargs['defaults'] = defaults
        return queryargs

    def update_user(self, user, attributes):
        changed = False
        for key, value in attributes.items():
            user_attr = getattr(user, key)
            if user_attr != value:
                setattr(user, key, value)
                changed = True
        if changed:
            user.save()

    def get_saml_auth(self, request):
        saml_request = dict(SamlSettings.get_request_settings())
        # Update not existing keys
        saml_request['https'] = saml_request.get('https', 'on' if request.is_secure() else 'off')
        saml_request['http_host'] = saml_request.get('http_host', request.META['HTTP_HOST'])
        saml_request['script_name'] = saml_request.get('script_name', request.META['PATH_INFO'])
        saml_request['server_port'] = saml_request.get('server_port', request.META['SERVER_PORT'])
        # add get and post data
        saml_request['get_data'] = request.GET.copy()
        saml_request['post_data'] = request.POST.copy()
        return saml_request, OneLogin_Saml2_Auth(saml_request, SamlSettings.get())


def serve_metadata(request, *args, **kwargs):
    settings = SamlSettings.get()
    metadata = settings.get_sp_metadata()
    errors = settings.validate_metadata(metadata)

    if len(errors) is not 0:
        return HttpResponseServerError(content=', '.join(errors))
    else:
        return HttpResponse(content=metadata, content_type='text/xml')


def is_saml_user(request, *args, **kwargs):
    content = 'false'
    if request.user.is_authenticated():
        name_id = request.session.get('samlNameId')
        session_index = request.session.get('samlSessionIndex')
        if name_id is not None and session_index is not None:
            content = 'true'
    return HttpResponse(content=content, content_type='application/json')
