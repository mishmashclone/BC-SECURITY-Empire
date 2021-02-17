from __future__ import print_function

from builtins import str

from empire.server.common import helpers


class Module:
    def __init__(self, mainMenu, params=[]):
        self.info = {
            'Name': 'PrivescCheck',
            'Author': ['@itm4n'],
            'Description': ('Find Windows local privilege escalation vulnerabilities.'),
            'Software': '',
            'Techniques': ['T1046'],
            'Background': True,
            'OutputExtension': None,
            'NeedsAdmin': False,
            'OpsecSafe': True,
            'Language': 'powershell',
            'MinLanguageVersion': '2',

            'Comments': [
                'https://github.com/itm4n/PrivescCheck'
            ]
        }
        # any options needed by the module, settable during runtime
        self.options = {
            # format:
            #   value_name : {description, required, default_value}
            'Agent': {
                'Description': 'Agent to run module on.',
                'Required': True,
                'Value': ''
            },
            'Extended': {
                'Description': 'Set this flag to enable extended checks.',
                'Required': True,
                'Value': 'False'
            },
            'Format': {
                'Description': 'Select the format of the output file (e.g.: TXT, HTML or CSV).',
                'Required': True,
                'Value': 'TXT'
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
        moduleName = self.info["Name"]

        # read in the common powerup.ps1 module source code
        moduleSource = self.mainMenu.installPath + "/data/module_source/privesc/PrivescCheck.ps1"
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
        # # get just the code needed for the specified function
        # script = helpers.generate_dynamic_powershell_script(moduleCode, moduleName)
        script = moduleCode
        scriptEnd = "Invoke-PrivescCheck"

        if obfuscate:
            scriptEnd = helpers.obfuscate(self.mainMenu.installPath, psScript=scriptEnd,
                                          obfuscationCommand=obfuscationCommand)
        script += scriptEnd
        script = helpers.keyword_obfuscation(script)

        return script
