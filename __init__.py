"""Persistence module."""
import os
import sys


if not ("pytest" in sys.modules or "PYTEST_CURRENT_TEST" in os.environ):
    from .image_bank.image_bank import PersistImageBank
    from .image_bank.stepped_image_bank import PersistSteppedImageBank

    NODE_CLASS_MAPPINGS = {
        "PersistSteppedImageBank": PersistSteppedImageBank,
        "PersistImageBank": PersistImageBank,
    }

    NODE_DISPLAY_NAME_MAPPINGS = {
        "PersistSteppedImageBank": "[Persist] SteppedImageBank",
        "PersistImageBank": "[Persist] ImageBank",
    }

WEB_DIRECTORY = os.path.join(os.path.dirname(__file__), "web")


def web_directory():
    """Indicate the location of web resources."""
    return WEB_DIRECTORY
