""" An example of a plugin. """
from __future__ import print_function

from lib.common.plugins import Plugin
import lib.common.helpers as helpers

# anything you simply write out (like a script) will run immediately when the
# module is imported (before the class is instantiated)
print("Hello from your new plugin!")


# this class MUST be named Plugin
class Plugin(Plugin):

    def onLoad(self):
        """
        Any custom loading behavior - called by init, so any
        behavior you'd normally put in __init__ goes here
        """
        print("Custom loading behavior happens now.")

        # you can store data here that will persist until the plugin
        # is unloaded (i.e. Empire closes)
        self.calledTimes = 0

        self.info = {
                        # Name for the module that will appear in module menus
                        'Name': 'Invoke-Something',

                        # List of one or more authors for the module
                        'Author': ['@yourname'],

                        # More verbose multi-line description of the module
                        'Description': ('description line 1 '
                                        'description line 2'),

                        # Software and tools that from the MITRE ATT&CK framework (https://attack.mitre.org/software/)
                        'Software': 'SXXXX',

                        # Techniques that from the MITRE ATT&CK framework (https://attack.mitre.org/techniques/enterprise/)
                        'Techniques': ['TXXXX', 'TXXXX'],

                        # List of any references/other comments
                        'Comments': [
                            'comment',
                            'http://link/'
                        ]
                    }

        # Any options needed by the module, settable during runtime
        self.options = {
                        # Format:
                        #   value_name : {description, required, default_value}
                        'Status': {
                            # The 'Agent' option is the only one that MUST be in a module
                            'Description': 'Example Status update',
                            'Required': True,
                            'Value': 'start'
                        },
                        'Message': {
                            'Description': 'Message to print',
                            'Required': True,
                            'Value': 'test'
                        }
        }

    def execute(self, command):
        """
        Parses commands from the API
        """
        try:
            # essentially switches to parse the proper command to execute
            self.options['Status']['Value'] = command['Status']
            self.options['Message']['Value'] = command['Message']
            results = self.do_test('')
            return results
        except:
            return False

    def register(self, mainMenu):
        """
        Any modifications to the mainMenu go here - e.g.
        registering functions to be run by user commands
        """
        mainMenu.__class__.do_test = self.do_test

    def do_test(self, *args):
        """
        An example of a plugin function.

        Usage: test <start|stop> <message>
        """
        print("This is executed from a plugin!")
        print(helpers.color("[*] It can even import Empire functionality!"))

        # Parse arguments from CLI or API
        if len(args[0]) > 0:
            if args[0] == 'help':
                print(helpers.color("[!] example <start|stop> <message>"))
                return
            else:
                self.status = args[0]
                try:
                    self.message = args[1]
                except:
                    self.message = self.options['Message']['Value']
        else:
            self.status = self.options['Status']['Value']
            self.message = self.options['Message']['Value']

        # Store data in the plugin (see onLoad)
        self.calledTimes += 1
        print("This function has been called {} times.".format(self.calledTimes))

        print(self.message)

    def shutdown(self):
        """
        Kills additional processes that were spawned
        """
        # If the plugin spawns a process provide a shutdown method for when Empire exits else leave it as pass
        pass
