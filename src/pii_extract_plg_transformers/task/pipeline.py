"""
Load models from the Transformers library, using pipelines
"""

try:
    import torch
    from transformers import (
        AutoTokenizer,
        AutoModelForTokenClassification,
        pipeline
    )
except ImportError:
    torch = None
    AutoTokenizer = None
    AutoModelForTokenClassification = None
    pipeline = object

from pii_data.helper.exception import ProcException
from pii_extract.helper.logger import PiiLogger

from typing import Dict, Iterable, List

from .. import defs
from .utils import package_languages


# Cache for engine reuse
ENGINE_CACHE = {}


class MissingDependency(ProcException):
    pass


def ner_labels(pl: pipeline) -> List[str]:
    """
    Return the labels the model will produce
    """
    lbl = pl.model.config.label2id
    if not lbl:
        return []
    lbl = set(t.split('-')[-1] for t in lbl)
    lbl.discard("O")
    return lbl



def create_pipelines(config: Dict, languages: Iterable[str] = None,
                     logger: PiiLogger = None) -> Dict[str, pipeline]:
    """
    Create Transfomers pipelines for entity detection
     :param config: the engine config (a section of the overall plugin config)
     :param languages: restrict languages in the analyzer
     :param logger: a logger instance
    Will reuse an object with the same configuration if it's in the cache
    and `reuse_engine` in the config is True (which is its default value)
    """
    if pipeline is None:
        raise MissingDependency("transformers package not found")
    if torch is None:
        raise MissingDependency("PyTorch package not found")

    # Decide the languages we'll load
    langset = package_languages(config)
    #print("PIPELINE", langset, "&", languages, config)
    if languages:
        langset = langset.intersection(languages)

    # Keep only the language models we'll use
    model_list = [m for m in config.get(defs.CFG_TASK_MODELS)
                  if not langset or m["lang_code"] in langset]
    if logger:
        logger(".. Transformers models: %s",
               ','.join(m['lang_code'] for m in model_list))

    # Create pipelines, according to the configuration
    reuse = config.get(defs.CFG_TASK_REUSE, True)
    default_agg = config.get("aggregation", "max")
    pdict = {}
    if logger:
        logger("... Instantiating Transformer models")

    for m in model_list:
        lang = m['lang_code']
        if logger:
            logger("... model: %s", lang)

        mdname = m["model"]
        tkname = m.get("tokenizer") or m["model"]
        par = m.get("model_params", {})
        agg = m.get("aggregation", default_agg)

        # Look for it in cache
        if reuse:
            # Build the cache key
            key = f"{tkname}/{mdname}"
            if par:
                key += '/' + '-'.join(f"{k}={par[k]}" for k in sorted(par))

            # Try to find it in cache
            model = ENGINE_CACHE.get(key)
            if model:
                pdict[lang] = pipeline("ner", tokenizer=model[0], model=model[1],
                                       aggregation_strategy=agg)
                if logger:
                    logger(".... Reusing Transformers pipeline for %s: %s", lang, mdname)
                continue

        # Create objects & build the pipeline
        tokenizer = AutoTokenizer.from_pretrained(tkname)
        model = AutoModelForTokenClassification.from_pretrained(mdname, **par)
        pdict[lang] = pipeline("ner", tokenizer=tokenizer, model=model,
                               aggregation_strategy=agg)

        # Save to cache
        if reuse:
            ENGINE_CACHE[key] = tokenizer, model

    return pdict
