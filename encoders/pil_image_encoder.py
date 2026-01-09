"""PilImageEncoder module."""
import torch
import numpy as np
from PIL import Image
from .image_encoder import ImageEncoder


class PilImageEncoder(ImageEncoder):
    """PilImageEncoder implementation."""

    COMPRESS_LEVEL = 4

    @staticmethod
    def file_extension() -> str:
        """Get file extension (with initial dot)."""
        return ".webp"

    @staticmethod
    def get_name() -> str:
        """Get the unique name of the encoder."""
        return "pil"

    @staticmethod
    def save_image(image: torch.Tensor, save_path: str):
        """
        Save a Tensor image to the provided path.

        :param image: Tensor containing an image
        :type image: torch.Tensor
        :param save_path: save path without extension
        :type save_path: str
        """
        i = 255.0 * image.cpu().numpy()
        img = Image.fromarray(np.clip(i, 0, 255).astype(np.uint8))

        file_path = f"{save_path}{PilImageEncoder.file_extension()}"
        img.save(file_path, compress_level=PilImageEncoder.COMPRESS_LEVEL)

    @staticmethod
    def load_image(image_path: str) -> torch.Tensor:
        """
        Load image from a given path.

        :param image_path: path without extension
        :type image_path: str
        :return: Image as a Tensor
        :rtype: Tensor
        """
        i = Image.open(f"{image_path}{PilImageEncoder.file_extension()}")

        if i.mode == "I":
            i = i.point(lambda i: i * (1 / 255))
        image = i.convert("RGB")

        image = np.array(image).astype(np.float32) / 255.0
        image = torch.from_numpy(image)[None,]
        return image.squeeze(0)  # remove batch dimension
