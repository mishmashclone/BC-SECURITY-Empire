from __future__ import print_function
from builtins import str
from builtins import object
from lib.common import helpers


class Module(object):

    def __init__(self, mainMenu, params=[]):

        # Metadata info about the module, not modified during runtime
        self.info = {
            # Name for the module that will appear in module menus
            'Name': 'Invoke-Rubeus',

            # List of one or more authors for the module
            'Author': ['@harmj0y', '@S3cur3Th1sSh1t'],

            # More verbose multi-line description of the module
            'Description': ("Rubeus is a C# toolset for raw Kerberos interaction and abuses. "
                            "It is heavily adapted from Benjamin Delpy's Kekeo project (CC BY-NC-SA 4.0 license) "
                            "and Vincent LE TOUX's MakeMeEnterpriseAdmin project (GPL v3.0 license). Full credit goes "
                            "to Benjamin and Vincent for working out the hard components of weaponization- without "
                            "their prior work this project would not exist."),

            'Software': '',

            'Techniques': ['T1208', 'T1097'],

            # True if the module needs to run in the background
            'Background': False,

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
                'https://github.com/GhostPack/Rubeus',
                'https://github.com/S3cur3Th1sSh1t/PowerSharpPack'
            ]
        }

        # Any options needed by the module, settable during runtime
        self.options = {
            # Format:
            #   value_name : {description, required, default_value}
            'Agent': {
                # The 'Agent' option is the only one that MUST be in a module
                'Description': 'Agent to run on.',
                'Required': True,
                'Value': ''
            },
            'Command': {
                'Description': 'Use available Rubeus commands as a one-liner. ',
                'Required': False,
                'Value': '',
            },
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
        # First method: Read in the source script from module_source
        module_source = self.mainMenu.installPath + "/data/module_source/credentials/Invoke-Rubeus.ps1"
        if obfuscate:
            helpers.obfuscate_module(moduleSource=module_source, obfuscationCommand=obfuscationCommand)
            module_source = module_source.replace("module_source", "obfuscated_module_source")
        try:
            f = open(module_source, 'r')
        except:
            print(helpers.color("[!] Could not read module source path at: " + str(module_source)))
            return ""

        module_code = f.read()
        f.close()

        script = module_code
        script_end = 'Invoke-Rubeus -Command "'

        # Add any arguments to the end execution of the script
        if self.options['Command']['Value']:
            script_end += " " + str(self.options['Command']['Value'])

        script_end = script_end.replace('" ', '"')
        script_end += '"'

        if obfuscate:
            script_end = helpers.obfuscate(psScript=script_end, installPath=self.mainMenu.installPath,
                                          obfuscationCommand=obfuscationCommand)
        script += script_end
        script = helpers.keyword_obfuscation(script)

        return script
