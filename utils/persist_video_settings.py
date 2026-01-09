"""Video settings."""
import re
from typing import Any, Dict, Tuple


RESOLUTION_FORMAT = re.compile("""(\\d+)x(\\d+)""")

RESOLUTIONS = [
    (704, 1280),
    (480, 864),
    (320, 576),
]


def parse_preset(preset: str) -> Tuple[int, int]:
    """
    Parse a resolution preset input value.

    :param preset: input value expected in format RESOLUTION_FORMAT
    :type preset: str
    :return: video resolution W, H
    :rtype: Tuple[int, int]
    """
    p = RESOLUTION_FORMAT.match(preset)
    if p:
        return (int(p.group(1)), int(p.group(2)))

    raise Exception(f"Incorrect preset input: {preset}!")


class PersistVideoSettings:
    """PersistVideoSettings node implementation."""

    @classmethod
    def INPUT_TYPES(cls) -> Dict[str, Any]:
        """Provide ComfyUI with node inputs."""
        all_resolutions = RESOLUTIONS + [(h, w) for w, h in RESOLUTIONS]

        r = [
            f"{w}x{h} ({round(max(w, h) / min(w, h), 2)}, {w * h})"
            for w, h in all_resolutions
        ]

        return {
            "required": {
                "resolution": (r,),
                "custom_resolution": ("STRING", {"mutiline": False, "default": ""}),
                "project_name": ("STRING", {"mutiline": False, "default": "my_project"}),
                "save": ("BOOLEAN", {"default": True})
            }
        }

    RETURN_TYPES = (
        "STRING",
        "BOOLEAN",
        "INT",
        "INT"
    )
    RETURN_NAMES = (
        "cleaned_project_name",
        "save",
        "width",
        "height"
    )
    FUNCTION = "process"
    CATEGORY = "Persistence"

    def process(
        self,
        resolution: str,
        custom_resolution: str,
        project_name: str,
        save: bool
    ):
        """Execute the node."""
        if custom_resolution:
            width, height = parse_preset(custom_resolution)
        else:
            width, height = parse_preset(resolution)

        cleaned_project_name = re.sub(r'[^A-Za-z0-9_]', '_', project_name.split(".")[0])

        return (cleaned_project_name, save, width, height,)
