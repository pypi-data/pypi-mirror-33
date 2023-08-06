"""
Introduction
------------
Source objects represent various data sources that could be used to create
collections.

Example usage
-------------
::

    from rockset import Client, Q, F
    import os

    rs = Client()

    # create a collection from an AWS S3 bucket
    s3 = rs.Source.s3(bucket='my-s3-bucket',
        access_key=os.getenv('AWS_ACCESS_KEY_ID'),
        secret_access=os.getenv('AWS_SECRET_ACCESS_KEY'))
    newcoll = rs.Collection.create(name='newcoll', sources=[s3])

Create AWS S3 source for a collection
-------------------------------------
AWS S3 buckets can be used as a data source for collections::

    from rockset import Client, Q, F
    import os

    rs = Client()

    # create a collection from an AWS S3 bucket
    s3 = rs.Source.s3(bucket='my-s3-bucket',
        access_key=os.getenv('AWS_ACCESS_KEY_ID'),
        secret_access=os.getenv('AWS_SECRET_ACCESS_KEY'))
    newcoll = rs.Collection.create(name='newcoll', sources=[s3])

.. automethod :: rockset.Source.s3

"""

import csv
from rockset.query import FieldRef

class Source(object):
    def __str__(self):
        return str(vars(self))
    def __iter__(self):
        for k,v in vars(self).items():
            yield (k, v)

    @classmethod
    def s3(cls, bucket, prefixes=None, mappings=None, access_key=None,
            secret_access=None, data_format='json'):
        """ Creates a source object to represent an AWS S3 bucket as a
        data source for a collection.

        Args:
            bucket (str): Name of the S3 bucket
            prefixes (list of str): Path prefix to only source S3 objects that
                are recursively within the given path. (optional)
            mappings (list of tuples): Each tuple has 2 fields as:
                (input_path, masking_function) of type (FieldRef, str)
            access_key (str): AWS access key ID (optional)
            secret_access (str): AWS secret access key (optional)
            data_format (str): oneof "json", "parquet, or "xml"
                [default: "json"]

        """
        return S3Source(bucket=bucket, prefixes=prefixes, mappings=mappings,
            access_key=access_key, secret_access=secret_access,
            data_format=data_format)

    @classmethod
    def collection(cls, name=None, query=None, mappings=None):
        """ Source object to represent a collection as a data source.

        Args:
            name (str): Name of the source collection
            query (Query): Query to filter documents in the source
                collection (optional).
            mappings (list of tuples): Each tuple has 2 fields as:
                (projection, output_field) of type (str, FieldRef)

       """
        return CollectionSource(name=name, query=query, mappings=mappings)


class S3Source(Source):
    def __init__(self, bucket, prefixes=None, mappings=None,
            access_key=None, secret_access=None, data_format='json'):
        self.s3 = {
            'format': data_format,
            'bucket': bucket,
        }
        if prefixes is not None:
            self.s3['prefixes'] = prefixes
        if access_key is not None:
            self.s3['access_key'] = access_key
        if secret_access is not None:
            self.s3['secret_access'] = secret_access

        if mappings:
            mo = []
            for m in mappings:
                if type(m) != tuple or len(m) != 2:
                    raise ValueError("each mapping needs to be a tuple with 2 "
                        "fields as: (input_path, masking_function)")
                if not isinstance(m[0], FieldRef):
                    raise ValueError("input_path of type {} "
                        "not supported".format(type(m[0])))
                mo.append({'input_path': list(m[0]),
                    'mask': {'name': str(m[1])}})

            self.s3['mappings'] = mo


class CollectionSource(Source):
    def __init__(self, name=None, query=None, mappings=None):
        self.collection = {
            'name': name,
        }

        if query:
            self.collection['query'] = str(query)

        if mappings:
            mo = []
            for m in mappings:
                if type(m) != tuple or len(m) != 2:
                    raise ValueError("each mapping needs to be a tuple with 2 "
                        "fields as: (projection, output_field)")
                if not isinstance(m[1], FieldRef):
                    raise ValueError("output_field of type {} "
                        "not supported".format(type(m[1])))
                output_field_path = list(m[1])
                if len(output_field_path) != 1:
                    raise ValueError("output_field cannot be nested")

                mo.append({'projection': m[0],
                           'output_field': output_field_path[0]})

            self.collection['mappings'] = mo

class GmailSource(Source):
    def __init__(self, refresh_token, access_token):
        self.gmail = {
            'refresh_token': refresh_token,
            'access_token': access_token
        }
