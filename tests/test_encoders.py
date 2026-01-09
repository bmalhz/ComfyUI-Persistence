import pytest
import torch
import os
import numpy as np
import zstandard as zstd

from typing import Dict
from pathlib import Path
from PIL import Image
from safetensors.torch import save_file
from encoders.image_encoder import ImageEncoder
from encoders.pil_image_encoder import PilImageEncoder
from encoders.safetensor_image_encoder import SafetensorsImageEncoder


@pytest.mark.unit
class TestPilEncoder:
    """Tests PilImageEncoder."""

    @pytest.fixture
    def sample_image_path(self, tmp_path) -> Dict[str, str]:
        output = dict()
        # webp format
        pil_img_path = tmp_path / "img.webp"
        img = Image.new("RGB", (100, 100), color=(255, 0, 0))
        img.save(pil_img_path, format="WEBP")
        output[PilImageEncoder.file_extension()] = str(tmp_path / "img")  # path without extension

        # safetensor.zst format
        np_image = np.array(img).astype(np.float32) / 255.0
        tensor_img = torch.from_numpy(np_image.copy())[None,].squeeze(0)

        zstd_sf_img_path = tmp_path / f"img{SafetensorsImageEncoder.file_extension()}"
        tmp_fname = str(tmp_path / "img.tensor")
        save_file(
            {"img": tensor_img.clone().contiguous()}, filename=tmp_fname
        )

        z_comp = zstd.ZstdCompressor(level=4)
        with open(tmp_fname, "rb") as ifh, open(
            str(zstd_sf_img_path), "wb"
        ) as ofh:
            z_comp.copy_stream(ifh, ofh)

        output[SafetensorsImageEncoder.file_extension()] = str(tmp_path / "img")

        return output

    @pytest.fixture
    def tensor_image(self) -> torch.Tensor:
        img = Image.new("RGB", (100, 100), color=(255, 0, 0))
        image = np.array(img).astype(np.float32) / 255.0  # HWC

        return torch.from_numpy(image.copy())[None,].squeeze(0)  # removes batch dim

    @pytest.fixture(params=[PilImageEncoder, SafetensorsImageEncoder], ids=lambda c: c.__name__)
    def encoder(self, request):
        return request.param()

    def test_load_image(self, encoder: ImageEncoder, sample_image_path):
        img_path = sample_image_path.get(encoder.file_extension())
        assert img_path is not None
        tImage = encoder.load_image(img_path)
        assert tImage.size() == torch.Size([100, 100, 3])

    def test_save_image(self, encoder: ImageEncoder, tensor_image: torch.Tensor, tmp_path: Path):
        save_path = str(tmp_path / "output")
        encoder.save_image(image=tensor_image, save_path=save_path)

        assert os.path.isfile(f"{save_path}{encoder.file_extension()}")
