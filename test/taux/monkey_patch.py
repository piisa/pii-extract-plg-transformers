"""
Some utils to monkey patch objects in the plugin
"""

from os import environ

from unittest.mock import Mock

from typing import List, Dict

from pii_extract.gather.collection.sources.defs import PII_EXTRACT_PLUGIN_ID
from pii_extract_plg_transformers.plugin_loader import PiiExtractPluginLoader
from pii_extract_plg_transformers.task.utils import ENV_HF_CACHE

import pii_extract.gather.collection.sources.plugin as mod1
import pii_extract_plg_transformers.task.pipeline as mod_pl


# ---------------------------------------------------------------------


def patch_entry_points(monkeypatch):
    """
    Monkey-patch the importlib.metadata.entry_points call to return only our
    plugin entry point
    """
    mock_entry = Mock()
    mock_entry.name = "piisa-detectors-presidio [unit-test]"
    mock_entry.load = Mock(return_value=PiiExtractPluginLoader)

    mock_ep = Mock(return_value={PII_EXTRACT_PLUGIN_ID: [mock_entry]})

    monkeypatch.setattr(mod1, 'entry_points', mock_ep)


# ---------------------------------------------------------------------


def patch_transformer_pipeline(monkeypatch, results: Dict,
                               model_labels: List[str] = None) -> Mock:
    """
    Monkey patch the Transformers API we use
    """
    # Ensure the torch object is not None
    monkeypatch.setattr(mod_pl, 'torch', True)

    # Patch Transformers entry points
    mock_class = Mock()
    monkeypatch.setattr(mod_pl, 'AutoTokenizer', mock_class)
    mock_class = Mock()
    monkeypatch.setattr(mod_pl, 'AutoModelForTokenClassification', mock_class)

    # Patch pipeline
    pipeline = Mock(return_value=results)
    pipeline.model.config.label2id = model_labels or []
    pipeline_creator = Mock(return_value=pipeline)
    monkeypatch.setattr(mod_pl, 'pipeline', pipeline_creator)

    # Reset cache
    monkeypatch.setattr(mod_pl, 'ENGINE_CACHE', {})

    return pipeline_creator


def patch_env(monkeypatch):
    """
    Monkey patch the environment variables
    """
    m = environ.get(ENV_HF_CACHE)
    if m:
        monkeypatch.delenv(ENV_HF_CACHE)
