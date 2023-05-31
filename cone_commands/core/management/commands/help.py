
import sys
from collections import defaultdict
from cone_commands.core.management import color_style
from cone_commands.core.management.base import BaseCommand, Command


@Command.register()
class HelpCommand(BaseCommand):

    def handle(self, *args, **options):
        if "--commands" in args:
            sys.stdout.write('\n'.join(list(Command.keys())) + "\n")
        elif not args:
            usage = [
                "",
                "Type '%s help <subcommand>' for help on a specific subcommand."
                % sys.argv[0],
                "",
                "Available subcommands:",
            ]
            commands_dict = defaultdict(lambda: [])
            for name, item in Command.items():
                commands_dict[name].append(item)
            style = color_style()
            for app in sorted(commands_dict):
                usage.append("")
                usage.append(style.NOTICE("[%s]" % app))
                for name in sorted(commands_dict[app]):
                    usage.append("    %s" % name)
            sys.stdout.write("\n".join(usage) + "\n")
        else:
            command: BaseCommand = Command(args[0], is_registry=False)()
            command.print_help(self.prog_name, args[0])
