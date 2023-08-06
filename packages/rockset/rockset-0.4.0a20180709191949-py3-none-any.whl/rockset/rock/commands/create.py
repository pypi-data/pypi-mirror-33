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
  rock create collection --help
  rock create collection [-h] [--desc=TEXT] <name> [<collection_source_args> ...]

Create a new collection

commands:
  collection          create a new collection.
                      you can optionally specify data sources to automatically
                      feed into the collection such as AWS S3

arguments:
  <name>              name of the new collection you wish to create

options:
  -d TEXT, --desc=TEXT  human readable description of the new resource
  -f FILE, --file=FILE  create all resources in the a YAML file
  -h, --help            show this help message and exit
        """

        usage_collection = """
usage:
  rock create collection --help
  rock create collection [-h] <name> [<collection_source_args> ...]
  rock create collection [-h] <name>
        (s3 <s3_bucket_name>)
        [(prefix <s3_bucket_prefix>) ...]
        [(format <data_format>)]
        [(mask <field_mask>) ...]
        [(delimiter <field_path_delimiter>)]
        [(access_key <aws_access_key_id>)]
        [(secret_access <aws_secret_access_key>)]
        [<next_collection_source_args> ...]

Create a new collection using AWS S3 as a data source.

Optionally, fields can be masked or anonymized as they are replicated into
the collection.

arguments:
  <aws_access_key_id>      AWS access key id
  <aws_secret_access_key>  AWS secret access key
  <data_format>            Data format of objects in S3. One of "json",
                           "parquet", or "xml". [default: "json"]
  <field_mask>             field masks can anonymize or ignore fields
                           as they are replicated into the collection.
                           Each <field_mask> is a ":" colon-separated tuple of
                           an input field that needs to be masked and name of
                           the masking function such as 'SHA256' or 'NULL'.
  <field_path_delimiter>   specify field path delimiter while specifying
                           nested fields in <field_mask> [default: "."]
  <s3_bucket_name>         name of the AWS S3 bucket
  <s3_bucket_prefix>       only add objects with prefix from AWS S3 bucket

options:
  -h, --help               show this help message and exit

examples:
    Create a collection and source all contents from an AWS S3 bucket:

        $ rock create collection bkt1rocks \\
              s3 bkt1.mycompany.com

    Create a collection from an AWS S3 bucket but only pull certain paths:

        $ rock create collection bkt1rocks \\
              s3 bkt1.mycompany.com \\
              prefix '/root/path/in/bkt1' \\
              prefix '/root/path2'

    Create a collection from AWS S3 after incorporating the following two masks:
         i) anonymize input nested field from.email
        ii) overwrite input field email_body to NULL

        $ rock create collection bkt1-coll \\
              s3 bkt1.mycompany.com \\
              mask from.email:SHA256 \\
              mask email_body:NULL
        """
        if subcommand == 'collection':
            return usage_collection
        return usage

    def _parse_arg_pairs(self, args, heads, singles, multi, leftover):
        """ splits `args` after validation into a map.
        returns dict or None if error.
        every entry in `singles` + `multi` will be a key.
        default value for all `singles` will be None and `multi` will be [].
        expects `args` to start with one of the `heads`, and returns
        the remainder in key `leftover`.
        """
        if len(args) < 2 or len(args) % 2 != 0:
            return None
        for head in heads:
            if head not in singles or head in multi:
                return None
        if args[0] not in heads:
            return None
        pargs = {}
        for s in singles:
            pargs[s] = None
        for m in multi:
            pargs[m] = []
        i = 0
        while i < len(args):
            # pop keys and ensure we didn't hit the next head
            key = args[i]
            if i > 0 and key in heads:
                break
            # pop value and bump i
            value = args[i + 1]
            i += 2
            if key in singles:
                if pargs[key] is not None:
                    return None
                pargs[key] = value
            elif key in multi:
                pargs[key].append(value)
            else:
                return None
        pargs[leftover] = args[i:]
        return pargs

    def _source_s3(self, args):
        mappings = []
        if len(args['mask']) > 0:
            delimiter = '.'
            if args['delimiter']:
                delimiter = args['delimiter']
            for fm in args['mask']:
                mask = list(csv.reader([fm], delimiter=':')).pop()
                if len(mask) != 2:
                    raise ValueError('cannot understand '
                        'field_mask {}'.format(fm))
                input_path = list(csv.reader([mask[0]],
                    delimiter=delimiter)).pop()
                input_path_fr = F
                for i in input_path:
                    input_path_fr = input_path_fr[i]
                mappings.append(tuple([input_path_fr, mask[1]]))
        return self.client.Source.s3(bucket=args['s3'],
            data_format=args.get('format', None),
            prefixes=args.get('prefix', None),
            mappings=mappings,
            access_key=args.get('access_key', None),
            secret_access=args.get('secret_access', None))

    def _source_collection(self, args):
        mappings = []
        if len(args['mapping']) > 0:
            delimiter = '.'
            if args['delimiter']:
                delimiter = args['delimiter']
            for fm in args['mapping']:
                mapping = list(csv.reader([fm], delimiter=':')).pop()
                if len(mapping) != 2:
                    raise ValueError('cannot understand '
                        'field_mapping {}'.format(fm))
                projection = mapping[0]
                output_field_fr = F[mapping[1]]
                mappings.append(tuple([projection, output_field_fr]))
        return self.client.Source.collection(name=args['collection'],
            query=args.get('query', None),
            mappings=mappings)

    def parse_args(self, args):
        parsed_args = dict(docopt(self.usage(), argv=args, help=False))

        # handle help
        if parsed_args['--help']:
            if parsed_args['collection']:
                ret = self.usage(subcommand='collection')
            else:
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
            if len(parsed_args['<collection_source_args>']) > 0:
                argv = parsed_args['<collection_source_args>']
                while len(argv) > 0:
                    parsed_args = self._parse_arg_pairs(argv,
                        heads=['s3'],
                        singles=['s3','delimiter','format',
                            'access_key','secret_access'],
                        multi=['prefix','mask'],
                        leftover='_next')
                    if parsed_args is None:
                        ret = self.usage(subcommand='collection')
                        raise SystemExit(ret.strip())
                    if parsed_args['s3']:
                        sources.append(self._source_s3(parsed_args))
                    argv = parsed_args['_next']
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
        self.lprint(0, 'Collection "%s" was created successfully.'
            % (c.name))
        return 0

