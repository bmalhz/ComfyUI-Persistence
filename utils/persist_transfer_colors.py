"""VPersistTransferColors."""
from typing import Dict, Any
from itertools import accumulate

from torch import Tensor
from comfy_execution.graph_utils import GraphBuilder

from ..image.image_utils import split_images


class PersistTransferColors:
    """PersistTransferColors node implementation."""

    @classmethod
    def INPUT_TYPES(cls) -> Dict[str, Any]:
        """Provide ComfyUI with node inputs."""

        return {
            "required": {
                "images": ("IMAGE", ),
                "match_strength": ("FLOAT", {"default": 0.9})
            }
        }

    RETURN_TYPES = (
        "IMAGE",
    )
    RETURN_NAMES = (
        "images",
    )
    FUNCTION = "process"
    CATEGORY = "Persistence"

    def process(
        self,
        images: Tensor,
        match_strength: float
    ):
        """Execute the node."""
        graph = GraphBuilder()
        # split images and add dim 0
        images_seq = [img.unsqueeze(0) for img in split_images(images)]

        def match_color(prev, img):
            return (
                # match colors using ColorMatch from KJ
                graph.node(
                    "ColorMatch",
                    image_ref=prev,
                    image_target=img,
                    method="hm-mvgd-hm",
                    strength=match_strength,
                    multithread=True,
                ).out(0)
                if prev is not None
                else img
            )

        # match all images with previous one
        matched_images = list(accumulate(images_seq, match_color))
        # prepare dict for Expansion call
        arg_imgs = {f"image_{i}": img for i, img in enumerate(matched_images, 1)}

        return {
            # batch all images using ImageBatchMulti from KJ
            "result": (graph.node("ImageBatchMulti", inputcount=len(arg_imgs),  **arg_imgs).out(0),),
            "expand": graph.finalize()
        }
