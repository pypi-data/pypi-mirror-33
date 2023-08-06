import logging
import os
import tempfile
import urllib.request
# from urllib.error import HTTPError
from urllib.parse import urlparse


#
# from doodledashboard.configuration.config import MissingRequiredOptionException, HandlerCreationException
# from doodledashboard.filters.contains_text import ContainsTextFilter
# from doodledashboard.filters.matches_regex import MatchesRegexFilter
# from doodledashboard.updaters.updater import NotificationUpdater, MessageHandlerConfigSection
#
#
# class ImageNotificationUpdater(NotificationUpdater):
#     """
#     * First message that contains text that matches an image's filter
#     """
#
#     def __init__(self):
#         self._filtered_images = []
#         self._default_image_path = None
#         self._chosen_image_path = None
#
#     def add_image_filter(self, absolute_path, choice_filter=None):
#         if choice_filter:
#             self._filtered_images.append({"path": absolute_path, "filter": choice_filter})
#         else:
#             self._default_image_path = absolute_path
#
#     def update(self, notification, message):
#         for image_filter in self._filtered_images:
#             if image_filter["filter"].filter(message):
#                 self._chosen_image_path = image_filter["path"]
#
#         if self._chosen_image_path:
#             image_path = self._chosen_image_path
#         else:
#             image_path = self._default_image_path
#
#         if image_path:
#             notification.set_path(image_path)
#
#     # def get_image(self):
#     #     if self._chosen_image_path:
#     #         return self._chosen_image_path
#     #     else:
#     #         return self._default_image_path
#
#     # @property
#     # def get_notification_type(self):
#     #     return SupportsImage
#
#     # def __str__(self):
#     #     return "Image handler with %s images" % len(self._filtered_images)


class FileDownloader:

    def __init__(self):
        self._downloaded_files = []
        self._logger = logging.getLogger("doodledashboard")

    def download(self, url):
        fd, path = tempfile.mkstemp("-doodledashboard-%s" % self._extract_filename(url))

        logging.info("Downloading %s to %s", [url, path])
        with urllib.request.urlopen(url) as response, os.fdopen(fd, "wb") as out_file:
            out_file.write(response.read())

        self._downloaded_files.append(path)

        return path

    def get_downloaded_files(self):
        return self._downloaded_files

    @staticmethod
    def _extract_filename(url):
        parsed_url = urlparse(url)
        return os.path.basename(parsed_url.path)


# class ImageMessageHandlerConfigCreator(MessageHandlerConfigSection):
#     def __init__(self, key_value_storage, file_downloader):
#         MessageHandlerConfigSection.__init__(self, key_value_storage)
#         self._file_downloader = file_downloader
#
#     def creates_for_id(self, filter_id):
#         return filter_id == "image-handler"
#
#     def create_handler(self, config_section, key_value_store):
#         handler = ImageNotificationUpdater(key_value_store)
#
#         has_images = "images" in config_section
#         has_default_image = "default-image" in config_section
#
#         if not has_images and not has_default_image:
#             raise MissingRequiredOptionException("Expected 'images' list and/or default-image to exist")
#
#         if has_default_image:
#             try:
#                 image_path = self._file_downloader.download(config_section["default-image"])
#             except HTTPError as err:
#                 raise HandlerCreationException("Error '%s' when downloading %s" % (err.msg, err.url))
#
#             handler.add_image_filter(image_path)
#
#         if has_images:
#             for image_config_section in config_section["images"]:
#                 if "uri" not in image_config_section:
#                     raise MissingRequiredOptionException("Expected 'uri' option to exist")
#
#                 image_uri = image_config_section["uri"]
#                 image_filter = self._create_filter(image_config_section)
#
#                 try:
#                     image_path = self._file_downloader.download(image_uri)
#                 except HTTPError as err:
#                     raise HandlerCreationException(err.url)
#
#                 handler.add_image_filter(image_path, image_filter)
#
#         return handler
#
#     @staticmethod
#     def _create_filter(image_config_section):
#         pattern_exists = "if-matches" in image_config_section
#         contains_exists = "if-contains" in image_config_section
#
#         if not pattern_exists and not contains_exists:
#             raise MissingRequiredOptionException("Expected either 'if-contains' or 'if-matches' option to exist")
#
#         if pattern_exists and contains_exists:
#             raise MissingRequiredOptionException("Expected either 'if-contains' or 'if-matches' option, but not both")
#
#         if pattern_exists:
#             return MatchesRegexFilter(image_config_section["if-matches"])
#         else:
#             return ContainsTextFilter(image_config_section["if-contains"])
