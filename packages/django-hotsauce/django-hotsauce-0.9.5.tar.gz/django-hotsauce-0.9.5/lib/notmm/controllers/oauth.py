#!/usr/bin/env python
# -*- coding: utf-8 -*-
from notmm.controllers.wsgi import WSGIController, sessionmanager
from wsgi_oauth2 import client

__all__ = ['OAuthController']

class OAuthController(WSGIController):
    debug = True
    def __init__(self, **kwargs):
        super(OAuthController, self).__init__(**kwargs)
        
class GoogleController(OAuthController):
    scope = 'email'
    def __init__(self, request, **kwargs):
        super(GoogleController, self).__init__()
        self._request = request
        self._client = client.GoogleClient(
            self.settings.OAUTH2_CLIENT_ID,
            access_token=self.settings.OAUTH2_ACCESS_TOKEN,
            scope=self.scope, 
            redirect_url=self.settings.OAUTH2_REDIRECT_URL,
            )
            
    def application(self, environ, start_response):
        with sessionmanager(environ):
            response = self.get_response(request=self.request)
            response = self._client.wsgi_middleware(response, 
                secret=wsgi_app.settings.SECRET_KEY, 
                login_path=wsgi_app.settings.OAUTH2_LOGIN_URL)

        #assert 'REMOTE_USER' in response.environ, 'Eat Shit Mr Nothing Personal!'
        self.logger('Wazzup bro!!!')
        return response
