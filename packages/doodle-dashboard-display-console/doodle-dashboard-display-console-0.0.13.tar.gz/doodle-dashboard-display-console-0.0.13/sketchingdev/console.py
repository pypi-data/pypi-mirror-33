import click
from doodledashboard.display import Display
from doodledashboard.notifications import TextNotification, ImageNotification


class ConsoleDisplay(Display):

    def __init__(self, size=click.get_terminal_size()):
        self._size = size

    def draw(self, notification):
        click.clear()
        if isinstance(notification, TextNotification):
            click.echo(notification.get_text())
        elif isinstance(notification, ImageNotification):
            click.echo("Image: %s" % notification.get_image_path())

    @staticmethod
    def get_supported_notifications():
        return [TextNotification, ImageNotification]

    @staticmethod
    def get_id():
        return "console"

    def __str__(self):
        return "Console display"
