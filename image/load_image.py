"""PersistLoadImage module."""
import os
from typing import Generator
from nodes import LoadImage
from folder_paths import get_input_directory, filter_files_content_types


class PersistLoadImage(LoadImage):
    """PersistLoadImage with output path."""

    @classmethod
    def INPUT_TYPES(s):
        """Comfyui input types."""
        input_dir = get_input_directory()

        def get_files() -> Generator[str, None, None]:
            for root, _, files in os.walk(input_dir):
                for f in files:
                    p = os.path.join(root, f)
                    if os.path.isfile(p):
                        yield p[len(os.path.commonprefix((input_dir, p))) + 1:]

        files = filter_files_content_types(list(get_files()), ["image"])

        return {
            "required": {
                "image": (sorted(files), {"image_upload": True})
            },
        }

    RETURN_TYPES = ("IMAGE", "MASK", "STRING")
    RETURN_NAMES = (
        "image",
        "mask",
        "image_path"
    )

    FUNCTION = "_pst_load_image"

    def _pst_load_image(self, image):
        output_image, output_mask = super().load_image(image=image)

        # append image_path
        return (output_image, output_mask, image)
