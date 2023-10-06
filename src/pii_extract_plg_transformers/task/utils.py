"""
Some configuration utilities
"""

import sys
from os import environ
from pathlib import Path
from importlib.metadata import version

from typing import Dict, Set

from pii_data.helper.exception import ConfigException, FileException


ENV_HF_CACHE = "HUGGINGFACE_HUB_CACHE"


def hf_cachedir(cachedir: str = None):
    """
    Find the place where to keep the HuggingFace cache
    Create the directory if it does not exist
    Note: the cachedir needs to be set _before_ importing the Transformers module
    """
    # Define HF cache directory
    if not cachedir:
        cachedir = environ.get(ENV_HF_CACHE)
    if cachedir:
        cachedir = Path(cachedir)
    else:
        cachedir = Path(sys.prefix) / "var" / "piisa" / "hf-cache"
    # Create directory if neded
    try:
        if not cachedir.is_dir():
            cachedir.mkdir(parents=True)
    except Exception as e:
        raise FileException("cannot create HF cachedir '{}': {}", cachedir, e) from e
    # Push it to the environment
    environ[ENV_HF_CACHE] = str(cachedir)
    #print("CACHEDIR", str(cachedir))


def package_languages(config: Dict) -> Set[str]:
    """
    Return the set of languages defined in the configuration for the package
    """
    try:
        langlist = [m["lang_code"] for m in config.get("models", [])]
    except KeyError:
        raise ConfigException("missing 'lang_code' in Transformers plugin model config")
    return set(langlist)


def transformers_version() -> str:
    """
    Return the version of the available Transformers package
    """
    try:
        return version("transformers")
    except Exception as e:
        raise ConfigException("cannot fetch transformers library version: {}",
                              e) from e
