from colorama import Fore, Style
import sys

if sys.version_info[0] < 3:
    from utils import green
else:
    from structure.utils import green


class Error(object):

    @staticmethod
    def error_missing_app_arg(cmd_name, arg_name, arg_value):
        cmd = green('--{} {}'.format(arg_name, arg_value))
        return Error.warn("No application specified; please provide one.\nUsage: structure {} {}".format(cmd_name, cmd))

    @staticmethod
    def error_not_logged_in():
        return Error.warn("No account found, please log in by running `structure login`", newline=True)

    @staticmethod
    def note(message, newline=False):
        return Error.format(message=message, message_type='note', newline=newline)

    @staticmethod
    def warn(message, newline=False):
        return Error.format(message=message, message_type='warning', newline=newline)

    @staticmethod
    def error(message, newline=False):
        return Error.format(message=message, message_type='error', newline=newline)

    @staticmethod
    def format(message, message_type, newline=False):
        if newline:
            newline = "\n"
        else:
            newline = "\n"

        message_prefix = ''
        message_color = Fore.WHITE

        if message_type == 'note':
            message_prefix = "Note: "
            message_color = Fore.GREEN

        if message_type == 'warning':
            message_prefix = "Warning: "
            message_color = Fore.YELLOW

        if message_type == 'error':
            message_prefix = "Error: "
            message_color = Fore.RED

        return ''.join([
            newline,
            message_color,
            message_prefix,
            Style.RESET_ALL,
            message,
            newline
        ])
