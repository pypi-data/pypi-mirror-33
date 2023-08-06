""" Base class for Collection objects
"""

import time
import datetime

from rockset.cursor import Cursor
from rockset.exception import InputError
from rockset.query import Query

from bravado.exception import HTTPError

class Resource(object):
    # instance methods
    def __init__(self, client, model, name, **kwargs):
        """Represents a single Rockset collection"""
        self.client = client
        self.model = model
        self.workspace = 'commons'
        self.name = name
        self.dropped = False
        for key in kwargs:
            setattr(self, key, kwargs[key])
        return
    def __str__(self):
        """Converts the collection into a user friendly printable string"""
        return str(vars(self))
    def asdict(self):
        d = vars(self)
        d.pop('client')
        d.pop('model')
        if not self.dropped:
            d.pop('dropped')
        return d
    def describe(self, func):
        kwargs = {}
        kwargs['method'] = func
        kwargs['workspace'] = self.workspace
        kwargs['collection'] = self.name
        kwargs['all'] = True
        return self.client.apicall(**kwargs)
    def drop(self, func):
        kwargs = {}
        kwargs['method'] = func
        kwargs['workspace'] = self.workspace
        kwargs['collection'] = self.name
        self.client.apicall(**kwargs)
        self.dropped = True
        return
    def query(self, q, **kwargs):
        return self.client.query(q=q, collection=self.name, **kwargs)
    def fence(self, func, commit_mark):
        kwargs = {}
        kwargs['method'] = func
        kwargs['workspace'] = self.workspace
        kwargs['collection'] = self.name
        kwargs['poll_max'] = False
        kwargs['commit_mark'] = {'commit_mark': commit_mark.serialize()}
        result = self.client.apicall(**kwargs)
        return result['passed']

    def wait_barrier(self, commit_mark, timeout=None,
                         poll_interval=0.1):
        deadline = None
        if timeout is not None:
            deadline = (datetime.datetime.utcnow() +
                datetime.timedelta(seconds=timeout))
        while True:
            if self.fence(commit_mark):
                return
            if deadline and datetime.datetime.utcnow() >= deadline:
                raise TimeoutError('wait_barrier timeout exceeded')
            time.sleep(poll_interval)


__all__ = [
    'Resource',
]
