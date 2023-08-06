from abc import abstractmethod, ABC
from doodledashboard.display import Display
from pkg_resources import iter_entry_points

from doodledashboard.configuration.config import InvalidConfigurationException
from doodledashboard.datafeeds.datetime import DateTimeFeedSection
from doodledashboard.datafeeds.rss import RssFeedSection
from doodledashboard.datafeeds.slack import SlackFeedSection
from doodledashboard.datafeeds.text import TextFeedSection
from doodledashboard.filters.contains_text import ContainsTextFilterConfig
from doodledashboard.filters.matches_regex import MatchesRegexFilterConfig
from doodledashboard.notifications import TextNotificationConfig
from doodledashboard.updaters.text.text import TextNotificationUpdaterConfig


class ComponentsLoader(ABC):
    @abstractmethod
    def configure(self, dashboard_config):
        pass


def validate_displays(displays):
    for display in displays:
        if not issubclass(display, Display):
            raise InvalidConfigurationException(
                "Display loaded does not implement Display base class. Contact the Display's creator"
            )
    return displays


class StaticDisplayLoader(ComponentsLoader):
    displays = []

    def configure(self, dashboard_config):
        dashboard_config.add_available_displays(StaticDisplayLoader.displays)


class ExternalPackageLoader(ComponentsLoader):

    _DISPLAYS_GROUP_NAME = "doodledashboard.customdisplays"

    def configure(self, dashboard_config):
        dashboard_config.add_available_displays(ExternalPackageLoader._find_displays())

    @staticmethod
    def _find_displays():
        displays = []
        for entry_point in iter_entry_points(ExternalPackageLoader._DISPLAYS_GROUP_NAME):
            displays.append(entry_point.load())

        return displays


class InternalPackageLoader(ComponentsLoader):

    def configure(self, dashboard_config):
        dashboard_config.add_data_feed_creators(InternalPackageLoader._find_data_feed_creators())
        dashboard_config.add_notification_creators(InternalPackageLoader._find_notification_creators())
        dashboard_config.add_notification_updater_creators(InternalPackageLoader._find_notification_updater_creators())
        dashboard_config.add_filter_creators(InternalPackageLoader._find_filter_creators())

    @staticmethod
    def _find_data_feed_creators():
        return [
            RssFeedSection(),
            SlackFeedSection(),
            DateTimeFeedSection(),
            TextFeedSection()
        ]

    @staticmethod
    def _find_notification_creators():
        return [TextNotificationConfig()]

    @staticmethod
    def _find_notification_updater_creators():
        return [TextNotificationUpdaterConfig()]

    @staticmethod
    def _find_filter_creators():
        return [
            MatchesRegexFilterConfig(),
            ContainsTextFilterConfig()
        ]
