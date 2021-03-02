"""
Parse arguments to be used in other modules.
"""
import argparse

parser = argparse.ArgumentParser()

launcher_type = parser.add_argument_group('Client/Server Launcher')
launcher_type.add_argument('--server', action='store_true', help='Launcher Empire Teamserver')
launcher_type.add_argument('--client', action='store_true', help='Launcher Empire CLI')

generalGroup = parser.add_argument_group('General Options')
generalGroup.add_argument('--debug', nargs='?', const='1',
                          help='Debug level for output (default of 1, 2 for msg display).')
generalGroup.add_argument('--reset', action='store_true', help="Resets Empire's database to defaults.")
generalGroup.add_argument('-v', '--version', action='store_true', help='Display current Empire version.')
generalGroup.add_argument('-r', '--resource', nargs=1,
                          help='Run the Empire commands in the specified resource file after startup.')

restGroup = parser.add_argument_group('RESTful API Options')
launchGroup = restGroup.add_mutually_exclusive_group()
launchGroup.add_argument('--rest', action='store_true', help='No longer needed, RESTful API is on by default.')
launchGroup.add_argument('--headless', action='store_true',
                         help='Run the RESTful API and Socket Server headless without the usual interface.')
restGroup.add_argument('--restip', nargs=1, help='IP to bind the Empire RESTful API on. Defaults to 0.0.0.0')
restGroup.add_argument('--restport', type=int, nargs=1, help='Port to run the Empire RESTful API on. Defaults to 1337')
restGroup.add_argument('--socketport', type=int, nargs=1, help='Port to run socketio on. Defaults to 5000')
restGroup.add_argument('--username', nargs=1,
                       help='Start the RESTful API with the specified username instead of pulling from empire.db')
restGroup.add_argument('--password', nargs=1,
                       help='Start the RESTful API with the specified password instead of pulling from empire.db')

args = parser.parse_args()
