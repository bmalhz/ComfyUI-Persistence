"""Persistence module."""
import os
import sys


if not ("pytest" in sys.modules or "PYTEST_CURRENT_TEST" in os.environ):
    from .image.load_image import PersistLoadImage
    from .image_bank.image_bank import PersistImageBank
    from .image_bank.stepped_image_bank import PersistSteppedImageBank
    from .utils.persist_video_settings import PersistVideoSettings
    from .utils.persist_transfer_colors import PersistTransferColors

    NODE_CLASS_MAPPINGS = {
        "PersistLoadImage": PersistLoadImage,
        "PersistTransferColors": PersistTransferColors,
        "PersistSteppedImageBank": PersistSteppedImageBank,
        "PersistVideoSettings": PersistVideoSettings,
        "PersistImageBank": PersistImageBank,
    }

    NODE_DISPLAY_NAME_MAPPINGS = {
        "PersistLoadImage": "PersistLoadImage",
        "PersistTransferColors": "PersistTransferColors",
        "PersistSteppedImageBank": "PersistSteppedImageBank",
        "PersistVideoSettings": "PersistVideoSettings",
        "PersistImageBank": "PersistImageBank",
    }

WEB_DIRECTORY = os.path.join(os.path.dirname(__file__), "web", "js")


def web_directory():
    """Indicate the location of web resources."""
    return WEB_DIRECTORY
