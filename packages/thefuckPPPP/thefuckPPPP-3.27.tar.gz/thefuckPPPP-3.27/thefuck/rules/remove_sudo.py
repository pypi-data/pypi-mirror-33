from thefuck.types import Command
from thefuck.corrector import get_rules


def match(command):
    if command.script_parts and command.script_parts[0] == 'sudo':
        return True
    return False


def get_new_command(command):
    script = command.script[4:]
    output = command.output
    newCommand = Command(script, output)
    corrected_commands = list(
        corrected for rule in get_rules()
        if rule.is_match(newCommand)
        for corrected in rule.get_corrected_commands(newCommand))
    if len(corrected_commands) > 0:
        return [u'sudo' + str(cc.script) for cc in corrected_commands]
    else:
        return []
