import csv
import sys

from .command_auth import AuthCommand
from docopt import docopt
from rockset import Q, F


class Create(AuthCommand):
    def usage(self, subcommand=None):
        usage = """
usage:
  rock create --help
  rock create [-h] --file=YAMLFILE
  rock create collection <name> [options] [<data_source_url> ...]

Create a new collection

commands:
  collection          create a new collection.
                      you can optionally specify data sources to automatically
                      feed into the collection such as AWS S3

arguments:
  <name>              name of the new collection you wish to create
  <data_source_url>   specify the data source to auto ingest in order to
                      populate the collection
                      eg: s3://my-precious-s3-bucket
                          s3://my-precious-s3-bucket/data/path/prefix


options:
  -d TEXT, --desc=TEXT        human readable description of the new resource
  -f FILE, --file=FILE        create all resources specified in the YAML file,
                              run `rock -o yaml describe <collection>` on an
                              existing collection to see the YAML format
  -h, --help                  show this help message and exit

options for AWS data sources (such as AWS S3):
  --aws_access_key_id=AWS_ACCESS_KEY_ID              AWS access key id
  --aws_secret_access_key=AWS_SECRET_ACCESS_KEY      AWS secret access key

examples:

    Create a collection and source all contents from an AWS S3 bucket:

        $ rock create collection customers s3://customers-mycompany-com

    Create a collection from an AWS S3 bucket but only pull a particular
    path prefix within the S3 bucket:

        $ rock create collection event-log \\
            s3://event-log.mycompany.com/root/path/in/bkt

        """
        return usage

    def _source_s3(self, s3_url, args):
        parts = s3_url[5:].split('/')
        bucket = parts[0]
        prefixes = (len(parts) > 1) and ['/'.join(parts[1:])] or []
        return self.client.Source.s3(
            bucket=bucket,
            prefixes=prefixes,
            access_key=args.get('--aws_access_key_id', None),
            secret_access=args.get('--aws_secret_access_key', None)
        )

    def parse_args(self, args):
        parsed_args = dict(docopt(self.usage(), argv=args, help=False))

        # handle help
        if parsed_args['--help']:
            ret = self.usage()
            raise SystemExit(ret.strip())

        # see if YAMLFILE was specified
        fn = parsed_args['--file']
        if fn:
            self.set_batch_items('resource', self._parse_yaml_file(fn))
            return {}

        # construct a valid CreateRequest object
        resource = {}
        resource['name'] = parsed_args['<name>']
        if parsed_args['--desc']:
            resource['description'] = parsed_args['--desc']
        sources = []
        if parsed_args['collection']:
            resource['type'] = 'COLLECTION'
            for source in parsed_args['<data_source_url>']:
                if source[:5] == 's3://':
                    sources.append(self._source_s3(source, parsed_args))
                else:
                    ret = 'Error: invalid data source URL "{}"\n'.format(source)
                    ret += self.usage()
                    raise SystemExit(ret.strip())
        resource['sources'] = sources
        return {'resource': resource}

    def go(self):
        self.logger.info('create {}'.format(self.resource))
        rtype = self.resource.pop('type', None)
        if rtype is None:
            return 1
        if rtype == 'COLLECTION':
            return self.go_collection(self.resource)
        return 1

    def go_collection(self, resource):
        name = resource.pop('name')
        c = self.client.Collection.create(name, **resource)
        self.lprint(0, 'Collection "%s" was created successfully.' % (c.name))
        return 0
