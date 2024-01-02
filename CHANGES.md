# ChangeLog

## v. 0.1.3
 * new config field to set the seed for random numbers

## v. 0.1.2
 * allow the "cachedir" config field to be set as `False`, which prevents
   setting the HF cache directory whatsoever
 * default config uses a multilingual NER model (configured for en, es, fr)
 * save a tuple (tokenizer, model) in the cache for reuse, not the full pipeline

## v. 0.1.1
 * fix: package description blurb

## v. 0.1.0
 * initial version
