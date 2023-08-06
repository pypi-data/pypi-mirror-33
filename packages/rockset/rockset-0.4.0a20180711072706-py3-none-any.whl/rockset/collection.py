"""
Introduction
------------
Collection objects repesents a single Rockset collection.
These objects are generally created using a Rockset Client_
object using methods such as::

    from rockset import Client

    # connect to Rockset
    rs = Client(api_key=...)

    # create a new collection
    user_events = rs.Collection.create('user-events')

    # retrieve an existing collection
    users = rs.retrieve('users')

You can add documents to the collection using the ``add_docs()`` method. Each
document in a collection is uniquely identified by its ``_id`` field.

If documents added have ``_id`` fields that match existing documents,
then their contents will be merged. Otherwise, the new documents will be
added to the collection.

You can remove documents from a collection using the ``remove_docs()`` method.

Refer to the Query_ module for documentation and examples on how to query
collections.

Example usage
-------------
::

    from rockset import Client, Q, F

    # connect securely to Rockset
    rs = Client()

    # retrieve the relevant collection
    emails = rs.Collection.retrieve('emails')

    # look for all emails to johndoe that contains the term 'secret'
    johndoe_secret_q = Q('emails').where(
        (F["to"].startswith('johndoe@')) & (F["body"][:] == 'secret')
    )

    # query the collection
    docs = rs.query(query=johndoe_secret_q).results()

.. _Collection.create:

Create a new collection
-----------------------
Creating a collection using the Client_ object is as simple as
calling ``client.Collection.create("my-new-collection")``::

    from rockset import Client
    rs = Client()
    new_collection = rs.Collection.create("my-new-collection")

.. _Collection.list:

List all collections
--------------------
List all collections using the Client_ object using::

    from rockset import Client
    rs = Client()
    collections = rs.list()

.. _Collection.retrieve:

Retrieve an existing collection
-------------------------------
Retrive a collection to run various operations on that collection
such as adding or removing documents or executing queries::

    from rockset import Client
    rs = Client()
    users = rs.retrieve('users')


.. _Collection.describe:

Describe an existing collection
-------------------------------
The ``describe`` method can be used to fetch all the details about the collection
such as what data sets act as the collection's sources, various performance and
usage statistics::

    from rockset import Client
    rs = Client()
    users = rs.retrieve('users')
    print(users.describe())

.. _Collection.drop:

Drop a collection
-----------------
Use the ``drop()`` method to remove a collection permanently from Rockset.

.. note:: This is a permanent and non-recoverable operation. Beware.

::

    from rockset import Client
    rs = Client()
    users = rs.retrieve('users')
    users.drop()

.. _Collection.add_docs:

Add documents to a collection
-----------------------------
Python dicts can be added as documents to a collection using the ``add_docs``
method. Documents are uniquely identified by the ``_id`` field. If an input
document does not have an ``_id`` field, then an unique id will be assigned
by Rockset.

If the ``_id`` field of an input document does not match an existing document,
then a new document will be created.

If the ``_id`` field of an input document matches an existing document,
then the new document will be merged with the existing document::

    from rockset import Client
    import json

    rs = Client()
    users = rs.Collection.retrieve('users')
    with open('my-json-array-of-dicts.json') as data_fh:
        ret = users.add_docs(json.load(data_fh))

.. _Collection.remove_docs:

Delete documents from a collection
----------------------------------
Remove documents from a collection using the ``remove_docs`` method::

    from rockset import Client

    rs = Client()
    users = rs.Collection.retrieve('users')
    users_to_remove = ['user007', 'user042', 'user435']
    docs_to_remove = [{'_id': u} for u in users_to_remove]
    ret = users.remove_docs(docs_to_remove)

"""
from .exception import InputError
from .query import Query
from .resource import Resource
from .commit_mark import CommitMark

from bravado.exception import HTTPError

