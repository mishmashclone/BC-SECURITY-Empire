from __future__ import print_function
from builtins import str
from builtins import object
from lib.common import helpers


class Module(object):

    def __init__(self, mainMenu, params=[]):

        # Metadata info about the module, not modified during runtime
        self.info = {
            # Name for the module that will appear in module menus
            'Name': 'Invoke-SauronEye',

            # List of one or more authors for the module
            'Author': ['@vivami', '@S3cur3Th1sSh1t'],

            # More verbose multi-line description of the module
            'Description': ("SauronEye is a search tool built to aid red teams in finding files containing "
                            "specific keywords."),

            'Software': '',

            'Techniques': ['T1083'],

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
                'https://github.com/vivami/SauronEye'
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
            'filetypes ': {
                'Description': 'Filetypes to search for/in',
                'Required': False,
                'Value': '.txt .doc .docx .xls',
            },
            'contents': {
                'Description': 'Search file contents',
                'Required': False,
                'Value': 'True',
            },
            'keywords': {
                'Description': 'Keywords to search for',
                'Required': False,
                'Value': 'password pass*',
            },
            'directories': {
                'Description': "Directories to search",
                'Required': False,
                'Value': '',
            },
            'maxfilesize': {
                'Description': "Max file size to search contents in, in kilobytes",
                'Required': False,
                'Value': '',
            },
            'beforedate': {
                'Description': 'Filter files last modified before this date, format: yyyy-MM-dd',
                'Required': False,
                'Value': '',
            },
            'afterdate': {
                'Description': "Filter files last modified after this date, format: yyyy-MM-dd",
                'Required': False,
                'Value': '',
            },
            'systemdirs': {
                'Description': 'Search in filesystem directories %APPDATA% and %WINDOWS%',
                'Required': False,
                'Value': '',
            },
            'vbamacrocheck': {
                'Description': 'Check if 2003 Office files (*.doc and *.xls) contain a VBA macro',
                'Required': False,
                'Value': 'True',
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
        module_source = self.mainMenu.installPath + "/data/module_source/collection/Invoke-SauronEye.ps1"
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
        script_end = 'Invoke-SauronEye -Command "'

        # Add any arguments to the end execution of the script
        for option, values in self.options.items():
            if option.lower() != "agent":
                if values['Value'] and values['Value'] != '':
                    if values['Value'].lower() == "true":
                        # if we're just adding a switch
                        script_end += " --" + str(option)
                    else:
                        script_end += " --" + str(option) + " " + str(values['Value'])
        script_end += '"'

        if obfuscate:
            script_end = helpers.obfuscate(psScript=script_end, installPath=self.mainMenu.installPath,
                                           obfuscationCommand=obfuscationCommand)
        script += script_end
        script = helpers.keyword_obfuscation(script)

        return script
