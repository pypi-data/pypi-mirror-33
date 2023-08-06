import sys

if sys.version_info[0] < 3:
  from utils import green
else:
  from structure.utils import green


class HelpCommand(object):

  @staticmethod
  def text():
    return '''     
  Usage:        {} <command> [arguments]

  Commands:

    {}      [app]           Deploy the current folder to Structure
                [--type X]      (Optional: `node`, `flask`, or `static`)

    list                        List all apps

    remove      [app]           Remove an existing app

    logs        [app]           View a running app's logs

    run         [app]           Run an app
    stop        [app]           Stop an app
    restart     [app]           Restart an app

    token                       See your API token
    version                     See the Structure CLI version

  --------------

  Documentation and tutorials: {}

  Examples:

    - Deploy the project in the current directory
      $ structure deploy hello-world --type --static

    - Run an existing app:
      $ structure run hello-world

    '''.format(
        green('\033[1mstructure'),
        green('\033[1mdeploy'),
        green('https://docs.structure.sh')
    )
