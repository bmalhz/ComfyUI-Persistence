"""SafetensorsImageEncoder module."""
import torch
import tempfile
import zstandard as zstd
from safetensors.torch import save_file, load_file
from .image_encoder import ImageEncoder

ZSTD_COMPRESSION_LEVEL = 5


class SafetensorsImageEncoder(ImageEncoder):
    """SafetensorsImageEncoder implementation."""

    @staticmethod
    def get_name() -> str:
        """Get the unique name of the encoder."""
        return "safetensors"

    @staticmethod
    def file_extension() -> str:
        """Get file extension (with initial dot)."""
        return ".safetensors.zst"

    @staticmethod
    def save_image(image: torch.Tensor, save_path: str):
        """
        Save a Tensor image to the provided path.

        :param image: Tensor containing an image
        :type image: torch.Tensor
        :param save_path: save path without extension
        :type save_path: str
        """
        with tempfile.NamedTemporaryFile(delete=True) as save_tmp_filename:
            save_file(
                {"img": image.clone().contiguous()}, filename=save_tmp_filename.name
            )

            z_comp = zstd.ZstdCompressor(level=ZSTD_COMPRESSION_LEVEL)
            with open(save_tmp_filename.name, "rb") as ifh, open(
                f"{save_path}{SafetensorsImageEncoder.file_extension()}", "wb"
            ) as ofh:
                z_comp.copy_stream(ifh, ofh)

    @staticmethod
    def load_image(image_path: str) -> torch.Tensor:
        """
        Load image from a given path.

        :param image_path: path without extension
        :type image_path: str
        :return: Image as a Tensor
        :rtype: Tensor
        """
        with tempfile.NamedTemporaryFile(delete=True) as load_tmp_filename:
            with open(
                f"{image_path}{SafetensorsImageEncoder.file_extension()}", "rb"
            ) as cached_file, open(
                load_tmp_filename.name, "wb"
            ) as uncompressed_cached_file:
                z_decomp = zstd.ZstdDecompressor()
                z_decomp.copy_stream(cached_file, uncompressed_cached_file)
            return load_file(load_tmp_filename.name).get("img")  # type: ignore
