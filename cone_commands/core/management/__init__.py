import os
import sys
from cone_commands.core.management.base import (
    Command,
    RemoteCommand,
    BaseCommand,
    CommandError,
    CommandParser,
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
            parser.parse_known_args(self.argv[2:])
        except CommandError:
            pass  # Ignore any option errors at this point.

        local_commands = list(Command.keys())
        remote_commands = []
        for _, items in RemoteCommand.items():
            remote_commands.extend(items.keys())
        print("%s local commands are available: %s" % (len(local_commands), local_commands))
        print("%s remote commands are available: %s" % (len(remote_commands), remote_commands))
        try:
            command: BaseCommand = Command(command_name=subcommand, is_registry=False)
        except KeyError:
            try:
                command = RemoteCommand(command_name=subcommand)
            except KeyError:
                print("Unknown command: %r\nType '%s help' for usage." % (subcommand, self.prog_name))
                sys.exit(1)
        command.run_from_argv(self.argv)


def execute_from_command_line(argv=None):
    """Run a ManagementUtility."""
    utility = ManagementUtility(argv)
    utility.execute()
