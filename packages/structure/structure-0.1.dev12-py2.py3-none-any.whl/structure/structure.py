# -*- coding: utf-8 -*-
#!/usr/bin/python

import io
import json
import os
import subprocess
import sys
import zipfile

import fire
import requests
import pkg_resources
from colorama import Back, Fore, Style, init

if sys.version_info[0] < 3:
    from authentication import AuthCLI, login_required
    from config import ConfigManager
    from deploy import DeployManager
    from errors import Error
    from help import HelpCommand
    from lifecycle import Lifecycle
    from network import NetworkManager
    from utils import *
    from update import check_for_updates_if_needed
else:
    from structure.authentication import AuthCLI, login_required
    from structure.config import ConfigManager
    from structure.deploy import DeployManager
    from structure.errors import Error
    from structure.help import HelpCommand
    from structure.lifecycle import Lifecycle
    from structure.network import NetworkManager
    from structure.utils import *
    from structure.update import check_for_updates_if_needed

init()

class CLI(object):

    def help(self):
        return HelpCommand.text()

    def login(self):
        return AuthCLI.login()

    def logout(self):
        return AuthCLI.logout()

    def token(self):
        return ConfigManager.get_api_token()

    def version(self, verbose=False):
        structure_version = pkg_resources.require("structure")[0].version
        print("Structure CLI version: {}".format(structure_version))

        if verbose:
            python_version = sys.version
            print("Python version: {}".format(python_version))

    @login_required
    def create(self):

        application_name = None
        application_type = None

        if sys.version_info[0] < 3:
            application_name = raw_input("Name your application: ")
            application_type = raw_input("Select a stack (flask, express, or static): ")
        else:
            application_name = input("Name your application: ")
            application_type = input("Select a stack (flask, express, or static): ")

        if not application_name or not application_type:
            return "Please provide an application name and type."

        data = {
            'application_name': application_name,
            'language': application_type,
        }

        try:
            response = NetworkManager.POST_JSON(
                endpoint='/cli/createApplication',
                json_data=data
            )

            success = response['success']
            if success:
                if 'message' in response:
                    return response['message']
                else:
                    return green('Successfully created application.')
            else:
                return 'Unable to create application.'
        except Exception as e:
            print("Unable to reach the Structure server.")

    @login_required
    def deploy(self, app=None, type=None, reload=False):
        return DeployManager.deploy(app=app, type=type, reload=reload)

    @login_required
    def pull(self, app=None):
        if not app:
            return Error.error_missing_app_arg(
                cmd_name='pull',
                arg_name='app',
                arg_value='APP_NAME'
            )

        try:
            url = 'https://structure.sh/cli/{}/pull'.format(app)
            r = requests.get(
                url=url,
                headers={
                    'X-Structure-Token': ConfigManager.get_api_token(),
                }
            )

            z = zipfile.ZipFile(io.BytesIO(r.content))
            z.extractall()
        except Exception as e:
            return Error.warn("Unable to retrieve project files.")

    @login_required
    def run(self, app=None):
        if not app:
            return Error.error_missing_app_arg(
                cmd_name='run',
                arg_name='app',
                arg_value='APP_NAME'
            )

        print("Running application...")
        err = Lifecycle.set_status(app, 'reload')
        if err:
            print(err)
        else:
            print("Run `{}` to check the status of your application.".format(green('structure list')))
            print('')

    @login_required
    def stop(self, app=None):
        if not app:
            return Error.error_missing_app_arg(
                cmd_name='stop',
                arg_name='app',
                arg_value='APP_NAME'
            )

        print("Stopping application...")
        err = Lifecycle.set_status(app, 'stopped')
        if err:
            print(err)
        else:
            print("Run `{}` to check the status of your application.".format(green('structure list')))
            print('')

    @login_required
    def restart(self, app=None):
        if not app:
            return Error.error_missing_app_arg(
                cmd_name='restart',
                arg_name='app',
                arg_value='APP_NAME'
            )

        print("Restarting application...")
        err = Lifecycle.set_status(app, 'reload')
        if err:
            print(err)
        else:
            print("Run `{}` to check the status of your application.".format(green('structure list')))
            print('')

    @login_required
    def remove(self, *apps):
        if not apps:
            cmd = green('--apps MY_APP')
            return Error.warn("No application(s) specified; please provide at least one.\nUsage: structure remove {} ...".format(cmd))

        # TODO: Make this one api call
        for app in apps:
            data = {
                'application_name': app,
            }

            try:
                response = NetworkManager.POST_JSON(
                    endpoint='/cli/removeApplication',
                    json_data=data,
                )

                success = response['success']

                if success:
                    print(green('\n  Successfully removed {}. \n'.format(app)))
                else:
                    print(Error.warn("Unable to remove {}}.".format(app)))

            except Exception as e:
                print(Error.warn("Unable to remove {}.".format(app)))

    @login_required
    def ls(self):
        try:
            response = NetworkManager.POST_JSON(
                endpoint='/cli/apps'
            )

            success = response['success']
            if success:
                states = response['apps']
                username = response['username']

                keys = states.keys()

                if len(keys) == 0:
                    return "You don't have any apps yet; run `{}` to get started.".format(green('structure create'))

                print('')
                longest_app_name = max(keys, key=len)
                max_name_len = len(longest_app_name)

                pad_constant = 8
                pad_len = max_name_len - len('Name') + pad_constant
                pad_string = padding(pad_len)

                print("Name{}Status{}url".format(pad_string, padding(pad_constant)))
                print("----{}------{}---".format(pad_string, padding(pad_constant)))

                for name, status in sorted(states.items()):
                    pad_len = max_name_len - len(name) + pad_constant
                    pad_string = padding(pad_len)

                    formatted_status = None

                    if status == 'running':
                        formatted_status = green(status.title())
                    else:
                        formatted_status = yellow(status.title())

                    url = 'https://{}-{}.structure.sh'.format(name, username)
                    print("{}{}{}{}{}".format(name, pad_string, formatted_status, padding(pad_constant - 1), url))

                print('')

                return None
            else:
                if 'message' in response:
                    return Error.warn(response['message'])

            return Error.warn("Unable to retrieve applications.")
        except Exception as e:
            return Error.warn("Request failed.")

    @login_required
    def logs(self, app=None):
        if not app:
            return Error.error_missing_app_arg(
                cmd_name='logs',
                arg_name='app',
                arg_value='APP_NAME'
            )

        print("Fetching logs for {}...".format(app))

        try:
            endpoint = '/cli/{}/logs'.format(app)
            response = NetworkManager.POST_JSON(
                endpoint=endpoint
            )

            success = response['success']
            if success:
                return response['logs']
            else:
                if 'message' in response:
                    return Error.warn(response['message'])

            return Error.warn("Unable to retrieve application logs.")
        except Exception as e:
            return Error.warn("Unable to retrieve application logs.")

    @login_required
    def ssh(self, app=None):
        if not app:
            return Error.error_missing_app_arg(
                cmd_name='ssh',
                arg_name='app',
                arg_value='APP_NAME'
            )

        try:
            url = 'https://structure.sh/cli/{}/ssh'.format(app)
            r = requests.get(
                url=url,
                headers={
                    'X-Structure-Token': ConfigManager.get_api_token(),
                }
            )
            response = json.loads(r.text)
            success = response['success']
            if not success:
                return Error.warn(response['message'])

            ip = response['ip']
            port = response['port']
            ssh_cmd = 'ssh app@{} -p {}'.format(ip, port)

            subprocess.call(ssh_cmd, shell=True)
        except Exception as e:
            return Error.warn("Request failed.")

    @login_required
    def ssh_add(self, app=None, path=None):
        if not app:
            cmd = green('--app APP_NAME --path /optional/path/to/public/key')
            return Error.warn("No application specified; please provide one.\nUsage: structure ssh-add {}".format(cmd))

        try:
            public_key_path = os.path.expanduser('~/.ssh/id_rsa.pub')

            if path:
                public_key_path = path

            if not os.path.exists(public_key_path):
                return Error.warn("No public key found in `{}`. Run `ssh-keygen` to add one.".format(public_key_path))

            with open(public_key_path, 'r+') as f:
                # TODO: Seems to only read the last key
                key_contents = f.read()

                endpoint = '/cli/{}/ssh'.format(app)
                response = NetworkManager.POST_JSON(
                    endpoint=endpoint,
                    json_data={
                        'public_key': key_contents
                    }
                )

                if response['success']:
                    return 'Successfully added your public key. Try running `{}` to SSH into your app.'.format(green('ssh app@structure.sh'))
                else:
                    return response['message']
        except Exception as e:
            return Error.warn("Request failed.")


def main():
    # Manually route `structure` to `structure help`
    if len(sys.argv) == 1:
        return CLI().help()

    # Alias list and ls
    if sys.argv[1] == 'list':
        sys.argv[1] = 'ls'

    command = sys.argv[1]

    # Keep this updated
    available_commands = [
        'create',
        'deploy',
        'help',
        'login',
        'logout',
        'logs',
        'ls',
        'pull',
        'remove',
        'restart',
        'run',
        'ssh',
        'ssh-add',
        'stop',
        'token',
        'version',
    ]

    if not (command in available_commands):
        print(Error.warn("'{}' is not a structure command.".format(command)))
        print("See 'structure help' to see all available commands.\n")
        return

    fire.Fire(CLI)
    check_for_updates_if_needed()

if __name__ == '__main__':
    main()
