from .command_auth import AuthCommand
from rockset.exception import InputError

import json
import os
import sys

class Add(AuthCommand):
    def usage(self):
        return """
usage: rock add [--help] <collection> <files>...

Add local files to a collection

arguments:
  collection            name of the collection you wish to add data

commands:
  <files>               add local JSON files to the collection.
                        use "-" for STDIN.
                        each file can be in any of the following formats:
                        i.   JSON object
                        ii.  JSON array of documents
                        iii. JSON object per line

options:
  -h, --help    show this help message and exit
        """

    def _input(self):
        return sys.stdin

    def go(self):
        c = self.client.Collection.retrieve(self.collection)

        all_docs = []
        for localfile_name in self.files:
            # open file
            try:
                if localfile_name == '-':
                    localfile = self._input()
                else:
                    localfile = open(localfile_name, 'r', encoding="utf-8")
            except (OSError, IOError) as e:
                self.error('Skipping file {} : Unable to open: {}'.format(
                    localfile_name, str(e)))
                continue

            try:
                localfile_contents = localfile.read()
                self.logger.info('add file contents: "{}"'.format(
                    localfile_contents))
                local_json = json.loads(localfile_contents)
            except json.JSONDecodeError as e:
                try:
                    local_json = []
                    for line in localfile_contents.split('\n'):
                        local_json.append(json.loads(line))
                except json.JSONDecodeError as e2:
                    # bad JSON - report exception "e" not "e2"
                    self.error('Skipping file {} : '
                        'JSON decode error at line {}:{}'.format(
                        localfile_name, e.lineno, e.colno))
            finally:
                if localfile_name != '-':
                    localfile.close()

            if type(local_json) == list:
                all_docs += local_json
            elif type(local_json) == dict:
                all_docs += [local_json]
            else:
                self.error('Skipping file {} : '
                    'type {} is not supported'.format(
                    localfile_name, type(local_json)))

        self.print_list(0, c.add_docs(all_docs)[0],
            field_order=['_collection', '_id', 'status', 'error'])
        return 0
