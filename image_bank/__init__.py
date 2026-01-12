"""Image Bank implementation."""
import os
import json
import hashlib
import logging
from typing import Dict, List, Any
from pathlib import Path
from pathvalidate import sanitize_filepath


BANK_CONF_FILE = "image_banks.json"
DEFAULT_BANK_ENCODER = "pil"
METADATA_FILENAME = "metadata.json"
DEFAULT_CACHE_NAME = "default"

_logger = logging.getLogger("comfy.custom.persistence")


def _get_cache_conf(cache_name: str = DEFAULT_CACHE_NAME) -> Dict[str, str]:
    from folder_paths import user_directory, output_directory

    conf_file_path = os.path.join(user_directory, BANK_CONF_FILE)

    if not os.path.isfile(conf_file_path):
        default_conf = {
            DEFAULT_CACHE_NAME: {
                "cache_path": os.path.join(output_directory, "_persistence"),
                "encoder": DEFAULT_BANK_ENCODER
            }
        }
        with open(conf_file_path, "w") as cf:
            json.dump(default_conf, cf, indent=2)

    with open(conf_file_path, "r") as cf:
        conf = json.load(cf)

    cache_conf = conf.get(cache_name)
    if cache_conf is None:
        raise Exception(f"Cache named '{cache_name}' does not exist {conf_file_path}!")

    cache_path = cache_conf.get("cache_path")
    if cache_path is None:
        raise Exception(f"'cache_path' has not been set for Cache {cache_name} in {conf_file_path}!")

    cache_conf["encoder"] = cache_conf.get("encoder", DEFAULT_BANK_ENCODER)

    return cache_conf


def get_cache_path(cache_name: str = DEFAULT_CACHE_NAME) -> str:
    """
    Get cache path.

    :param cache_name: Name of this cache
    :type cache_name: str
    :return: Absolute path of this cache
    :rtype: str
    """
    cache_path = _get_cache_conf(cache_name=cache_name).get("cache_path")
    if not cache_path:
        raise Exception(f"Missing 'cache_path' from cache configuration '{cache_name}'")
    return cache_path


def get_cache_encoder(cache_name: str = DEFAULT_CACHE_NAME) -> str:
    """
    Get the cache encoder for this cache.

    :param cache_name: Name of this cache
    :type cache_name: str
    :return: Encoder name for this cache
    :rtype: str
    """
    encoder = _get_cache_conf(cache_name=cache_name).get("encoder")
    if not encoder:
        raise Exception(f"Missing 'encoder' from cache configuration '{cache_name}'")
    return encoder


def read_bank_metadata(bank_path: str) -> Dict[str, Any]:
    """
    Get Bank metadata.

    :param bank_path: Bank path
    :type bank_path: str
    :return: Bank metadata
    :rtype: Dict[str, str]
    """
    metadata_path = os.path.join(bank_path, METADATA_FILENAME)
    with open(metadata_path, "rb") as mi:
        metadata = json.load(mi)
    return metadata


def is_bank_valid(bank_path: str) -> bool:
    """
    Check if a bank is valid.

    :param bank_path: Bank path
    :type bank_path: str
    :return: Wether the Bank is valid
    :rtype: bool
    """
    if os.path.isdir(bank_path):
        try:
            metadata = read_bank_metadata(bank_path=bank_path)
            num_frames = metadata.get("bank_config", dict()).get("num_frames")  # type: ignore
            if num_frames is None:
                return False
            # TODO: check all files are there
            return True
        except Exception as e:
            _logger.debug(e)
    return False


def get_bank_fingerprint(bank_id) -> str:
    """
    Derive bank fingerprint from its parameters.

    :param bank_id: String value or Json encodable value
    :return: bank fingerprint
    :rtype: str
    """
    if isinstance(bank_id, str):
        return bank_id
    else:
        try:
            hashed_value = json.dumps(bank_id)
            return hashlib.sha1(hashed_value.encode("utf-8")).hexdigest()
        except Exception as e:
            raise ValueError(f"Cannot derive Bank fingerprint from this value: {bank_id} ({e})")


def get_bank_path(cache_path: str, bank_name: str, bank_id):
    """
    Get bank absolute path.

    :param cache_path: root path of the cache
    :type cache_path: str
    :param bank_name: name of the bank
    :type bank_name: str
    :param bank_id: id of the bank
    """
    fingerprint = get_bank_fingerprint(bank_id=bank_id)

    return sanitize_filepath(os.path.join(cache_path, bank_name, fingerprint), platform="auto", replacement_text="_")


def get_banks(cache_path: str) -> List[str]:
    """
    Get all banks in a cache.

    :param cache_path: Path of the cache
    :type cache_path: str
    :return: List of {bank_name}/{bank_id}
    :rtype: List[str]
    """
    output = []
    abs_cache_path = os.path.abspath(cache_path)

    for root, dirs, _ in os.walk(abs_cache_path):

        p_root = Path(root)

        if p_root.parent == Path(abs_cache_path):
            for bank_id in dirs:
                bank_path = get_bank_path(abs_cache_path, p_root.name, bank_id)
                if is_bank_valid(bank_path):
                    output.append({
                        "bank_id": bank_id,
                        "bank_name": p_root.name,
                        "metadata": read_bank_metadata(bank_path=bank_path)
                    })
    return output


def write_bank_metadata(bank_path: str, data):
    """
    Write the metadata file.

    :param bank_path: bank full path
    :type bank_path: str
    :param data: bank data, should be Json serializable
    """
    metadata_path = os.path.join(bank_path, METADATA_FILENAME)
    with open(metadata_path, "w") as mo:
        json.dump(data, fp=mo)
