from __future__ import print_function
from builtins import str
from builtins import object
from lib.common import helpers


class Module(object):

    def __init__(self, mainMenu, params=[]):

        # Metadata info about the module, not modified during runtime
        self.info = {
            # Name for the module that will appear in module menus
            'Name': 'Invoke-winPEAS',

            # List of one or more authors for the module
            'Author': ['@carlospolop', '@S3cur3Th1sSh1t'],

            # More verbose multi-line description of the module
            'Description': ("WinPEAS is a script that search for possible paths to escalate privileges on Windows hosts."),

            'Software': '',

            'Techniques': ['T1046'],

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
                'https://github.com/carlospolop/privilege-escalation-awesome-scripts-suite/tree/master/winPEAS'
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
            'Full': {
                'Description': 'Default all checks (except CMD checks) are executed',
                'Required': False,
                'Value': 'True',
            },
            'Searchfast': {
                'Description': 'Avoid sleeping while searching files (notable amount of resources).',
                'Required': False,
                'Value': '',
            },
            'Searchall': {
                'Description': 'Search all known filenames whith possible credentials.',
                'Required': False,
                'Value': '',
            },
            'Cmd': {
                'Description': 'Obtain wifi, cred manager and clipboard information executing CMD commands.',
                'Required': False,
                'Value': '',
            },
            'Systeminfo': {
                'Description': 'Search system information.',
                'Required': False,
                'Value': '',
            },
            'Userinfo': {
                'Description': 'Search user information.',
                'Required': False,
                'Value': '',
            },
            'Procesinfo': {
                'Description': 'Search processes information.',
                'Required': False,
                'Value': '',
            },
            'Servicesinfo': {
                'Description': 'Search services information.',
                'Required': False,
                'Value': '',
            },
            'Applicationsinfo': {
                'Description': 'Search installed applications information.',
                'Required': False,
                'Value': '',
            },
            'Networkinfo': {
                'Description': 'Search network information.',
                'Required': False,
                'Value': '',
            },
            'Windowscreds': {
                'Description': 'Search windows information.',
                'Required': False,
                'Value': '',
            },
            'Browserinfo': {
                'Description': 'Search browser information.',
                'Required': False,
                'Value': '',
            },
            'Filesinfo': {
                'Description': 'Search files that can contains credentials.',
                'Required': False,
                'Value': '',
            },
            'Color': {
                'Description': 'Enable colored output.',
                'Required': True,
                'Value': 'True',
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
        module_source = self.mainMenu.installPath + "/data/module_source/privesc/Invoke-winPEAS.ps1"
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
        script_end = 'Invoke-winPEAS -Command "'

        # Add any arguments to the end execution of the script
        if self.options['Searchfast']['Value'].lower() == 'true':
            script_end += " searchfast"
        if self.options['Searchall']['Value'].lower() == 'true':
            script_end += " searchall"
        if self.options['Cmd']['Value'].lower() == 'true':
            script_end += " cmd"
        if self.options['Systeminfo']['Value'].lower() == 'true':
            script_end += " systeminfo"
        if self.options['Userinfo']['Value'].lower() == 'true':
            script_end += " userinfo"
        if self.options['Procesinfo']['Value'].lower() == 'true':
            script_end += " procesinfo"
        if self.options['Servicesinfo']['Value'].lower() == 'true':
            script_end += " servicesinfo"
        if self.options['Applicationsinfo']['Value'].lower() == 'true':
            script_end += " applicationsinfo"
        if self.options['Networkinfo']['Value'].lower() == 'true':
            script_end += " networkinfo"
        if self.options['Windowscreds']['Value'].lower() == 'true':
            script_end += " windowscreds"
        if self.options['Browserinfo']['Value'].lower() == 'true':
            script_end += " browserinfo"
        if self.options['Filesinfo']['Value'].lower() == 'true':
            script_end += " filesinfo"
        if self.options['Color']['Value'].lower() == 'false':
            script_end += " notansi"
        if self.options['Full']['Value'].lower() == 'true':
            script_end += " +"

        script_end = script_end.replace('" ', '"')
        script_end += '"'

        if obfuscate:
            script_end = helpers.obfuscate(psScript=script_end, installPath=self.mainMenu.installPath,
                                          obfuscationCommand=obfuscationCommand)
        script += script_end
        script = helpers.keyword_obfuscation(script)

        return script
