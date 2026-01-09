"""Image Bank implementation."""
import os
import logging
import torch
from typing import Any, Dict
from server import PromptServer
from comfy_execution.graph_utils import GraphBuilder

from . import DEFAULT_BANK_ENCODER, DEFAULT_CACHE_NAME
from . import get_bank_path, is_bank_valid, get_cache_path, read_bank_metadata, get_bank_fingerprint, write_bank_metadata

from ..image.image_utils import split_images
from ..encoders import get_encoders
from ..encoders.image_encoder import ImageEncoder


class PersistImageBank:
    """PersistImageBank node."""

    _logger = logging.getLogger("comfy.custom.persistence.PersistImageBank")

    @classmethod
    def INPUT_TYPES(cls) -> Dict[str, Any]:
        """INPUT_TYPES definition."""
        from comfy.comfy_types.node_typing import IO

        cache_names = [DEFAULT_CACHE_NAME]

        return {
            "required": {
                "cache_name": (cache_names,),
                "bank_name": ("STRING",),
                "bank_id": (IO.ANY,),
                "selected_index": ("INT", {"min": -1, "default": -1}),
                "enable_write": ("BOOLEAN", {"default": True}),
            },
            "optional": {
                "images": ("IMAGE", {"lazy": True}),
            },
        }

    RETURN_TYPES = (
        "IMAGE",
        "IMAGE",
    )
    RETURN_NAMES = (
        "images",
        "selected_image",
    )
    FUNCTION = "process"
    CATEGORY = "Persistence"

    def __get_encoder(self, encoder_name: str = DEFAULT_BANK_ENCODER) -> ImageEncoder:
        encoder = get_encoders().get(encoder_name)
        if not encoder:
            raise Exception(f"Encoder {encoder_name} does not exist!")
        return encoder

    def check_lazy_status(
        self,
        **kwargs
    ):
        """
        Check if input images are required.

        :param self: self
        :param cache_name: Name of the Cache to use
        :param bank_name: Name of this bank
        :param bank_id: Bank configuration parameters
        """
        cache_name = kwargs.get("cache_name", DEFAULT_CACHE_NAME)
        bank_name = kwargs.get("bank_name")
        bank_id = kwargs.get("bank_id")

        bank_path = get_bank_path(
            cache_path=get_cache_path(cache_name=cache_name), bank_name=bank_name, bank_id=bank_id
        )

        if is_bank_valid(bank_path=bank_path):
            self._logger.info(f"{bank_path} images are already cached!")
            return []

        self._logger.info(f"{bank_path} images are NOT already cached!")
        return ["images"]

    def process(
        self,
        cache_name: str,
        bank_name: str,
        bank_id: str,
        selected_index: int,
        enable_write: bool,
        images=None,
    ):
        """
        Run the node.

        :param self:
        :param cache_name: name of the cache in the configuration
        :type cache_name: str
        :param bank_name: name of the bank
        :type bank_name: str
        :param bank_id: id of the bank
        :type bank_id: str
        :param selected_index: index of the single image to output (use Python)
        :type selected_index: int
        :param enable_write: Description
        :type enable_write: bool
        :param images: Description
        """
        bank_path = get_bank_path(
            cache_path=get_cache_path(cache_name=cache_name),
            bank_name=bank_name,
            bank_id=bank_id
        )

        if images is not None:
            sp_images = split_images(images)

            if enable_write:
                self._logger.info(f"caching {bank_path} ...")

                os.makedirs(bank_path, exist_ok=True)

                for idx, img in enumerate(sp_images):
                    self.__get_encoder().save_image(img, f"{bank_path}/{idx}")

                if isinstance(bank_id, str):
                    bank_config = {
                        "num_frames": len(sp_images)
                    }
                elif isinstance(bank_id, dict):
                    bank_config = bank_id
                    # force num_frames if missing
                    bank_config["num_frames"] = len(sp_images)
                write_bank_metadata(
                    bank_path=bank_path,
                    data={"encoder": DEFAULT_BANK_ENCODER, "bank_config": bank_config},
                )

                # output movie using node expansion
                graph = GraphBuilder()
                graph.node("SaveWEBM", images=images, codec="vp9", fps=16.0, filename_prefix=f"{bank_path}/video", crf=32)

                PromptServer.instance.send_sync("persistence.written_bank", {
                    "bank_id": get_bank_fingerprint(bank_id=bank_id)
                })

                # perform node expansion to save the video
                return {
                    "result": (
                        images,
                        sp_images[selected_index].unsqueeze(0),
                    ),
                    "expand": graph.finalize(),
                }

            return (
                images,
                sp_images[selected_index].unsqueeze(0),
            )

        # load from cache since there are no input images
        self._logger.info(f"serving {bank_path} from cache")

        if not is_bank_valid(bank_path=bank_path):
            raise Exception(f"Unable to load the images from missing bank {bank_path}!")

        metadata = read_bank_metadata(bank_path=bank_path)
        num_frames = metadata.get("bank_config", {}).get("num_frames")  # type: ignore

        if num_frames is None:
            raise Exception(f"Unable to get num_frames from bank {bank_path} metadata!")

        cached_images = []
        for idx in range(num_frames):
            img = self.__get_encoder(
                metadata.get("encoder", DEFAULT_BANK_ENCODER)
            ).load_image(f"{bank_path}/{idx}")
            cached_images.append(img)

        return (
            torch.stack(cached_images, dim=0),
            cached_images[selected_index].unsqueeze(0),
        )
