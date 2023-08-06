import operator

from slackminion.plugin import cmd
from slackminion.plugin.base import BasePlugin


def subcmd(*args, **kwargs):
    def wrapper(func):
        func.is_subcmd = True
        return func
    return wrapper


class DebugUtility(BasePlugin):

    @cmd(admin_only=True)
    def debug(self, msg, args):
        """Bot Debug Utility.

        Usage:
        !debug _action_ [args]

        Actions:
        dump - Dumps a list of all variables for all plugins and classes
        """
        if len(args) == 0:
            return "Usage: !debug _action_ _args_"

        subcommands = filter(lambda x: callable(x) and hasattr(x, 'is_subcmd'), [getattr(self, x) for x in dir(self)])
        subcommands = {x.__name__: x for x in subcommands}

        action = args[0]
        if action in subcommands:
            return subcommands[action](msg, args[1:])
        else:
            return '%s: Invalid command.  Type `!help debug` for a list of commands.'

    @subcmd()
    def dump(self, msg, args):
        self.send_message(msg.channel, '===== Bot =====\n' + self.attr_to_string(self._bot))
        if hasattr(self._bot, 'user_manager'):
            self.send_message(msg.channel, '===== User Manager =====\n' + self.attr_to_string(self._bot.user_manager))
        if hasattr(self._bot.dispatcher, 'auth_manager'):
                    self.send_message(msg.channel, '===== Auth Manager =====\n' + self.attr_to_string(self._bot.dispatcher.auth_manager))

    def attr_to_string(self, object):
        objects = {x: getattr(object, x) for x in dir(object)}
        objects = sorted(objects.items(), key=lambda x: x[0])
        return '\n'.join(['{}: {}'.format(x[0], x[1]) for x in objects])
