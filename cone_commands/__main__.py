"""
Invokes cone when the cone_commands module is run as a script.

Example: python -m cone_commands check
"""
from cone_commands.core import management

if __name__ == "__main__":
    management.execute_from_command_line()
