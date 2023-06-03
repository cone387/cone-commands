import os
import sys
from cone_commands.core.management.base import (
    Command,
    BaseCommand,
    CommandError,
    CommandParser,
    handle_default_options,
)
from cone_commands.core.management.color import color_style


class ManagementUtility:
    """
    Encapsulate the logic of the cone_commands-admin and manage.py utilities.
    """

    def __init__(self, argv=None):
        self.argv = argv or sys.argv[:]
        self.prog_name = os.path.basename(self.argv[0])
        if self.prog_name == "__main__.py":
            self.prog_name = "python -m cone_commands"

    def execute(self):
        """
        Given the command-line arguments, figure out which subcommand is being
        run, create a parser appropriate to that command, and run it.
        """
        try:
            subcommand = self.argv[1]
        except IndexError:
            self.argv.append('help')
            subcommand = "help"  # Display help if no arguments were given.

        # Preprocess options to extract --settings and --pythonpath.
        # These options could affect the commands that are available, so they
        # must be processed early.
        parser = CommandParser(
            prog=self.prog_name,
            usage="%(prog)s subcommand [options] [args]",
            add_help=False,
            allow_abbrev=False,
        )
        parser.add_argument("--pythonpath")
        parser.add_argument("args", nargs="*")  # catch-all
        try:
            options, args = parser.parse_known_args(self.argv[2:])
            handle_default_options(options)
        except CommandError:
            pass  # Ignore any option errors at this point.

        commands = list(Command.keys())
        print("%s commands are available: %s" % (len(commands), commands))
        try:
            command: BaseCommand = Command(command_name=subcommand, is_registry=False)
        except KeyError:
            print("Unknown command: %r\nType '%s help' for usage." % (subcommand, self.prog_name))
        else:
            command.run_from_argv(self.argv)


def execute_from_command_line(argv=None):
    """Run a ManagementUtility."""
    utility = ManagementUtility(argv)
    utility.execute()
