import click
from doodledashboard.display import Display
from doodledashboard.notifications import TextNotification


class ConsoleDisplay(Display):

    def __init__(self, size=click.get_terminal_size()):
        self._size = size

    def draw(self, notification):
        click.clear()
        click.echo(notification.get_text())

    @staticmethod
    def get_supported_notifications():
        return [TextNotification]

    @staticmethod
    def get_id():
        return "console"

    def __str__(self):
        return "Console display"
