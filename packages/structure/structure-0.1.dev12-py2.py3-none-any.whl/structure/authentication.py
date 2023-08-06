import getpass
import sys

from colorama import Back, Fore, Style, init

if sys.version_info[0] < 3:
    from config import ConfigManager
    from errors import Error
    from network import NetworkManager
else:
    from structure.config import ConfigManager
    from structure.errors import Error
    from structure.network import NetworkManager


def login_required(function):
    def wrapper(*args, **kwargs):
        if not ConfigManager.get_api_token():
            return Error.error_not_logged_in()

        return function(*args, **kwargs)

    wrapper.__name__ = function.__name__
    return wrapper


class AuthCLI(object):
    @staticmethod
    def login():
        email = None

        if sys.version_info[0] < 3:
            email = raw_input(Fore.GREEN + 'Enter your Structure email address: ' + Style.RESET_ALL)
        else:
            email = input(Fore.GREEN + 'Enter your Structure email address: ' + Style.RESET_ALL)

        password = getpass.getpass()

        data = {
            'email': email,
            'password': password,
            'client': 'cli',
        }

        try:
            response = NetworkManager.POST_form('/login', data)

            success = response['success']
            if not success:
                return response['message']

            api_token = response['api_token']
            ConfigManager.create(api_token)

            print(Fore.GREEN + '\nWelcome to the Structure CLI!' + Style.RESET_ALL)
            print('See the available commands by running ' + Fore.GREEN + '`structure help`\n' + Style.RESET_ALL)

        except Exception as e:
            print("Login failed: {}".format(e))

    @staticmethod
    def logout():
        ConfigManager.remove_api_token()
        print(Fore.YELLOW + 'Logged out.' + Style.RESET_ALL)
