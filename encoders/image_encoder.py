"""ImageEncoder base class."""
import torch
from abc import ABC, abstractmethod


class ImageEncoder(ABC):
    """ImageEncoder implementation."""

    @staticmethod
    @abstractmethod
    def file_extension() -> str:
        """Get file extension (with initial dot)."""
        pass

    @staticmethod
    @abstractmethod
    def get_name() -> str:
        """Get the unique name of the encoder."""
        pass

    @staticmethod
    @abstractmethod
    def save_image(image: torch.Tensor, save_path: str):
        """
        Save a Tensor image to the provided path.

        :param image: Tensor containing an image
        :type image: torch.Tensor
        :param save_path: save path without extension
        :type save_path: str
        """
        pass

    @staticmethod
    @abstractmethod
    def load_image(image_path: str) -> torch.Tensor:  # type: ignore
        """
        Load image from a given path.

        :param image_path: path without extension
        :type image_path: str
        :return: Image as a Tensor
        :rtype: Tensor
        """
        pass
