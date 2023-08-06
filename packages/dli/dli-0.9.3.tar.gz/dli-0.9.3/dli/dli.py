"""
Command Line Interface

:Usage:
  - ``dli configure``
  - ``dli configure (--update|--overwrite)``
  - ``dli register (package|dataset) <config_file>``
  - ``dli -h | --help``
  - ``dli --version``
 
:Options:
  - ``--version``                         Show version.
  - ``-h --help``                         Show this screen.

:Examples:
  dli hello
 
:Help:
  For help using this tool, please open an issue on the Github repository:
  https://git.mdevlab.com/data-lake/data-lake-sdk
"""


from inspect import getmembers, isclass

from docopt import docopt


def main():
    """Main CLI entrypoint."""
    import dli.commands
    options = docopt(__doc__, version=dli.__version__)

    # Here we'll try to dynamically match the command the user is trying to run
    # with a pre-defined command class we've already created.
    for k, v in options.items():
        if hasattr(dli.commands, k) and v is True:
            module = getattr(dli.commands, k)
            commands = getmembers(module, isclass)
            command = [command[1]
                       for command in commands if command[0] != 'Base'][0]
            command = command(options)
            command.run()
            return 
