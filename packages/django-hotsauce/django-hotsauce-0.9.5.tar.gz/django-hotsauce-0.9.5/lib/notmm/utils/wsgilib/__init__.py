#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2007-2018 Etienne Robillard <tkadm30@yandex.com>
# All rights reserved.
"""Mostly Random WSGI Utilities.

Useful for learning and education purposes only. Deploy
in production at your own risks... ;-)
"""

from .response import *
from .request  import HTTPRequest
from .exc      import HTTPClientError, HTTPException, HTTPUnauthorized
from .multidict import MultiDict
