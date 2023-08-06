#!/usr/bin/env python
# -*- coding: utf-8 -*-

from notmm.utils.wsgilib import HTTPResponse

__all__ = ['HTTPException', 'HTTPClientError', 'HTTPServerError', 'HTTPNotFound', 'HTTPUnauthorized']

class HTTPException(HTTPResponse, BaseException):
    status_int = 500
    def __init__(self, *args, **kwargs):
        super(HTTPException, self).__init__(**kwargs)

class HTTPClientError(HTTPException):
    status_int = 400 # bad request
class HTTPUnauthorized(HTTPClientError):
    status_int = 401
class HTTPNotFound(HTTPClientError):    
    status_int = 404

