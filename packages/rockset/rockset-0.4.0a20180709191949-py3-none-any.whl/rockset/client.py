"""
Introduction
------------
Client objects allow you to connect securely to the Rockset service.
All other API calls require a valid Client object.

In order to create a Client object, you will need a valid Rockset
API key. If you have access to the Rockset Console, then you can use
the console to create an API key. If not, please contact the
Rockset team at support@rockset.io

::

    from rockset import Client

    # connect securely to Rockset production API servers
    client = Client(api_server='api.rockset.io',
                    api_key='adkjf234rksjfa23waejf2')

You can manage your api_key credentials using the ``rock`` command-line tool.
Run the ``rock configure`` tool to setup one or more api_key credentials and
select the one that you want all ``rock`` commands and the Python Rockset
Client to use. Once setup, you should expect the following to work.

::

    from rockset import Client

    # connect to the active credentials profile
    # you can see see the active profile by running ``rock configure ls``
    rs = Client()

    # connect to credentials profile 'prod' as defined by ``rock configure``
    rs = Client(profile='prod')


Example usage
-------------

Connect to Rockset API server and then subsequently use the client object
to retrieve collections.

::

    from rockset import Client

    # connect securely to Rockset dev API server
    rs = Client(api_server='api-us-west-2.rockset.io',
                api_key='adkjf234rksjfa23waejf2')

    # list all collections in the account that I have access to
    all_collections = rs.Collection.list()

    # create a new collection; returns a collection object
    new_collection = rs.Collection.create('customer_info')

    # get details of an existing collection as a collection object
    users = rs.retrieve('users')

"""
import bravado
from bravado.client import SwaggerClient
from bravado.requests_client import RequestsClient, Authenticator
import collections
import logging
import os
import platform
import requests
import time
import tempfile
import yaml
import simplejson as json

import rockset

from rockset.collection import Collection
from rockset.credentials import Credentials
from rockset.cursor import Cursor
from rockset.exception import (AuthError, InputError, LimitReached,
    NotYetImplemented, RequestTimeout, ResourceSuspendedError, ServerError,
    TransientServerError)
from rockset.query import Query
from rockset.source import Source

