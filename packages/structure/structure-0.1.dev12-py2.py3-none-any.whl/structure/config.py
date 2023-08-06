import os
import yaml
from tinynetrc import Netrc

YAML_CONFIG = 'structure.yaml'


class ConfigManager(object):

    # Client app configuation

    @staticmethod
    def get_app_config(path=YAML_CONFIG):
        try:
            with open(YAML_CONFIG, 'r+') as f:
                data = yaml.safe_load(f)
                return data
        except Exception as e:
            return None


    # .netrc

    @staticmethod
    def netrc_create_if_needed():
        netrc_path = os.path.expanduser('~/.netrc')
        if not os.path.exists(netrc_path):
            f = open(netrc_path, 'w')
            f.close()

    @staticmethod
    def get_api_token():
        ConfigManager.netrc_create_if_needed()

        netrc = Netrc()
        not_logged_in_error = "No API token found. Please run `structure login` to get started."

        if not 'structure.sh' in netrc:
            print(not_logged_in_error)
            return None

        if not 'login' in netrc['structure.sh']:
            print(not_logged_in_error)
            return None

        api_key = netrc['structure.sh']['login']
        if not api_key or api_key == 'None':
            print(not_logged_in_error)
            return None

        return api_key

    @staticmethod
    def remove_api_token():
        try:
            netrc = Netrc()
            if 'structure.sh' in netrc:
                del netrc['structure.sh']
            netrc.save()
        except Exception as e:
            pass

    @staticmethod
    def create(token):
        try:
            ConfigManager.netrc_create_if_needed()
            netrc = Netrc()

            # `login` and `password` keys are required
            # for netrc
            netrc['structure.sh'] = {
                'login': token,
                'password': 'None',
            }

            netrc.save()

        except Exception as e:
            print(e)
