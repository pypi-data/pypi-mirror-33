# -*- coding: utf-8 -*-
import sys
import os
import zipfile
import pathspec

if sys.version_info[0] < 3:
    from config import ConfigManager
    from errors import Error
    from network import NetworkManager
    from utils import green, blue
else:
    from structure.config import ConfigManager
    from structure.errors import Error
    from structure.network import NetworkManager
    from structure.utils import green, blue

SRC_ZIP_NAME = 'structure_source.zip'


def files_exists(src_path, files):
    for f in files:
        path = os.path.join(src_path, f)
        if os.path.isfile(path):
            return True
    return False


def guess_application_type(src_path):
    is_flask = files_exists(src_path, ['app.py'])
    is_node = files_exists(src_path, ['package.json'])
    is_docker = files_exists(src_path, ['Dockerfile'])
    is_static = files_exists(src_path, ['index.html'])

    # Intentionally exclude is_static for now
    count = sum([is_flask, is_node, is_docker])

    # No candidates other than static
    if count == 0:
        return 'static' if is_static else None

    # One clear candidate
    elif count == 1:
        if is_flask:
            return 'flask'
        elif is_node:
            return 'express'
        elif is_docker:
            return 'docker'

    # Multiple candidates
    return None


def is_restricted_directory(path):
    home_dir = os.path.expanduser('~')
    directories = [
        home_dir,
        os.path.join(home_dir, 'Desktop'),
        os.path.join(home_dir, 'Downloads'),
        os.path.join(home_dir, 'Documents'),
    ]

    for d in directories:
        if os.path.exists(d) and os.path.samefile(path, d):
            return True
    return False


class DeployManager(object):

    @staticmethod
    def default_ignored_files():
        return [
            SRC_ZIP_NAME,
            "*.pyc",
            ".env",
            "env/",
            "venv/*",
            "venv",
            ".eggs",
            "node_modules",
            "node_modules/*",
            "*.zip",
            ".DS_STORE",
            ".DS_Store",
            "npm-debug.log*",
            "yarn-debug.log*",
            "yarn-error.log*",
            ".npm",
        ]

    @staticmethod
    def git_ignored_files(base_path):
        try:
            path = os.path.join(base_path, '.gitignore')
            if os.path.exists(path):
                with open(path) as gitignore:
                    lines = gitignore.readlines()

                    # Convert '\n' items to ''
                    lines = [x.strip() for x in lines]

                    # Remove '' items
                    lines = [x for x in lines if x]

                    return lines
            return []
        except:
            return []


    @staticmethod
    def size_of_files_mb(file_paths):
        total_size = 0
        for abs_path in file_paths:
            total_size += os.path.getsize(abs_path)
        return float(total_size) / 1e6

    @staticmethod
    def files_to_deploy(src_path):
        skip_rules = set(DeployManager.default_ignored_files())
        skip_rules.update(DeployManager.git_ignored_files(src_path))
        skip_rules = list(skip_rules)

        spec = pathspec.PathSpec.from_lines(
            pathspec.patterns.GitWildMatchPattern,
            skip_rules
        )

        files_to_archive = []

        for root, dirs, files in os.walk(src_path):
            if 'node_modules' in dirs:
                dirs.remove('node_modules')

            for file in files:
                abs_path = os.path.abspath(os.path.join(root, file))
                arc_name = os.path.relpath(abs_path)

                should_ignore = len(list(spec.match_files([arc_name]))) > 0
                if not should_ignore:
                    files_to_archive.append(abs_path)

        return files_to_archive

    @staticmethod
    def archive_files(file_paths, output_file):
        zipf = zipfile.ZipFile(output_file, 'w', zipfile.ZIP_DEFLATED)

        for abs_path in file_paths:
            arc_name = os.path.relpath(abs_path)
            zipf.write(abs_path, arcname=arc_name)

        zipf.close()

        return zipf

    @staticmethod
    def deploy(app=None, type=None, reload=False):
        config = ConfigManager.get_app_config()
        src_path = os.getcwd()

        if not app:
            if not config:
                print(Error.warn('Please provide either an app name to deploy to, or create a structure.yaml file.'))
                return
            elif not 'name' in config:
                print(Error.warn('No application name specified in your structure.yaml file.'))
                return
            else:
                app = config['name']

        print("\n  ▶  Deploying {}...".format(green(app)))

        if not type:
            if config and 'type' in config:
                type = config['type']
                print("Application type: {}".format(green(type)))
            else:
                guess = guess_application_type(src_path)

                if guess:
                    type = guess
                    print("  ▶  Detected application type: {}".format(guess))
                else:
                    type_string = green('--type')
                    print(Error.warn(
                        'Please specify an application type either with the {} argument, or via a structure.yaml file.'.format(type_string)))
                    return

        # Safety check.
        if is_restricted_directory(src_path):
            return Error.error("  You're trying to deploy a protected folder; please choose a different folder.")

        if os.path.isfile(SRC_ZIP_NAME):
            os.remove(SRC_ZIP_NAME)

        files_to_deploy = DeployManager.files_to_deploy(src_path)

        project_size_mb = DeployManager.size_of_files_mb(files_to_deploy)
        if project_size_mb > 50:
            if os.path.isfile(SRC_ZIP_NAME):
                os.remove(SRC_ZIP_NAME)

            return Error.error("  The project folder you're trying to deploy is too large ({} MB). Deployments must be less than 50 MB.".format(
                int(project_size_mb)
            ))
        elif project_size_mb > 10:
            print(Error.warn("  The project folder you're trying to deploy is large ({} MB). Deploying may be slow. \n\t   If you have static assets (photos, video, etc.), we recommend hosting them externally.".format(
                int(project_size_mb)
            )))

        zipf = DeployManager.archive_files(
            file_paths=files_to_deploy, 
            output_file=SRC_ZIP_NAME
        )

        zip_file = open(SRC_ZIP_NAME, 'rb')

        response = NetworkManager.POST_JSON(
            endpoint='/cli/{}/deploy/{}'.format(app, type),
            files={
                'src.zip' : zip_file
            },
        )

        os.remove(SRC_ZIP_NAME)

        bold = '\033[1m'
        underline = '\033[4m'
        end = '\033[0m'

        try:
            success = response['success']

            url = None
            if 'url' in response:
                url = 'https://' + response['url']
                styled_url =  blue(underline + bold + url + end)

            if success:
                print('  ▶' + bold + '  Deploy complete!\n' + end)
                print("  Run {} to check the status of your application.".format(green('structure list')))

                if url:
                    print('  Your application will be running at {} \n'.format(styled_url))

                return
            else:
                message = response['message']
                if message:
                    return Error.error(message)
        except Exception as e:
            return Error.warn("Failed to deploy application.")
