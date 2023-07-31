"""
A collector for the Transformers detection task
"""

from pii_extract.helper.utils import taskd_field
from pii_extract.helper.logger import PiiLogger

from typing import Iterable, Dict, Union, Set

from .. import VERSION, defs
from .utils import package_languages
from .task import TransformersTask


# ---------------------------------------------------------------------


def _pii_list(config: Dict, langset: Set[str]) -> Dict:
    """
    Compute the list of PII Entities that will be detected
      :param config: PIISA config containing the defined list of PII
      :param lang: restrict the result to this set of languages
    """
    piimap = {}
    for p in config[defs.CFG_MAP]:

        key = f"{p['type']}/{p.get('subtype')}"
        lang = p.get("lang")

        if lang is None:
            piimap.pop(key, None)
            continue    # remove entries whose language is defined as None
        elif langset and not taskd_field(p, "lang") & langset:
            continue    # skip if we've been given a precise set of languages

        piimap[key] = p

    return list(piimap.values())


# ---------------------------------------------------------------------

class TaskCollector:
    """
    The class used by the plugin loader to produce the PII task
    """

    def __init__(self, cfg: Dict, languages: Iterable[str] = None,
                 debug: bool = True):
        """
          :param cfg: the task configuration
          :param languages: restrict the collected plugin task to a subset of
            languages, from among the ones available in the config
          :param debug: activate debug logging
        """
        self.cfg = cfg
        self.model_lang = package_languages(self.cfg[defs.CFG_TASK])
        if languages is not None:
            self.model_lang = self.model_lang.intersection(languages)
        self._log = PiiLogger(__name__, debug)
        self._log(".. Transformer task collector: init (lang=%s)",
                  self.model_lang)


    def gather_tasks(self, lang: Union[str, Iterable[str]] = None) -> Iterable[Dict]:
        """
        Return the iterable of available PII Descriptors for all tasks
        (in this case it is a single multi-task)
          :param lang: restrict the languages for the PII instances to a subset
        """
        task_lang = self.model_lang
        if lang:
            task_lang = task_lang.intersection([lang] if isinstance(lang, str) else lang)
        self._log(".. transformers-plugin gather tasks for lang=%s", task_lang)

        # Prepare the raw task descriptor
        task = {
            "class": "PiiTask",
            "source": defs.TASK_SOURCE,
            "version": VERSION,
            "doc": defs.TASK_DESCRIPTION,
            "pii": _pii_list(self.cfg, task_lang),
            "task": TransformersTask,
            "kwargs": {"cfg": self.cfg[defs.CFG_TASK],
                       "model_lang": task_lang, "log": self._log}
        }
        yield task
