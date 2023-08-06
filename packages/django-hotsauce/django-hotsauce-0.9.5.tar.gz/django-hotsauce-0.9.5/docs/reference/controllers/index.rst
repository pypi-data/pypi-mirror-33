BaseController API
===================

:Author: Etienne Robillard <tkadm30@yandex.com>
:Version: 0.9.4

Introduction
-------------

The ``notmm.controllers`` package provides a high-performance API for Django apps to extend from 
the ``BaseController`` class.

Modules
--------

``BaseController``
~~~~~~~~~~~~~~~~~~~

The ``notmm.controllers.base.BaseController`` module requires the ``Werkzeug`` library to operate properly. 

Its purpose is to provide an abstract base class and a set of common methods to derived subclasses.


``WSGIController``
~~~~~~~~~~~~~~~~~~~

The ``notmm.controllers.wsgi.WSGIController`` class provides the core wrapper for Django apps to extend from. 

It is essentially a thin but valid WSGI request and response middleware to sit between Django and nginx. 

Django 1.11 or higher is recommended for optimal results. 

In addition, the ``WSGIController`` supports many exclusive features such as:

- Thread-local request/response handling based on ``Werkzeug`` and ``gevent``.
- Customized Django exception handling.
- Django settings autoloading via Proxy-style attribute delegation.
- Allow developers to embed Django applications using a shared library. (``Cython``)
- Makes the Pylons developers to build pyramids instead of pylons.. :)

Exception Handling
-------------------

.. The following is out-of-date...

To register a custom WSGI response handler ::

    from notmm.controllers.wsgi import WSGIController
    
    wsgi_app = WSGIController()
    wsgi_app.sethandle('handle401', 'myapp.views.handle401')
    wsgi_app.sethandle('handle404', 'myapp.views.handle404')
    wsgi_app.sethandle('handle500', 'myapp.views.handle500') 

Notes
------

* The name `BaseController' is inspired from the Pylons (Pyramid) framework.

See Also
---------

The ``session`` and ``authentication`` chapters.

