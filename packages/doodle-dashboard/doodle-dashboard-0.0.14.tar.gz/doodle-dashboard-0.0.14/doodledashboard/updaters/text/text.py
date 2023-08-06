from doodledashboard.configuration.config import ConfigSection

from doodledashboard.updaters.updater import NotificationUpdater


class TextNotificationUpdater(NotificationUpdater):

    def _update(self, notification, message):
        notification.set_text(message.get_text())


class TextNotificationUpdaterConfig(ConfigSection):

    @property
    def id_key_value(self):
        return "name", "text-from-message"

    def create_item(self, config_section):
        return TextNotificationUpdater()