class Client(object):
    """Securely connect to Rockset using an API key.

    Optionally, an alternate API server host can also be provided.
    If you have configured credentials using the ``rock configure``
    command, then those credentials will act as fall back values, when
    none of the api_key/api_server parameters are specified.

    Args:
        api_key (str): API key
        api_server (str): API server URL. Will default to https if URL
            does not specify a scheme.
        profile (str): Optionally, you can also specify name of your
            credentials profile setup using ``rock configure``

    Returns:
        Client: A Client object

    Raises:
        ValueError: when API key is not specified and
                    could not be fetched from ``rock`` CLI
                    credentials or api_server URL is invalid.
    """

    #: Maximum allowed length of a collection
    MAX_NAME_LENGTH = 2048

    #: Maximum allowed length of a field name
    MAX_FIELD_NAME_LENGTH = 10 * 1024

    #: Maximum allowed size of a field value
    MAX_FIELD_VALUE_BYTES = 4 * 1024 * 1024

    #: Maximum allowed length of ``_id`` field value
    MAX_ID_VALUE_LENGTH = 10 * 1024

    #: Maximum allowed levels of depth for nested documents
    MAX_NESTED_FIELD_DEPTH = 30

    #: Maximum allowed size of a single document
    MAX_DOCUMENT_SIZE_BYTES = 40 * 1024 * 1024

    # Config directory path
    @classmethod
    def config_dir(cls):
        """Returns name of the directory where Rockset credentials, config,
        and logs are stored.

        Defaults to ``"~/.rockset/"``

        Can be overriddden via ``ROCKSET_CONFIG_HOME`` env variable.
        """
        if 'ROCKSET_CONFIG_HOME' in os.environ:
            homedir = '%s/' % os.path.expanduser(os.environ['ROCKSET_CONFIG_HOME'])
        elif platform.system() == 'Windows':
            homedir = os.getenv('ROCKSET_CONFIG_HOME') + '\\AppData\\Local\\'
        else:
            homedir = os.path.expanduser('~')

        # if user does not have home dir, use tmpdir
        if not os.path.isdir(homedir):
            homedir = tempfile.gettempdir()

        # config dir is `homedir`/.rockset
        return os.path.join(homedir, '.rockset')

    # Constructor
    def __init__(self,
                 api_key=None,
                 api_server=None,
                 profile=None,
                 **kwargs):
        # inititalize api key and server
        self.api_key = api_key
        self.api_server = api_server

        # if both api key and server were not set, default to active profile
        if api_key is None or api_server is None:
            # read credentials from creds file if not supplied
            creds = Credentials()
            active_profile = creds.get(profile=profile)
            if api_key is None:
                self.api_key = active_profile.get('api_key', None)
            if api_server is None:
                self.api_server = active_profile.get('api_server', None)

        # no api_key => no soup for you
        if self.api_key is None:
            raise ValueError("api_key need to be specified")

        # default to api.rockset.io
        if self.api_server is None:
            self.api_server = 'api.rockset.io'

        # peel http scheme from api_server setting
        if self.api_server[:7] == 'http://':
            self.api_server = self.api_server[7:]
            self.scheme = 'http'
        elif self.api_server[:8] == 'https://':
            self.api_server = self.api_server[8:]
            self.scheme = 'https'
        else:
            self.scheme = 'https'

        # init swagger client
        self.swagger_client = self._create_swagger_client()

        # create instances of helper classes
        self.Collection = ClientResource(resource=Collection,
            client=self, model=self.swagger_client.All)
        self.Source = ClientSource(client=self)

        # init config dir
        self.config_dir = Client.config_dir()
        if not os.path.isdir(self.config_dir):
            os.makedirs(self.config_dir)

        # init logging
        self.logger = logging.getLogger(__name__)
        self.logger.addHandler(logging.NullHandler())

        return

    def _create_swagger_client(self):
        # get swagger spec
        # (TODO): fetch it from www and cache it in ~/.rockset
        swagger_dir = os.path.join(os.path.dirname(__file__), 'swagger')
        with open(os.path.join(swagger_dir, 'apiserver.yaml')) as f:
            spec_dict = yaml.load(f.read())

        # override the host
        spec_dict['host'] = self.api_server
        # defaults to https, but override scheme so our tests can use this
        spec_dict['schemes'] = [self.scheme]

        http_client = RequestsClient()
        if 'HTTPS_PROXY' in os.environ:
            http_client.session.proxies['https'] = os.environ['HTTPS_PROXY']
        if 'HTTP_PROXY' in os.environ:
            http_client.session.proxies['http'] = os.environ['HTTP_PROXY']

        # setup bravado config
        bravado_config = {
            'also_return_response': False,
            'validate_requests': False,
            'validate_responses': False,
            'use_models': False,
        }

        return SwaggerClient.from_spec(
            spec_dict,
            http_client=http_client,
            config=bravado_config)

    def _get_request_options(self):
        return {
            "connect_timeout": 3.0,
            "headers": {
                "Authorization": "ApiKey {}".format(self.api_key),
                "x-rockset-version": rockset.version(),
            }
        }

    def apicall(self, method, *args, **kwargs):
        try:
            timeout = kwargs.pop('timeout', None)
            if 'org' not in kwargs:
                kwargs['org'] = 'self'
            kwargs['_request_options'] = self._get_request_options()
            start_time = time.time()
            result = method(*args, **kwargs).result(timeout=timeout)
        except bravado.exception.HTTPUnauthorized as e:
            raise AuthError(response=e.response) from None
        except (bravado.exception.HTTPForbidden,
                bravado.exception.HTTPPayloadTooLarge) as e:
            raise LimitReached(response=e.response) from None
        except bravado.exception.HTTPNotImplemented as e:
            raise NotYetImplemented(response=e.response) from None
        except (bravado.exception.HTTPServiceUnavailable,
                bravado.exception.HTTPGatewayTimeout) as e:
            raise TransientServerError(response=e.response) from None
        except (bravado.exception.HTTPBadGateway,
                requests.exceptions.ConnectionError) as e:
            message = "error connecting to {}://{}".format(
                self.scheme, self.api_server)
            elapsed = int(time.time() - start_time)
            raise RequestTimeout(message=message, timeout=elapsed) from None
        except bravado.exception.HTTPClientError as e:
            raise InputError(response=e.response) from None
        except bravado.exception.HTTPServerError as e:
            raise ServerError(response=e.response) from None
        except bravado.exception.HTTPError as e:
            if e.status_code == 530:
                raise ResourceSuspendedError(response=e.response) from None
            raise e
        except requests.exceptions.ReadTimeout as e:
            elapsed = int(time.time() - start_time)
            message = "request timed out after {} secs".format(elapsed)
            raise RequestTimeout(message=message, timeout=elapsed) from None
        except json.scanner.JSONDecodeError as e:
            raise InputError(code='-', message=str(e), type='InputError') from e
        except requests.exceptions.RequestException as e:
            raise InputError(code='-', message=str(e), type='InputError') from e
        return result

    def list(self, **kwargs):
        """Returns list of all collections.

        Returns:
            List: A list of Collection objects
        """
        kwargs['method'] = self.swagger_client.All.list
        kwargs['workspace'] = 'commons'
        return self.apicall(**kwargs)['data']

    def retrieve(self, name):
        """Retrieves a single collection

        Args:
            name (str): Name of the collection to be retrieved

        Returns:
            Collection: Collection object
        """
        kwargs = {}
        kwargs['method'] = self.swagger_client.All.describe
        kwargs['workspace'] = 'commons'
        kwargs['collection'] = name
        kwargs['all'] = False
        resource = self.apicall(**kwargs)['data']
        rname = resource.pop('name')
        rtype = resource.pop('type')
        if rtype == 'COLLECTION':
            return Collection(client=self, model=self.swagger_client.All,
                name=rname)
        raise TypeError('cannot recognize type {} for resource {}'.format(
            rtype, name))

    def query(self, q, collection=None, **kwargs):
        """Execute a query against Rockset.

        This method prepares the given query object and binds it to
        a Cursor_ object, and returns that Cursor object. The request is not
        actually dispatched to the backend until the results are fetched
        from the cursor.

        Input query needs to be supplied as a Query_ object.

        Cursor objects are iterable, and you can iterate through a cursor to
        fetch the results. The entire result data set can also be retrieved
        from the cursor object using a single ``results()`` call.

        When you iterate through the cursor in a loop, the cursor objects
        implement automatic pagination behind the scenes. If the query
        returns a large number of results, with automatic pagination,
        only a portion of the results are buffered into the cursor at a
        time. As the cursor iterator reaches the end of the current batch,
        it will automatically issue a new query to fetch the next batch
        and seamlessly resume. Cursor's default iterator uses batch size
        of 10,000, and you can create an iterator of a different batch size
        using the iter() method in the cursor object.

        Example::

            ...
            rs = Client()
            cursor = rs.query(q)

            # fetch all results in 1 go
            all_results = cursor.results()

            # iterate through all results;
            # automatic pagination with default iterator batch size of 100
            # if len(all_results) == 21,442, then as part of looping
            # through the results, three distinct queries would be
            # issued with (limit, skip) of (10000, 0), (10000, 10000),
            # (10000, 20000)
            for result in cursor:
                print(result)

            # iterate through all results;
            # automatic pagination with iterator batch size of 20,000
            # if len(all_results) == 21,442, then as part of looping
            # through the results, two distinct queries would have
            # been issued with (limit, skip) of (20000, 0), (20000, 20000).
            for result in cursor.iter(20000):
                print(result)
            ...

        Args:
            q (Query): Input Query object
            timeout (int): Client side timeout. When specified, RequestTimeout_ \
            exception will be thrown upon timeout expiration. By default, \
            the client will wait indefinitely until it receives results or \
            an error from the server.

        Returns:
            Cursor: returns a cursor that can fetch query results with or
            without automatic pagination
        """
        if not isinstance(q, Query):
            raise NotImplementedError(
                'query of type {} not supported'.format(type(q)))
        if not collection:
            collection = q.get_source()
            if not collection:
                raise ValueError('please specify target collection to '
                    'run this query against')
        kwargs['method'] = self.swagger_client.All.query
        kwargs['workspace'] = 'commons'
        kwargs['collection'] = collection
        return Cursor(q=q, sexpr=True, sql=False,
            queryf=self.apicall, queryfargs=kwargs)

    def sql(self, q, **kwargs):
        if not isinstance(q, Query):
            raise NotImplementedError(
                'query of type {} not supported'.format(type(q)))
        kwargs['method'] = self.swagger_client.All.sql
        return Cursor(q=q, sexpr=False, sql=True,
            queryf=self.apicall, queryfargs=kwargs)


Client.sql.__doc__ = Client.query.__doc__.replace('rs.query(', 'rs.sql(')

class ClientResource(object):
    def __init__(self, client, model, resource):
        self.client = client
        self.model = model
        self.cls = resource

    def create(self, name, description=None, **kwargs):
        sources = [dict(s) for s in kwargs.pop('sources', [])]
        return self.cls.create(name=name, description=description,
            sources=sources, client=self.client, model=self.model, **kwargs)

    def list(self):
        return self.cls.list(client=self.client, model=self.model)

    def retrieve(self, name):
        return self.cls.retrieve(name=name, client=self.client,
            model=self.model)

class ClientSource(object):
    def __init__(self, client):
        self.client = client

    def s3(self, *args, **kwargs):
        return Source.s3(*args, **kwargs)

    def collection(self, *args, **kwargs):
        return Source.collection(*args, **kwargs)


__all__ = [
    'Client',
]
