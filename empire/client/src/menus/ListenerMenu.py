import string
import textwrap

from prompt_toolkit.completion import Completion

from empire.client.src.EmpireCliState import state
from empire.client.src.menus.Menu import Menu
from empire.client.src.utils import table_util, date_util
from empire.client.src.utils.autocomplete_util import filtered_search_list, position_util
from empire.client.src.utils.cli_util import register_cli_commands, command


@register_cli_commands
class ListenerMenu(Menu):
    def __init__(self):
        super().__init__(display_name='listeners', selected='')

    def autocomplete(self):
        return self._cmd_registry + super().autocomplete()

    def get_completions(self, document, complete_event, cmd_line, word_before_cursor):
        if cmd_line[0] in ['kill', 'options'] and position_util(cmd_line, 2, word_before_cursor):
            for listener in filtered_search_list(word_before_cursor, state.listeners.keys()):
                yield Completion(listener, start_position=-len(word_before_cursor))
        elif position_util(cmd_line, 1, word_before_cursor):
            yield from super().get_completions(document, complete_event, cmd_line, word_before_cursor)

    def on_enter(self):
        self.list()
        return True

    @command
    def list(self) -> None:
        """
        Get running/available listeners

        Usage: list
        """
        listener_list = list(map(lambda x: [x['ID'], x['name'], x['module'], x['listener_category'], date_util.humanize_datetime(x['created_at'])],
                                 state.listeners.values()))
        listener_list.insert(0, ['ID', 'Name', 'Module', 'Listener Category', 'Created At'])

        table_util.print_table(listener_list, 'Listeners List')

    @command
    def options(self, listener_name: str) -> None:
        """
        Get option details for the selected listener

        Usage: options <listener_name>
        """
        if listener_name not in state.listeners:
            return None

        listener_list = []

        for key, value in state.listeners[listener_name]['options'].items():
            values = list(map(lambda x: '\n'.join(textwrap.wrap(str(x), width=40)), value.values()))
            values.reverse()
            temp = [key] + values
            listener_list.append(temp)

        listener_list.insert(0, ['Name', 'Value', 'Required', 'Description'])

        table_util.print_table(listener_list, listener_name)

    @command
    def kill(self, listener_name: str) -> None:
        """
        Kill the selected listener

        Usage: kill <listener_name>
        """
        state.kill_listener(listener_name)


listener_menu = ListenerMenu()
