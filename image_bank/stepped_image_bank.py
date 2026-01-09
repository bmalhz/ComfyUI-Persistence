"""Serie step module."""
import torch
import logging
from server import PromptServer
from typing import Any, Dict, List, Optional, Tuple, override

from . import get_banks, get_cache_path, DEFAULT_CACHE_NAME
from .image_bank import PersistImageBank


_BANK_NAME_PLACEHOLDER = "<COPY-PREVIOUS-STEP>"


class PersistSteppedImageBank(PersistImageBank):
    """PersistSteppedImageBank node."""

    _logger = logging.getLogger("comfy.custom.persistence.PersistSteppedImageBank")

    @staticmethod
    def _get_bank_settings(bank_name: Optional[str], bank_id: Optional[Any], previous_series: Optional[List[Dict]]) -> Tuple[str, str]:
        if (not bank_name or bank_name == _BANK_NAME_PLACEHOLDER) and previous_series:
            bank_name = previous_series[-1].get("bank_name")  # type: ignore

        if not bank_name:
            raise Exception("bank_name must be provided!")

        if bank_id:
            return bank_name, bank_id
        if previous_series:
            return bank_name, f"step{len(previous_series) + 1}"
        return bank_name, "step1"

    @classmethod
    def INPUT_TYPES(cls) -> Dict[str, Any]:
        """INPUT_TYPES definition."""
        from comfy.comfy_types.node_typing import IO

        full_banks = get_banks(cache_path=get_cache_path())

        PromptServer.instance.send_sync("persistence.bank_list", {
            "banks": full_banks
        })

        banks = [b.get("bank_name") + "/" + b.get("bank_id") for b in full_banks]  # pyright: ignore[reportAttributeAccessIssue]

        banks.sort()
        banks.insert(0, "NONE")

        cache_names = [DEFAULT_CACHE_NAME]

        return {
            "required": {
                "cache_name": (cache_names,),
                "bank_name": ("STRING", {"default": _BANK_NAME_PLACEHOLDER}),
                "enable_write": ("BOOLEAN", {"default": True}),
                "forced_bank": (banks,)
            },
            "optional": {
                "bank_id": (IO.ANY,),
                "images": ("IMAGE", {"lazy": True}),
                "previous_series": ("VIDEO_SERIES",),
            },
        }

    RETURN_TYPES = (
        "IMAGE",
        "IMAGE",
        "IMAGE",
        "VIDEO_SERIES"
    )
    RETURN_NAMES = (
        "step_images",
        "step_last_image",
        "all_images",
        "series"
    )
    FUNCTION = "process_step"

    @override
    def check_lazy_status(
        self,
        **kwargs
    ):
        """
        Check if input images are required.

        :param self: self
        :param cache_name: Name of the Cache to use
        :param bank_name: Name of this bank
        :param bank_id: Bank id or configuration parameters
        :param previous_series: Previous steps if any
        """
        forced_bank = kwargs.get("forced_bank", "NONE")

        if forced_bank != "NONE":
            bank_name, bank_id = forced_bank.split("/")
        else:
            bank_name, bank_id = self._get_bank_settings(kwargs.get("bank_name"), kwargs.get("bank_id"), kwargs.get("previous_series"))

        return PersistImageBank.check_lazy_status(
            self,
            **{
                "cache_name": kwargs.get("cache_name", DEFAULT_CACHE_NAME),
                "bank_name": bank_name,
                "bank_id": bank_id,
            }
        )

    def process_step(
        self,
        cache_name: str,
        bank_name: str,
        enable_write: bool,
        forced_bank: str,
        bank_id=None,
        images: Optional[torch.Tensor] = None,
        previous_series: Optional[List[Dict]] = None
    ):
        """
        Run the node.

        :param self:
        :param cache_name: name of the cache to use
        :type cache_name: str
        :param bank_name: name of the bank to use
        :type bank_name: str
        :param bank_id: id of this bank, can be a string of any Json encodable dict
        :param enable_write: enable writing
        :type enable_write: bool
        :param forced_bank: id of the bank to force if any
        :type forced_bank: str
        :param images: input images if any
        :type images: Optional[torch.Tensor]
        :param previous_series: previous series if any
        :type previous_series: Optional[List[Dict]]
        """
        if forced_bank != "NONE":
            # force bank
            bank_name, bank_id = forced_bank.split("/")
        else:
            bank_name, bank_id = self._get_bank_settings(bank_name, bank_id, previous_series)

        pstBankOutput = PersistImageBank.process(
            self=self,
            cache_name=cache_name,
            bank_name=bank_name,
            bank_id=bank_id,
            selected_index=-1,
            enable_write=enable_write,
            images=images
        )
        if isinstance(pstBankOutput, dict):
            current_images, current_last_image = pstBankOutput.get("result")
            graph = pstBankOutput.get("expand")
        else:
            current_images, current_last_image = pstBankOutput
            graph = None

        current_serie = {"images": current_images, "bank_name": bank_name}

        if previous_series:
            # extract images from previous series
            previous_images = list(map(lambda s: s.get("images"), previous_series))

            if None in previous_images:
                raise Exception("Not all previous series have images!")

            all_images = previous_images + [current_images]

            return {
                "result": (
                    current_images,
                    current_last_image,
                    torch.cat(all_images, dim=0),
                    previous_series + [current_serie]
                ),
                "expand": graph,
            }

        else:
            # first or single step
            return {
                "result": (
                    current_images,
                    current_last_image,
                    current_images,
                    [current_serie]
                ),
                "expand": graph
            }
