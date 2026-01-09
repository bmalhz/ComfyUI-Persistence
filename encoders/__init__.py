"""Encoders module."""
from typing import Dict

from .image_encoder import ImageEncoder
from .safetensor_image_encoder import SafetensorsImageEncoder
from .pil_image_encoder import PilImageEncoder


def get_encoders() -> Dict[str, ImageEncoder]:
    """
    Get available encoders.

    :return: Encoders implementations
    :rtype: Dict[str, ImageEncoder]
    """
    return {"safetensors": SafetensorsImageEncoder, "pil": PilImageEncoder}  # type: ignore
