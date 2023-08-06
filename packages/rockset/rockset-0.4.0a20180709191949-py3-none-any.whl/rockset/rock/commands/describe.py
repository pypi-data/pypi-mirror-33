from .command_rest import RESTCommand

class Describe(RESTCommand):
    def usage(self):
        return """
usage: rock describe [-ah] <name> ...

Show details about a Rockset collection.

arguments:
    <name>              name of the collection

options:
    -a, --all           display extended stats
    -h, --help          show this help message and exit"""

    def go(self):
        for name in self.name:
            path='/orgs/{}/ws/{}/collections/{}'.format('self', 'commons',
                name)
            deets = self.get(path)
            if 'data' in deets and 'sources' in deets['data']:
                nsrcs = []
                for src in deets['data']['sources']:
                    nsrcs.append({k:v for k,v in src.items() if v})
                deets['data']['sources'] = nsrcs
            desc = {}
            if 'data' in deets:
                desc = {k:v for k,v in deets['data'].items() if v}
            self.print_one(0, desc)
        return 0
