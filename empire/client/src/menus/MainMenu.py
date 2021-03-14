from prompt_toolkit.completion import Completion

from empire.client.src.EmpireCliConfig import empire_config
from empire.client.src.EmpireCliState import state
from empire.client.src.menus.Menu import Menu
from empire.client.src.utils import print_util
from empire.client.src.utils.autocomplete_util import filtered_search_list, position_util
from empire.client.src.utils.cli_util import register_cli_commands, command


def patch_protocol(host):
    return host if host.startswith('http://') or host.startswith('https://') else f'https://{host}'


@register_cli_commands
class MainMenu(Menu):
    def __init__(self):
        super().__init__(display_name='(Empire)')

    def get_completions(self, document, complete_event, cmd_line, word_before_cursor):
        if not state.connected:
            if cmd_line[0] == 'connect' and position_util(cmd_line, 2, word_before_cursor):
                yield Completion('-c', start_position=-len(word_before_cursor))
            elif cmd_line[0] == 'connect' and len(cmd_line) > 1 and cmd_line[1] in ['-c', '--config'] \
                    and position_util(cmd_line, 3, word_before_cursor):
                for server in filtered_search_list(word_before_cursor, empire_config.yaml.get('servers', [])):
                    yield Completion(server, start_position=-len(word_before_cursor))
            elif position_util(cmd_line, 1, word_before_cursor):
                if 'connect'.startswith(word_before_cursor):
                    yield Completion('connect', start_position=-len(word_before_cursor))
        elif position_util(cmd_line, 1, word_before_cursor):
            yield from super().get_completions(document, complete_event, cmd_line, word_before_cursor)

    def autocomplete(self):
        commands = self._cmd_registry + super().autocomplete()
        if state.connected:
            commands.remove('connect')

        return commands

    def get_prompt(self) -> str:
        return f"{self.display_name} > "

    @command
    def connect(self, host: str, config: bool = False, port: int = 1337, socketport: int = 5000, username: str = None,
                password: str = None) -> None:
        """
        Connect to empire instance

        Usage: connect [--config | -c] <host> [--port=<p>] [--socketport=<sp>] [--username=<u>] [--password=<pw>]

        Options:
            host               The url for the empire server or the name of a server config from config.yaml
            --config -c        When true, host is a server name from config.yaml [default: False]
            --port=<p>         Port number for empire server. [default: 1337]
            --socketport=<sp>  Port number for empire socketio server. [default: 5000]
            --username=<u>     Username for empire. if not provided, will attempt to pull from yaml
            --password=<pw>    Password for empire. if not provided, will attempt to pull from yaml
        """
        if state.connected:
            return
        if config is True:
            # Check for name in yaml
            server: dict = empire_config.yaml.get('servers').get(host)
            if not server:
                print(f'Could not find server in config.yaml for {host}')
                server['host'] = patch_protocol(server['host'])
            response = state.connect(server['host'], server['port'], server['socketport'], server['username'],
                                     server['password'])
        else:
            host = patch_protocol(host)
            response = state.connect(host, port, socketport, username, password)

        if hasattr(response, 'status_code'):
            if response.status_code == 200:
                print(print_util.color('[*] Connected to ' + host))
            elif response.status_code == 401:
                print(print_util.color('[!] Invalid username and/or password'))

        else:
            # Print error messages that have reason available
            try:
                print(print_util.color("[!] Error: " + response.args[0].reason.args[0]))
            except:
                print(print_util.color("[!] Error: " + response.args[0]))

    @command
    def disconnect(self):
        """
        Disconnect from an empire instance

        Usage: disconnect
        """
        if not state.connected:
            return

        host = state.host
        state.disconnect()
        print(print_util.color('[*] Disconnected from ' + host))


main_menu = MainMenu()
