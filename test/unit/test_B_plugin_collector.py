"""
Test the list of collected tasks
"""

from pii_extract.gather.collection import get_task_collection

from pii_extract_plg_transformers.task.task import TransformersTask

from taux.monkey_patch import patch_entry_points



# ---------------------------------------------------------------------------

def _get_tasks():
    piic = get_task_collection()
    tasklist = piic.taskdef_list()
    return list(tasklist)


def test10_tasklist(monkeypatch):
    """
    Check the task list size
    """
    patch_entry_points(monkeypatch)

    tasks = _get_tasks()
    assert len(tasks) == 1


def test20_task_obj(monkeypatch):
    """
    Check the created task
    """
    patch_entry_points(monkeypatch)

    tasks = _get_tasks()
    t = tasks[0]
    tdef = t["obj"]
    assert tdef["class"] == "piitask"
    assert tdef["task"] == TransformersTask
    assert sorted(tdef["kwargs"].keys()) == ["cfg", "log", "model_lang"]


def test30_task_pii(monkeypatch):
    """
    Check the list of used Presidio PII
    """
    patch_entry_points(monkeypatch)

    tasks = _get_tasks()
    pii = tasks[0]["piid"]
    assert len(pii) == 4

    got_transformers_ent = [(p["extra"]["map"], p["lang"]) for p in pii]
    exp_transformers_ent = [
        ("PER", "en"), ("PER", "es"),
        ("LOC", "en"), ("LOC", "es")
    ]
    assert exp_transformers_ent == got_transformers_ent
