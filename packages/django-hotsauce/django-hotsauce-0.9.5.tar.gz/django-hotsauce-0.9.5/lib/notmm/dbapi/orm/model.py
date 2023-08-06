#!/usr/bin/env python
"""Base model classes for django-hotsauce"""
import logging
from notmm.dbapi.orm import RelationProxy

log = logging.getLogger(__name__)

__all__ = ('ModelManager',)

class ModelManager(object):

    model = None # Category
    db_connection = None
    def __init__(self, connection=None, model=None, **kwargs):
        self.kwargs = kwargs
        if model is not None:
            self.model = model
        if connection is not None:
            self.db_connection = connection
        self.objects = RelationProxy(getattr(self.db_connection, self.model))
        
    def __str__(self):
        return "<ModelManager: %s>" % self.model
    
    def save(self, commit=True):
        lock = self.db.write_lock()
        with lock:
            #if self.initialized:
            tx = self.extent.t.create(**self.kwargs)
            if commit:
                self.db.execute(tx)
                self.db._commit()
        lock.release()
        return self

