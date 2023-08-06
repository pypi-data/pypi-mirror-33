#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2007-2018 Etienne Robillard <tkadm30@yandex.com>
# All rights reserved.
"""Decorator functions to interact with Schevo databases"""

from functools import wraps
from notmm.controllers.zodb import ZODBController
from notmm.controllers.oauth import GoogleController
from notmm.utils.django_settings import LazySettings

_settings = LazySettings()

__all__ = ('require_oauth', 'with_schevo_database',)

def require_oauth(view_func):
    controller_class = GoogleController
    
    def decorator(view_func, **kwargs):
        #@wraps(view_func, **kwargs)
        def _wrapper(*args, **kwargs):
            req = args[0]
            wsgi_app = controller_class(req, **kwargs)
            def middleware(wsgi_app, env, start_response):
                print 'in middleware!'
                r = wsgi_app.application(env, start_response)
                return r
            return middleware(wsgi_app, req.environ, view_func)
        return wraps(view_func)(_wrapper, **kwargs)
    return decorator(view_func)



def with_schevo_database(dbname, controller_class=ZODBController):
    """
    Decorator that adds a Schevo database object reference
    in the ``request.environ`` dictionary.

    """
    def decorator(view_func, **kwargs):
        #@wraps(view_func, **kwargs)
        def _wrapper(*args, **kwargs):
            req = args[0]
            wsgi_app = controller_class(req, dbname)
            req.environ[wsgi_app.environ_key] = wsgi_app.db
            return view_func(req, **kwargs)
        return wraps(view_func)(_wrapper, **kwargs)
    return decorator

