from .command_auth import AuthCommand
from docopt import docopt
from rockset.exception import InputError

class Drop(AuthCommand):
    def usage(self):
        return """
usage: rock drop [-h] --file=<YAMLFILE>
       rock drop <name> ...

Drop existing collections.

arguments:
    <name>                   name of the collection you wish to drop

options:
    -f FILE, --file=FILE     drop all resources defined in the YAML file
    -h, --help               show this help message and exit
        """

    def parse_args(self, args):
        parsed_args = dict(docopt(self.usage(), argv=args))
        # handle file option
        fn = parsed_args['--file']
        if fn:
            self.set_batch_items('resource', self._parse_yaml_file(fn))
            return {}
        if len(parsed_args['<name>']) > 1:
            resources = [{'name': n} for n in parsed_args['<name>']]
            self.set_batch_items('resource', resources)
            return {}
        resource = {'name': parsed_args['<name>'].pop()}
        return {'resource': resource}

    def go(self):
        self.logger.info('drop {}'.format(self.resource))
        r = self.client.retrieve(name=self.resource['name'])
        if 'type' in self.resource:
            if self.resource['type'] != r.type:
                self.logger.error("input type {} does not match "
                    "actual type {} for resource {}".format(
                    self.resource['type'], r.type, self.resource['name']))
                return 0
        r.drop()
        self.lprint(0, '{} "{}" was dropped successfully.'.format(
            r.type.capitalize(), r.name))
        return 0
