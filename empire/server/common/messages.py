"""

Common terminal messages used across Empire.

Titles, agent displays, listener displays, etc.

"""
from __future__ import print_function
from __future__ import absolute_import

from builtins import str
from builtins import range
import os
import time
import textwrap

# Empire imports
from . import helpers


def headless_title(version, num_modules, num_listeners, num_agents):
    """
    Print the tool title, with version.
    """
    os.system('clear')
    print("================================================================================")
    print(" [Empire]  Post-Exploitation Framework")
    print('================================================================================')
    print(" [Version] %s | [Web] https://github.com/BC-SECURITY/Empire" % (version))
    print('================================================================================')
    print("""
   _______ .___  ___. .______    __  .______       _______
  |   ____||   \/   | |   _  \  |  | |   _  \     |   ____|
  |  |__   |  \  /  | |  |_)  | |  | |  |_)  |    |  |__
  |   __|  |  |\/|  | |   ___/  |  | |      /     |   __|
  |  |____ |  |  |  | |  |      |  | |  |\  \----.|  |____
  |_______||__|  |__| | _|      |__| | _| `._____||_______|
""")
    print("       " + helpers.color(str(num_modules), "green") + " modules currently loaded\n")
    print("       " + helpers.color(str(num_listeners), "green") + " listeners currently active\n")
    print("       " + helpers.color(str(num_agents), "green") + " agents currently active\n\n")

    print('                              EMPIRE API REQUIRES:                              ')
    print('================================================================================')
    print(' [Starkiller] Multi-User GUI | [Web] https://github.com/BC-SECURITY/Starkiller')
    print(' [Empire CLI] New Empire CLI | [Web] https://github.com/BC-SECURITY/Empire-Cli \n\n')


def loading():
    """
    Print and ascii loading screen.
    """

    print("""
                              `````````
                         ``````.--::///+
                     ````-+sydmmmNNNNNNN
                   ``./ymmNNNNNNNNNNNNNN
                 ``-ymmNNNNNNNNNNNNNNNNN
               ```ommmmNNNNNNNNNNNNNNNNN
              ``.ydmNNNNNNNNNNNNNNNNNNNN
             ```odmmNNNNNNNNNNNNNNNNNNNN
            ```/hmmmNNNNNNNNNNNNNNNNMNNN
           ````+hmmmNNNNNNNNNNNNNNNNNMMN
          ````..ymmmNNNNNNNNNNNNNNNNNNNN
          ````:.+so+//:---.......----::-
         `````.`````````....----:///++++
        ``````.-/osy+////:::---...-dNNNN
        ````:sdyyydy`         ```:mNNNNM
       ````-hmmdhdmm:`      ``.+hNNNNNNM
       ```.odNNmdmmNNo````.:+yNNNNNNNNNN
       ```-sNNNmdh/dNNhhdNNNNNNNNNNNNNNN
       ```-hNNNmNo::mNNNNNNNNNNNNNNNNNNN
       ```-hNNmdNo--/dNNNNNNNNNNNNNNNNNN
      ````:dNmmdmd-:+NNNNNNNNNNNNNNNNNNm
      ```/hNNmmddmd+mNNNNNNNNNNNNNNds++o
     ``/dNNNNNmmmmmmmNNNNNNNNNNNmdoosydd
     `sNNNNdyydNNNNmmmmmmNNNNNmyoymNNNNN
     :NNmmmdso++dNNNNmmNNNNNdhymNNNNNNNN
     -NmdmmNNdsyohNNNNmmNNNNNNNNNNNNNNNN
     `sdhmmNNNNdyhdNNNNNNNNNNNNNNNNNNNNN
       /yhmNNmmNNNNNNNNNNNNNNNNNNNNNNmhh
        `+yhmmNNNNNNNNNNNNNNNNNNNNNNmh+:
          `./dmmmmNNNNNNNNNNNNNNNNmmd.
            `ommmmmNNNNNNNmNmNNNNmmd:
             :dmmmmNNNNNmh../oyhhhy:
             `sdmmmmNNNmmh/++-.+oh.
              `/dmmmmmmmmdo-:/ossd:
                `/ohhdmmmmmmdddddmh/
                   `-/osyhdddddhyo:
                        ``.----.`

                Welcome to the Empire""")
    time.sleep(3)
    os.system('clear')


def wrap_string(data, width=40, indent=32, indentAll=False, followingHeader=None):
    """
    Print a option description message in a nicely
    wrapped and formatted paragraph.

    followingHeader -> text that also goes on the first line
    """

    data = str(data)

    if len(data) > width:
        lines = textwrap.wrap(textwrap.dedent(data).strip(), width=width)

        if indentAll:
            returnString = ' ' * indent + lines[0]
            if followingHeader:
                returnString += " " + followingHeader
        else:
            returnString = lines[0]
            if followingHeader:
                returnString += " " + followingHeader
        i = 1
        while i < len(lines):
            returnString += "\n" + ' ' * indent + (lines[i]).strip()
            i += 1
        return returnString
    else:
        return data.strip()


def wrap_columns(col1, col2, width1=24, width2=40, indent=31):
    """
    Takes two strings of text and turns them into nicely formatted column output.

    Used by display_module()
    """

    lines1 = textwrap.wrap(textwrap.dedent(col1).strip(), width=width1)
    lines2 = textwrap.wrap(textwrap.dedent(col2).strip(), width=width2)

    result = ''

    limit = max(len(lines1), len(lines2))

    for x in range(limit):

        if x < len(lines1):
            if x != 0:
                result += ' ' * indent
            result += '{line: <0{width}s}'.format(width=width1, line=lines1[x])
        else:
            if x == 0:
                result += ' ' * width1
            else:
                result += ' ' * (indent + width1)

        if x < len(lines2):
            result += '  ' + '{line: <0{width}s}'.format(width=width2, line=lines2[x])

        if x != limit-1:
            result += "\n"

    return result


def display_agent(agent, returnAsString=False):
    """
    Display an agent all nice-like.
    Takes in the tuple of the raw agent database results.
    """

    if returnAsString:
        agentString = "\n[*] Agent info:\n"
        for key, value in agent.items():
            if key != 'functions' and key != 'takings' and key != 'results':
                agentString += "  %s\t%s\n" % ('{0: <16}'.format(key), wrap_string(value, width=70))
        return agentString + '\n'
    else:
        print(helpers.color("\n[*] Agent info:\n"))
        for key, value in agent.items():
            if key != 'functions' and key != 'takings' and key != 'results':
                print("\t%s\t%s" % (helpers.color('{0: <16}'.format(key), "blue"), wrap_string(value, width=70)))
        print('')
