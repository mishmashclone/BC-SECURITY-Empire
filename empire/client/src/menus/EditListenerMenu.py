import textwrap

from prompt_toolkit.completion import Completion

from empire.client.src.EmpireCliState import state
from empire.client.src.menus.UseMenu import UseMenu
from empire.client.src.utils import print_util, table_util
from empire.client.src.utils.autocomplete_util import filtered_search_list, position_util
from empire.client.src.utils.cli_util import register_cli_commands, command


@register_cli_commands
class EditListenerMenu(UseMenu):
    def __init__(self):
        super().__init__(display_name='editlistener', selected='', record=None, record_options=None)

    def autocomplete(self):
        return self._cmd_registry + super().autocomplete()

    def get_completions(self, document, complete_event, cmd_line, word_before_cursor):
        if cmd_line[0] in ['edit'] and position_util(cmd_line, 2, word_before_cursor):
            for option in filtered_search_list(word_before_cursor, self.record_options):
                yield Completion(option, start_position=-len(word_before_cursor))
        else:
            yield from super().get_completions(document, complete_event, cmd_line, word_before_cursor)

    def on_enter(self, **kwargs) -> bool:
        if 'selected' not in kwargs:
            return False
        else:
            self.use(kwargs['selected'])
            #self.info()
            self.options()
            return True

    def use(self, module: str) -> None:
        """
        Use the selected listener

        Usage: use <module>
        """
        if module not in state.listeners:
            return None

        self.selected = module
        self.record = state.listeners[self.selected]['options']
        self.record_options = state.get_listener_options(self.selected)['listeneroptions']

    @command
    def options(self) -> None:
        """
        Get option details for the selected listener

        Usage: options
        """
        if self.selected not in state.listeners:
            return None

        listener_list = []

        for key, value in state.listeners[self.selected]['options'].items():
            values = list(map(lambda x: '\n'.join(textwrap.wrap(str(x), width=40)), value.values()))
            values.reverse()
            temp = [key] + values
            listener_list.append(temp)

        listener_list.insert(0, ['Name', 'Value', 'Required', 'Description'])

        table_util.print_table(listener_list, self.selected)

    @command
    def edit(self, key: str, value: str):
        """
        Edit a field for the current record

        Usage: edit <key> <value>
        """
        if state.listeners[self.selected]['enabled'] == False:
            if value.startswith("\"") and value.endswith("\""):
                value = value[1:-1]
            if key in self.record_options:
                response = state.edit_listener(self.selected, key, value)
                if 'success' in response.keys():
                    print(print_util.color(f'[*] Updated listener {self.selected}: {key} to {value}'))
                elif 'error' in response.keys():
                    print(print_util.color('[!] Error: ' + response['error']))
            else:
                print(print_util.color(f'Could not find field: {key}'))
        else:
            print(print_util.color(f'[!] Listener must be disabled before edits'))

    @command
    def kill(self) -> None:
        """
        Kill the selected listener

        Usage: kill
        """
        response = state.kill_listener(self.selected)
        if 'success' in response.keys():
            print(print_util.color('[*] Listener ' + self.selected + ' killed'))
        elif 'error' in response.keys():
            print(print_util.color('[!] Error: ' + response['error']))

    @command
    def enable(self) -> None:
        """
        Enable the selected listener

        Usage: enable
        """
        response = state.enable_listener(self.selected)
        if 'success' in response.keys():
            print(print_util.color('[*] Listener ' + self.selected + ' enabled'))
        elif 'error' in response.keys():
            print(print_util.color('[!] Error: ' + response['error']))

    @command
    def disable(self) -> None:
        """
        Disable the selected listener

        Usage: disable
        """
        response = state.disable_listener(self.selected)
        if 'success' in response.keys():
            print(print_util.color('[*] Listener ' + self.selected + ' disabled'))
        elif 'error' in response.keys():
            print(print_util.color('[!] Error: ' + response['error']))


edit_listener_menu = EditListenerMenu()
