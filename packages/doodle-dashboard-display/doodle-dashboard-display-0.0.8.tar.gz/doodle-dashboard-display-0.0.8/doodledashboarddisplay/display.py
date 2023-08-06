from abc import ABC, abstractmethod


class SupportsColourFill(ABC):
    """Mixin that indicates the display supports a colour fill"""

    @abstractmethod
    def colour_fill(self, colour):
        pass


class SupportsText(ABC):
    """Mixin that indicates the display supports showing text"""

    @abstractmethod
    def text(self, text):
        pass


class SupportsImageWithText(ABC):
    """Mixin that indicates the display supports showing an image with text"""

    @abstractmethod
    def image_with_text(self, image_path, text):
        pass


class SupportsImage(ABC):
    """Mixin that indicates the display supports showing an image"""

    @abstractmethod
    def image(self, image_path):
        pass


class Display(ABC):
    """Base class that every display must implement. Support for Notification types that are then supported are
    added via mixins."""

    @staticmethod
    @abstractmethod
    def get_id():
        pass
