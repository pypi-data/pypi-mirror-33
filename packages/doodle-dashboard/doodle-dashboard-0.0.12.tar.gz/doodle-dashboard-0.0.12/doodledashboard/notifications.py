from abc import ABC

from doodledashboard.configuration.config import ConfigSection


class Notification(ABC):
    def __init__(self):
        self._updater = None
        self._title = None

    def get_updater(self):
        return self._updater

    def set_updater(self, updater):
        self._updater = updater

    def set_title(self, title):
        self._title = title

    def get_title(self):
        return self._title

    def update(self, message):
        if self._updater:
            self._updater.update(self, message)

# class Colour(Notification):
#
#     def __init__(self, updater=None):
#         super().__init__(updater)
#         self._colour = "#000000"
#
#     def set_colour(self, colour):
#         self._colour = colour
#
#     def get_colour(self):
#         return self._colour
#
#     @property
#     def get_id(self):
#         return "colour"
#
#
# class ColourNotificationConfig(NotificationConfig, ConfigSection):
#
#     def create_item(self, config_section):
#         return Colour()
#
#     @property
#     def notification_id(self):
#         return "colour"


class TextNotification(Notification):
    def __init__(self):
        super().__init__()
        self._image_path = None
        self._text = ""

    def set_text(self, text):
        self._text = text

    def get_text(self):
        return self._text

    def __str__(self):
        return "Text notification (title=%s, text=%s)" % (self.get_title(), self.get_text())


class TextNotificationConfig(ConfigSection):

    @property
    def id_key_value(self):
        return "type", "text"

    def create_item(self, config_section):
        notification = TextNotification()

        if "title" in config_section:
            notification.set_title(config_section["title"])

        return notification

#
# class ImageNotification(Notification):
#     def __init__(self, updater=None):
#         super().__init__(updater)
#         self._path = None
#
#     def set_path(self, path):
#         self._path = path
#
#     def get_path(self):
#         return self._path
#
#     @property
#     def get_id(self):
#         return "image"
#
#
# class ImageWithTextNotification(Notification):
#     def __init__(self, updater=None):
#         super().__init__(updater)
#         self._image_path = None
#         self._text = ""
#
#     def set_image_path(self, path):
#         self._image_path = path
#
#     def get_image_path(self):
#         return self._image_path
#
#     def set_text(self, text):
#         self._text = text
#
#     def get_text(self):
#         return self._text
#
#     @property
#     def get_id(self):
#         return "image-with-text"
