#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import traceback
import logging

from notmm.utils.template import RequestContext 
from notmm.utils.wsgilib import (
    HTTPNotModifiedResponse, 
    HTTPResponse, 
    HTTPException
    )

from datetime               import datetime
from time                   import ctime

from .utils                  import get_template_loader, TemplateException

TemplateLoader = get_template_loader()

log = logging.getLogger('notmm.utils.template')

__all__ = ['direct_to_template', 'render_template']

def render_template(template_name, ctx, charset='UTF-8', disable_unicode=False):
    try:
        t = TemplateLoader.get_template(template_name)
        
        if t.output_encoding != charset:
            log.debug("Fixing output encoding to %s" % charset)
            setattr(t, 'output_encoding', charset)

        if charset == 'UTF-8' and not disable_unicode:
            chunk = t.render_unicode(data=ctx)
        else:
            chunk = t.render(data=ctx)
            
    except TemplateException as e:
        # Template error processing a unicode template
        # with Mako
        exc_type, exc_value, exc_tb = sys.exc_info()
        
        rawtb = ''.join([item for item in traceback.format_tb(exc_tb)])
        
        return HTTPException(
            'error processing template: %s'
            '\n'
            '%r'
            '\n'
            '%s' % (template_name, repr(e), rawtb))
    return t, chunk

def direct_to_template(request, template_name, extra_context={}, 
    status=200, charset='UTF-8', mimetype='text/html', 
    disable_unicode=False):
    """
    Generic view for returning a Mako template inside a simple 
    ``HTTPResponse`` instance. 
    
    """
    # Make sure ctx has our stuff
    if not isinstance(extra_context, RequestContext):
        ctx = RequestContext(request, extra_context)
    else:
        ctx = extra_context

    #import pdb; pdb.set_trace()
    t, chunk = render_template(template_name, ctx)
    
    #httpheaders = HeaderDct([
    #    ('Last-Modified', datetime.fromtimestamp(t.last_modified).ctime()), 
    #    ('Date', ctime()),
    #    ('If-None-Match', str(hashlib.md5(chunk).hexdigest()))
    #    ])
    
    #print httpheaders
    #request.environ.update(httpheaders)

    return HTTPResponse(content=chunk, request=request, status=status, mimetype=mimetype)

