from __future__ import print_function
from builtins import str
from builtins import object
from lib.common import helpers


class Module(object):

    def __init__(self, mainMenu, params=[]):

        # Metadata info about the module, not modified during runtime
        self.info = {
            # Name for the module that will appear in module menus
            'Name': 'Invoke-Seatbelt',

            # List of one or more authors for the module
            'Author': ['@S3cur3Th1sSh1t', '@Cx01N'],

            # More verbose multi-line description of the module
            'Description': ('Seatbelt is a C# project that performs a number of security oriented '
                            'host-survey "safety checks" relevant from both offensive and defensive '
                            'security perspectives.'),

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
                'https://github.com/GhostPack/Seatbelt'
            ]
        }

        # Any options needed by the module, settable during runtime
        self.options = {
            # Format:
            #   value_name : {description, required, default_value}
            'Agent': {
                # The 'Agent' option is the only one that MUST be in a module
                'Description':   'Agent to run on.',
                'Required'   :   True,
                'Value'      :   ''
            },
            'Command': {
                'Description':   'Use available Seatbelt commands (AntiVirus, PowerShellEvents, UAC, etc). ',
                'Required'   :   False,
                'Value'      :   ''
            },
            'Group': {
                'Description': 'Runs a predefined group of commands (All, User, System, Slack, Chrome, Remote'
                               ', Misc)',
                'Required': False,
                'Value': 'all'
            },
            'Computername': {
                'Description': 'Remote system to run enumeration against. This is performed over WMI via queries'
                               'for WMI classes and WMI StdRegProv for registry enumeration.',
                'Required': False,
                'Value': ''
            },
            'Username': {
                'Description': 'Alternate username for remote enumeration.',
                'Required': False,
                'Value': ''
            },
            'Password': {
                'Description': 'Alternate password for remote enumeration.',
                'Required': False,
                'Value': ''
            },
            'Full': {
                'Description': 'Display all results.',
                'Required': False,
                'Value': 'True'
            },
            'Quiet': {
                'Description': 'Runs in Quiet Mode.',
                'Required': False,
                'Value': 'False'
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
        moduleSource = self.mainMenu.installPath + "/data/module_source/situational_awareness/host/Invoke-Seatbelt.ps1"
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
        scriptEnd = 'Invoke-Seatbelt -Command "'

        # Add any arguments to the end execution of the script
        if self.options['Command']['Value']:
            scriptEnd += " " + str(self.options['Command']['Value'])
        if self.options['Group']['Value']:
            scriptEnd += " -group=" + str(self.options['Group']['Value'])
        if self.options['Computername']['Value']:
            scriptEnd += " -computername=" + str(self.options['Computername']['Value'])
        if self.options['Username']['Value']:
            scriptEnd += " -username=" + str(self.options['Username']['Value'])
        if self.options['Password']['Value']:
            scriptEnd += " -password=" + str(self.options['Password']['Value'])
        if self.options['Full']['Value'].lower() == 'true':
            scriptEnd += " -full"
        if self.options['Quiet']['Value'] .lower() == 'true':
            scriptEnd += " -q"

        scriptEnd = scriptEnd.replace('" ', '"')
        scriptEnd += '"'

        if obfuscate:
            scriptEnd = helpers.obfuscate(psScript=scriptEnd, installPath=self.mainMenu.installPath, obfuscationCommand=obfuscationCommand)
        script += scriptEnd
        # Restore the regular STDOUT object
        return script
