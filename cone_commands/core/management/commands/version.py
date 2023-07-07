import cone_commands
from cone_commands.core.management.base import BaseCommand, Command


@Command.register()
class VersionCommand(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument(
            "--version",
            action="version",
            help="Show program's version number and exit.",
        )

    def handle(self, *args, **options):
        self.stdout.write(cone_commands.__version__ + "\n")
