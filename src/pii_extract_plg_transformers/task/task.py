"""
The Transformers-based PiiTask
"""

import logging
from operator import itemgetter
from collections import defaultdict

from pii_data.helper.exception import ProcException, ConfigException
from pii_data.types import PiiEntity, PiiEntityInfo
from pii_data.types.doc import DocumentChunk
from pii_extract.build.task import BaseMultiPiiTask
from pii_extract.helper.utils import taskd_field
from pii_extract.helper.logger import PiiLogger

from typing import Iterable, Dict, List

from .. import VERSION, defs
from .utils import hf_cachedir



def einfo(p: Dict) -> PiiEntityInfo:
    """
    Create an entity info object from a PII descriptor dict
    """
    return PiiEntityInfo(p["pii"], p.get("lang"), p.get("country"),
                         p.get("subtype"))

# ---------------------------------------------------------------------


class TransformersTask(BaseMultiPiiTask):
    """
    PII Detector wrapper over models in the HF Transformers Library
    """
    pii_source = defs.TASK_SOURCE
    pii_name = "Transformers wrapper"
    pii_version = VERSION


    def __init__(self, task: Dict, pii: List[Dict], cfg: Dict,
                 model_lang: Iterable[str], log: PiiLogger, **kwargs):
        """
          :param task: the PII task info dict
          :param pii: the list of descriptors for the PII entities to include
          :param cfg: the plugin configuration
          :param model_lang: languages to instantiate models for
          :param log: a logger object
        """
        #print("\nTransformersTask INIT", model_lang, f"PII = {pii}", f"CONFIG = {cfg}")
        # Initialize data
        self._ent_map = defaultdict(dict)
        total_lang = set()
        restrict_lang = set(model_lang) if model_lang else None
        if isinstance(pii, dict):
            pii = [pii]

        # Use the "extra" field in the PII dict to build a map (by language)
        # of model-detected entities to PIISA entities
        # (before parent constructor, which will strip away "extra" fields)
        for p in pii:
            try:
                task_lang = taskd_field(p, "lang")
                if restrict_lang:
                    task_lang = task_lang & restrict_lang
                total_lang.update(task_lang)
                emap = p["extra"]["map"]
                for lang in task_lang:
                    etype = emap if isinstance(emap, str) else emap[lang]
                    self._ent_map[lang][etype] = einfo(p)
            except KeyError as e:
                raise ConfigException("invalid config for transformers plugin: missing field '{}' in: {}", e, p)

        # Call parent constructor
        super().__init__(task=task, pii=pii)
        self._log = log

        # Decide a default language for this task (possible if we have only one)
        self.lang = next(iter(total_lang)) if len(total_lang) == 1 else None
        self._log(".. TransformersTask (%s): #pii=%d lang=%s", VERSION,
                  len(pii), self.lang)

        # Define cache directory (_before_ importing the pipeline module)
        cachedir = cfg.get("cachedir")
        if cachedir is not False:
            hf_cachedir(cachedir)

        # Set up the Transformers pipeline engine
        try:
            from .pipeline import create_pipelines, ner_labels
            self.models = create_pipelines(cfg, languages=total_lang,
                                           logger=self._log)

            # Check that all entities we want are actually supported
            for lang, model in self.models.items():
                ent = ner_labels(model)
                missing = {pname for pname in self._ent_map[lang]
                           if pname not in ent}
            if missing:
                raise ConfigException("entity for {} not found in model {}",
                                      missing, lang)

        except ConfigException:
            raise
        except KeyError as e:
            raise ConfigException("cannot create Transformers pipeline: missing key {}",
                                  e) from e
        except Exception as e:
            raise ConfigException("cannot create Transformers pipeline: {}",
                                  e) from e


    def __repr__(self) -> str:
        return f"<{TransformersTask.pii_name} #{len(self)}>"


    def __len__(self) -> int:
        return sum(len(k) for k in self._ent_map.values())


    def find(self, chunk: DocumentChunk) -> Iterable[PiiEntity]:
        """
        Perform PII detection on a document chunk
        """
        # Decide the model languag: chunk language or default
        ctx = chunk.context or {}
        lang = ctx.get("lang", self.lang)
        if lang is None:
            raise ProcException("Transformers task exception: no language defined in task or document chunk")
        elif lang not in self._ent_map:
            raise ProcException("Transformers task exception: no tasks for lang: {}",
                                lang)

        # Take the entity map for our language
        entity_map = self._ent_map[lang]
        #print("LANG", lang, "\nDATA", chunk.data, "\nMAP", entity_map)

        # Call the pipeline to get entity results
        try:
            pp = self.models[lang]
            results = pp(chunk.data)
        except Exception as e:
            raise ProcException("Transformers exception: {}: {}",
                                type(e).__name__, e) from e

        self._log("... Transformers results: %s", results if results else "NONE",
                  level=logging.DEBUG)
        #print("\n**** TRFS", lang, list(self._ent_map), chunk.data, "=>", results, sep="\n")

        # Convert results into PiEntity objects
        for r in sorted(results, key=itemgetter("start")):

            try:
                if r["entity_group"] not in entity_map:
                    continue
            except KeyError:
                raise ProcException("Invalid aggregation in Transformers model: no entity_group in result: {}", r)

            v = chunk.data[r["start"]:r["end"]]

            # Prevent whitespace around the entity
            vs = v.strip()
            if vs != v:
                r["start"] += v.index(vs)
                v = vs

            process = {"stage": "detection", "score": r["score"]}
            yield PiiEntity(entity_map[r["entity_group"]],
                            v, chunk.id, r["start"], process=process)
