from empire.client.src.EmpireCliState import state
from empire.client.src.menus.Menu import Menu
from empire.client.src.utils import table_util
from empire.client.src.utils.autocomplete_util import position_util
from empire.client.src.utils.cli_util import register_cli_commands, command


@register_cli_commands
class CredentialMenu(Menu):
    def __init__(self):
        super().__init__(display_name='credentials', selected='')

    def autocomplete(self):
        return self._cmd_registry + super().autocomplete()

    def get_completions(self, document, complete_event, cmd_line, word_before_cursor):
        if position_util(cmd_line, 1, word_before_cursor):
            yield from super().get_completions(document, complete_event, cmd_line, word_before_cursor)

    def on_enter(self):
        self.list()
        return True

    @command
    def list(self) -> None:
        """
        Get running/available agents

        Usage: list
        """
        cred_list = list(map(
            lambda x: [x['ID'], x['credtype'], x['domain'], x['username'], x['host'], x['password']],
            state.get_credentials()))
        cred_list.insert(0, ['ID', 'CredType', 'Domain', 'UserName', 'Host', 'Password/Hash'])

        table_util.print_table(cred_list, 'Credentials')


credential_menu = CredentialMenu()
