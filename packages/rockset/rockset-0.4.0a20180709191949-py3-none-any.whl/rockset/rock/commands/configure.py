import os
import sys

from docopt import docopt
from rockset.credentials import Credentials
from .command import Command


def interactive_prompt(config):
    out = {}
    for item in config:
        key = item['key']
        message = item['message']
        prompt = item['prompt']
        default = item['default']
        if 'display' in default:
            prompt += ' [%s]' % default['display']
        sys.stdout.write(message + '\n')
        sys.stdout.write(prompt + ': ')
        sys.stdout.flush()
        value = input()
        value = value.strip()
        if value == '':
            value = default.get('value', '')
        out[key] = value
    return out


class Configure(Command):
    def usage(self):
        return """
usage: rock configure [--help]
       rock configure add <profile>
       rock configure update <profile>
       rock configure ls
       rock configure rm <profile>
       rock configure select <profile>

Manage Rockset credential profiles. Each profile is associated
with an API key and an API endpoint.

commands:
    add, update       create a new credentials profile or update an existing one
                      Default, when no profiles exist.
    ls                list all profiles.
                      Default, when 1 or more profiles exist.
    rm                remove profile
    select            select profile to use for subsequent rock commands

arguments:
    <profile>         name of the profile you wish to create or update

options:
  -h, --help          show this help message and exit
        """

    def go(self):
        creds = Credentials()

        # determine default command when none is specified
        if (
            not self.add and not self.update and not self.ls and not self.rm and
            not self.select
        ):
            if len(creds.get_all_profiles()) == 0:
                self.profile = 'default'
                self.add = True
            else:
                self.ls = True

        # update is same as add
        if self.add or self.update:
            new_profile = self.profile
            defaults = creds.get(new_profile)
            ip = interactive_prompt(
                [
                    {
                        'message': 'Enter Rockset API key',
                        'prompt': '  API Key',
                        'default':
                            {
                                'display':
                                    self._format_secret(
                                        defaults.get('api_key', None)
                                    ),
                                'value':
                                    defaults.get('api_key', None),
                            },
                        'key': 'api_key'
                    },
                    {
                        'message':
                            'Enter Rockset API server hostname or IP address',
                        'prompt':
                            '  API Server',
                        'default':
                            {
                                'display':
                                    defaults.get(
                                        'api_server', 'https://api.rs2.usw2.rockset.com'
                                    ),
                                'value':
                                    defaults.get(
                                        'api_server', 'https://api.rs2.usw2.rockset.com'
                                    ),
                            },
                        'key':
                            'api_server'
                    },
                ]
            )
            ip['profile'] = new_profile
            profile_details = creds.set(**ip)
            if len(creds.get_all_profiles()) == 1:
                creds.active_profile(ip['profile'])
            creds.save()
        elif self.select:
            select_profile = self.profile
            active_profile = creds.active_profile(select_profile)
            if active_profile != select_profile:
                self.error('Could not switch to profile "%s"!' % select_profile)
            else:
                creds.save()
        elif self.rm:
            rm_profile = self.profile
            deleted_profile = creds.delete(rm_profile)
            if deleted_profile is None:
                self.error('No profile with name "%s" exists!' % rm_profile)
            else:
                creds.save()

        # print all profiles in alphabetical order
        all_profiles = creds.get_all_profiles()
        all_profile_names = list(all_profiles.keys())
        all_profile_names.sort()

        # accumulate formatted profiles
        profiles = []
        for pn in all_profile_names:
            profiles.append(
                self._format_profile(
                    pn, all_profiles[pn], creds.active_profile()
                )
            )

        self.print_list(
            0,
            profiles,
            field_order=['profile', 'api_server', 'api_key'],
            header=True
        )
        if self.format == 'text':
            self.lprint(0, 'Credentials stored in %s' % creds.creds_file)

        return 0

    def _format_secret(self, value):
        if value is None:
            return None
        i = 4
        if len(value) < 20:
            i = 1
        return '%s**********%s' % (value[:i], value[-i:])

    def _format_profile(self, p, pd, ap):
        # prefix profile name with '*' if current
        if p == ap:
            prefix = '* '
        else:
            prefix = '  '
        pd['profile'] = prefix + p

        # don't show full api_key
        pd['api_key'] = self._format_secret(pd.get('api_key', None))
        return pd
