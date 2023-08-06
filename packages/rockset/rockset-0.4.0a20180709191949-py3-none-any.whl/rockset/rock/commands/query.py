from .command_auth import AuthCommand
from rockset import Q

class Query(AuthCommand):
    def usage(self):
        return """
usage: rock query [-h] [--limit=LIMIT] [--skip=SKIP] <name> [<sexpression>]
       rock query [-h] [--limit=LIMIT] [--skip=SKIP] <name> [<sexpression>] [<args>...]

Run a query against a collection

arguments:
  <name>                name of the collection
  <sexpression>         s-expression query to run;
                        will read from STDIN if not specified or if == '-'

optional arguments:
  -h, --help            show this help message and exit
  -l, --limit=LIMIT     maximum number of results to return. set limit to 0 to
                        return all results. [default: 100]
  -s, --skip=SKIP       number of results to skip before fetching
                        results [default: 0]

examples:
  The easiest way to construct sexpressions from command-line is to use Python.
  Here is a query to find all documents from a collection:

  $ python3 -c 'from rockset import Q, F; print(Q.all)' | rock query my_collection

  This example assumes you have two collections "bad_ips" and "login_attempts":

  "bad_ips" collection:
     {"_collection": "bad_ips", "ip_address": "106.6.6.6", "last_seen": ... }
     {"_collection": "bad_ips", "ip_address": "107.6.6.6", "last_seen": ... }

   "login_attempts" collection:
     {"_collection": "login_attempts", "login_ip": "72.43.99.108", ... }
     {"_collection": "login_attempts", "login_ip": "106.6.6.6", ... }

  You can model the above two collections as a graph, where there exists
  an edge between every login_attempts.login_ip and the corresponding
  bad_ips.ip_address

  The following query will find all login_attempts from any of the
  bad_ips:

  $ python3 -c 'from rockset import Q,F; \\
        print(Q("bad_ips")\
.select(F["ip_address"])\
.apply(F["login_ip"], Q("login_attempts")))' | rock query login_attempts

        """

    def validate_args(self, pargs):
        if pargs['--limit'] is not None:
            try:
                pargs['--limit'] = int(pargs['--limit'])
            except ValueError:
                return False
        else:
            pargs['--limit'] = 100
        if pargs['--skip'] is not None:
            try:
                pargs['--skip'] = int(pargs['--skip'])
            except ValueError:
                return False
        else:
            pargs['--skip'] = 0
        return True

    def go(self):
        if self.sexpression is None or self.sexpression == '-':
            self.sexpression = self.read_stdin('query as s-expression')
        q = Q(self.sexpression)
        if self.limit > 0 or self.skip > 0:
            q = q.limit(self.limit, skip=self.skip)

        # handle advanced args
        self.flood = 'flood' in self.args

        # lets do this
        results = self.client.query(q=q, collection=self.name,
            flood_all_leaves=self.flood).results()

        self.print_list_json(0, results)
        return 0
