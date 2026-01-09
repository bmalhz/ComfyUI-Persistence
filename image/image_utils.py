"""Image utils."""

import torch
from typing import List


def split_images(images: torch.Tensor, permute_layout: bool = False) -> List[torch.Tensor]:
    """
    Split a batch of images into a list of single images.

    :param images: Batch of images
    :type x: torch.Tensor
    :param permute_layout: Description
    :type permute_layout: bool
    :return: Description
    :rtype: List[Tensor]
    """
    if images.dim() == 3:
        # Already a single image
        return [images]

    if images.dim() != 4:
        raise ValueError(f"Expected 3D or 4D tensor, got shape {tuple(images.shape)}")

    if permute_layout:
        # convert NHWC -> NCHW
        images = images.permute(0, 3, 1, 2).contiguous()

    return [img for img in images.unbind(dim=0)]