class Collection(Resource):
    @classmethod
    def create(cls, name, description=None, sources=None, **kwargs):
        """Creates a new Rockset collection.

        Use it via rockset.Client().Collection.create()

        Only alphanumeric characters, ``_``, ``-`` and ``.`` are allowed
        in collection names.

        Args:
            name (str): name of the collection to be created.
            description (str): a human readable description of the collection
            sources (Source): array of Source objects that defines the set
                of input data sources for this collection

        Returns:
            Collection: Collection object
        """
        if 'client' not in kwargs or 'model' not in kwargs:
            raise ValueError('incorrect API usage. '
                'use rockset.Client().Collection.create() instead.')
        client = kwargs.pop('client')
        model = kwargs.pop('model')
        func = model.create
        request = kwargs.copy()
        request['name'] = name
        request['type'] = 'COLLECTION'
        request['description'] = description
        request['sources'] = sources

        kwargs = {}
        kwargs['method'] = func
        kwargs['workspace'] = 'commons'
        kwargs['request'] = request
        collection = client.apicall(**kwargs)['data']
        return cls(client=client, model=model, **collection)

    @classmethod
    def retrieve(cls, name, **kwargs):
        """Retrieves details of a single collection

        Use it via rockset.Client().Collection.retrieve()

        Args:
            name (str): Name of the collection

        Returns:
            Collection: Collection object
        """
        if 'client' not in kwargs or 'model' not in kwargs:
            raise ValueError('incorrect API usage. '
                'use rockset.Client().Collection.create() instead.')
        c = cls(name=name, **kwargs)
        c.describe()
        return c

    @classmethod
    def list(cls, **kwargs):
        """Returns list of all collections.

        Use it via rockset.Client().Collection.list()

        Returns:
            List: A list of Collection objects
        """
        if 'client' not in kwargs or 'model' not in kwargs:
            raise ValueError('incorrect API usage. '
                'use rockset.Client().Collection.list() instead.')
        client = kwargs.pop('client')
        model = kwargs.pop('model')

        kwargs = {}
        kwargs['method'] = model.list
        kwargs['workspace'] = 'commons'
        collections = client.apicall(**kwargs)['data']
        return [cls(client=client, model=model, **c) for c in collections]

    def __init__(self, *args, **kwargs):
        kwargs['type'] = 'COLLECTION'
        super(Collection, self).__init__(*args, **kwargs)
        self.docs_per_call = 1000

    def _chopper(self, docs):
        return [ docs[i:i + self.docs_per_call]
            for i in range(0, len(docs), self.docs_per_call) ]

    def _validate_doclist(self, docs):
        if type(docs) != list:
            raise InputError(message='arg "docs" is not a list of dicts')
        for doc in docs:
            if type(doc) != dict:
                raise InputError(message='cannot add a document that is not a dict')

    # instance methods
    def describe(self):
        """Returns all properties of the collection as a dict.

        Returns:
            dict: properties of the collection
        """
        func = self.model.describe
        return super(Collection, self).describe(func=func)

    def drop(self):
        """Deletes the collection represented by this object.

        If successful, the current object will contain
        a property named ``dropped`` with value ``True``

        Example::

            ...
            print(my_coll.asdict())
            my_coll.drop()
            print(my_coll.dropped)       # will print True
            ...
        """
        func = self.model.drop
        super(Collection, self).drop(func=func)
        return

    def query(self, q, timeout=None, flood_all_leaves=False):
        return super(Collection, self).query(q, timeout=timeout,
                                             flood_all_leaves=flood_all_leaves)
    def add_docs(self, docs, timeout=None):
        """Adds or merges documents to the collection. Provides document
        level atomicity.

        Documents within a collection are uniquely identified by the
        ``_id`` field.

        If the ``_id`` field of an input document does not match with
        any existing collection documents, then the input document will
        be inserted.

        If the ``_id`` field of an input document matches with an
        existing collection document, then the input document will be
        merged atomically as described below:

        * All fields present in both the input document and the collection
          document will be updated to values from the input document.
        * Fields present in the input document but not the collection
          document will be inserted.
        * Fields present in the collection document but not the input
          document will be left untouched.

        All fields within every input document will be inserted or updated
        atomically. No atomicity guarantees are provided across two different
        documents added.

        Args:
            docs (list of dicts): new documents to be added or merged
            timeout (int): Client side timeout. When specified,
                RequestTimeout_ exception will
                be thrown upon timeout expiration. By default, the client
                will wait indefinitely until it receives results or an
                error from the server.

        Returns:
            Dict: The response dict will have 2 fields: ``data`` and
            ``commit_mark``.

            The ``data`` field will be a list of document status records,
            one for each input document indexed in the same order as the list
            of input documents provided as part of the request. Each of those
            document status records will have fields such as the document
            ``_id``, ``_collection`` name, ``status`` describing if that
            particular document add request succeeded or not, and an optional
            ``error`` field with more details.

            The ``commit_mark`` is an opaque object that uniquely identifies
            this particular add document batch request. You can pass the
            ``commit_mark`` to the fence API, to enquire if Rockset's indexes
            have fully indexed the add document batch and subsequent queries
            to the collection will include those new document updates.
        """
        self._validate_doclist(docs)
        addFunc = self.model.addDocuments

        # chunk docs to operate in batches
        retval = []
        commit_mark = None
        for chunk in self._chopper(docs):
            request={'data': chunk}
            kwargs = {}
            kwargs['method'] = addFunc
            kwargs['workspace'] = self.workspace
            kwargs['collection'] = self.name
            kwargs['request'] = request
            kwargs['timeout'] = timeout
            chunk_ret = self.client.apicall(**kwargs)
            if 'commit_mark' in chunk_ret:
                cm = CommitMark.deserialize(chunk_ret['commit_mark'])
                if commit_mark is None:
                    commit_mark = cm
                else:
                    commit_mark.merge_append(cm)
            retval += chunk_ret['data']
        return retval, commit_mark

    def remove_docs(self, docs, timeout=None):
        """Deletes documents from the collection. The ``_id`` field needs to
        be populated in each input document. Other fields in each document
        will be ignored.

        Args:
            docs (list of dicts): documents to be deleted.
            timeout (int): Client side timeout. When specified,
                RequestTimeout_ exception will
                be thrown upon timeout expiration. By default, the client
                will wait indefinitely until it receives results or an
                error from the server.

        Returns:
            Dict: The response dict will have 2 fields: ``data`` and
            ``commit_mark``.

            The ``data`` field will be a list of document status records,
            one for each input document indexed in the same order as the list
            of input documents provided as part of the request. Each of those
            document status records will have fields such as the document
            ``_id``, ``_collection`` name, ``status`` describing if that
            particular document add request succeeded or not, and an optional
            ``error`` field with more details.

            The ``commit_mark`` is an opaque object that uniquely identifies
            this particular add document batch request. You can pass the
            ``commit_mark`` to the fence API, to enquire if Rockset's indexes
            have fully indexed the add document batch and subsequent queries
            to the collection will include those new document updates.
        """
        self._validate_doclist(docs)
        deleteFunc = self.model.deleteDocuments

        # chunk docs to operate in batches
        retval = []
        commit_mark = None
        docids = [{'_id': doc.get('_id', None)} for doc in docs]
        for chunk in self._chopper(docids):
            # assemble the items for this rpc call
            request={'data': chunk}
            kwargs = {}
            kwargs['method'] = deleteFunc
            kwargs['workspace'] = self.workspace
            kwargs['collection'] = self.name
            kwargs['request'] = request
            kwargs['timeout'] = timeout
            chunk_ret = self.client.apicall(**kwargs)
            if 'commit_mark' in chunk_ret:
                cm = CommitMark.deserialize(chunk_ret['commit_mark'])
                if commit_mark is None:
                    commit_mark = cm
                else:
                    commit_mark.merge_append(cm)
            retval += chunk_ret['data']
        return retval, commit_mark

    def fence(self, commit_mark):
        return super(Collection, self).fence(
            self.model.fence, commit_mark)
__all__ = [
    'Collection',
]
