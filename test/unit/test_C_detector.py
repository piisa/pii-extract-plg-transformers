"""
Test building the Transformers task
"""

import pytest

from pii_data.helper.exception import ConfigException
from pii_extract.gather.collection import get_task_collection

from taux.monkey_patch import patch_entry_points, patch_transformer_pipeline, patch_env

# ---------------------------------------------------------------------------


def test10_tasklist(monkeypatch):
    """
    Check the built task, for all languages
    """
    patch_entry_points(monkeypatch)
    patch_transformer_pipeline(monkeypatch, {}, model_labels=["PER", "LOC"])
    patch_env(monkeypatch)

    piic = get_task_collection(debug=False)
    tasks = piic.build_tasks()
    tasks = list(tasks)
    assert len(tasks) == 1
    assert str(tasks[0]) == "<Transformers wrapper #4>"


def test11_tasklist_err(monkeypatch):
    """
    Build the task, but with transformers not providing the requested labels
    """
    patch_entry_points(monkeypatch)
    patch_transformer_pipeline(monkeypatch, {})
    patch_env(monkeypatch)

    piic = get_task_collection(debug=False)
    tasks = piic.build_tasks()
    with pytest.raises(ConfigException):
        tasks = list(tasks)


def test20_tasklist_lang(monkeypatch):
    """
    Check the built task, specific language
    """
    patch_entry_points(monkeypatch)
    patch_transformer_pipeline(monkeypatch, {}, model_labels=["PER", "LOC"])
    patch_env(monkeypatch)

    piic = get_task_collection(debug=False)
    tasks = piic.build_tasks('en')
    tasks = list(tasks)
    assert len(tasks) == 1
    assert str(tasks[0]) == "<Transformers wrapper #2>"


def test30_engine_cache(monkeypatch):
    """
    Check engine object reuse
    """
    patch_entry_points(monkeypatch)
    patch_env(monkeypatch)

    mck = patch_transformer_pipeline(monkeypatch, {}, model_labels=["PER", "LOC"])

    piic = get_task_collection(debug=True)

    # Build once
    tasks = piic.build_tasks("en")
    tasks = list(tasks)

    # Check the pipeline constructor was called
    assert mck.call_count == 1

    # Build second time
    tasks = piic.build_tasks("en")

    # Check the pipeline constructor was not called -- pipeline is reused
    assert mck.call_count == 1

    # Build again, this time for ES
    tasks = piic.build_tasks("es")
    tasks = list(tasks)

    # Check this time there *was* a second pipeline call
    assert mck.call_count == 2
