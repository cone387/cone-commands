import sys
import cone_commands
from cone_commands.core.management.base import BaseCommand, Command


@Command.register()
class VersionCommand(BaseCommand):

    def create_parser(self, prog_name, subcommand, **kwargs):
        parser = super(VersionCommand, self).create_parser(prog_name, subcommand, **kwargs)
        parser.add_argument(
            "--version",
            action="version",
            help="Show program's version number and exit.",
        )
        return parser

    def handle(self, *args, **options):
        sys.stdout.write(cone_commands.__version__ + "\n")
