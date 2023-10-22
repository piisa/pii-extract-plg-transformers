"""
Test building the task and using it for detection
"""

import pytest

from pii_data.helper.exception import ProcException
from pii_extract.gather.collection import get_task_collection

from taux.monkey_patch import patch_entry_points, patch_transformer_pipeline, patch_env
from taux.taskproc import process_tasks



TESTCASES = [
    (
        # source document
        "Alan Turing. considered the father of AI, was born in England",

        # mock the result delivered by Presidio
        [{"start": 54, "end": 61, "entity_group": "LOC", "score": 0.85},
         {"start": 0, "end": 11, "entity_group": "PER", "score": 0.85}],

        # expected processed document
        "<PERSON:Alan Turing>. considered the father of AI, was born in <LOCATION:England>",

        # expected PII collection
        [{"type": "PERSON", "lang": "en", "chunkid": "1",
          "process": {"stage": "detection", "score": 0.85},
          "value": "Alan Turing", "start": 0, "end": 11},
         {"type": "LOCATION", "lang": "en", "chunkid": "1",
          "process": {"stage": "detection", "score": 0.85},
          "value": "England", "start": 54, "end": 61}]
    )
]



# ---------------------------------------------------------------------------


def test20_detect(monkeypatch):
    """
    Check detection
    """
    # Patch the plugin entry point so that only this plugin is detected
    patch_entry_points(monkeypatch)
    # Patch the pipeline creation function so that we use a mock
    results = TESTCASES[0][1]
    patch_transformer_pipeline(monkeypatch, results, ["LOC", "PER"])
    # Patch environment
    patch_env(monkeypatch)

    # Gather tasks and build them
    piic = get_task_collection()
    tasks = piic.build_tasks("en")
    tasks = list(tasks)

    for src_doc, _, exp_doc, exp_pii in TESTCASES:
        got_pii, got_doc = process_tasks(tasks, src_doc, lang="en")
        assert exp_doc == got_doc

        got_pii = list(got_pii)
        assert len(got_pii) == 2

        for e, g in zip(exp_pii, got_pii):
            #print("\nGOT", g.asdict())
            assert e == g.asdict()


def test21_detect_default_lang(monkeypatch):
    """
    Check detection, with a default language
    """
    # Patch the plugin entry point so that only this plugin is detected
    patch_entry_points(monkeypatch)
    # Patch the pipeline creation function so that we use a mock
    results = TESTCASES[0][1]
    patch_transformer_pipeline(monkeypatch, results, ["LOC", "PER"])
    # Patch environment
    patch_env(monkeypatch)

    # Gather tasks and build them
    piic = get_task_collection()
    tasks = piic.build_tasks("en")
    tasks = list(tasks)

    for src_doc, _, exp_doc, exp_pii in TESTCASES:
        # No language sent in the chunks -- the task should use the default
        got_pii, got_doc = process_tasks(tasks, src_doc)
        assert exp_doc == got_doc

        got_pii = list(got_pii)
        assert len(got_pii) == 2

        for e, g in zip(exp_pii, got_pii):
            #print("\nGOT", g.asdict())
            assert e == g.asdict()


def test30_error_lang(monkeypatch):
    """
    Check error generation due to language not specified
    """
    # Patch the plugin entry point so that only this plugin is detected
    patch_entry_points(monkeypatch)
    # Patch the pipeline creation function so that we use a mock
    results = TESTCASES[0][1]
    patch_transformer_pipeline(monkeypatch, results, ["LOC", "PER"])
    # Patch environment
    patch_env(monkeypatch)

    # Gather tasks and build them. Use two languages, to preclude definition
    # of a default language in the task
    piic = get_task_collection()
    tasks = piic.build_tasks(["en", "es"])
    tasks = list(tasks)

    # Process a chunk with no language info, and there's no default in the task
    with pytest.raises(ProcException) as e:
        _ = process_tasks(tasks, TESTCASES[0][0])
    assert str(e.value) == "Transformers task exception: no language defined in task or document chunk"
