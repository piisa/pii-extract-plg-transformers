# Pii Extractor plugin: Transformers

[![version](https://img.shields.io/pypi/v/pii-extract-plg-transformers)](https://pypi.org/project/pii-extract-plg-transformers)
[![changelog](https://img.shields.io/badge/change-log-blue)](CHANGES.md)
[![license](https://img.shields.io/pypi/l/pii-extract-plg-transformers)](LICENSE)
[![build status](https://github.com/piisa/pii-extract-plg-transformers/actions/workflows/pii-extract-plg-transformers-pr.yml/badge.svg)](https://github.com/piisa/pii-extract-plg-transformers/actions)

This repository builds a Python package that installs a [pii-extract-base]
plugin to perform PII detection for text data using the Hugging Face
[Transformers] Python library. It will download and use trained token
classification models running on that library.

The name of the plugin entry point is `piisa-detectors-transformers`


## Requirements

The package needs
 * at least Python 3.8
 * the [pii-data] and the [pii-extract-base] base packages
 * the [Transformers] package
 * PyTorch, either GPU or CPU
 * an NLP engine model for the desired language (will be downloaded on demand,
   based on the configuration)


## Installation

 * Install the package: `pip install pii-extract-plg-transformers` (it will
   automatically install its dependencies, *except* Pytorch)
 * [Install PyTorch]: either the CPU PyTorch package or the GPU package
   appropriate for your GPU
 * If necessary, define the cache directory for models (see
   [below](#cache-directory))
    

### Cache directory

The transformers library downloads models on the fly from the HuggingFace
Hub. It keeps them in a cache in a local folder, to avoid repeated downloads.

The `pii-extract-plg-transformers` package defines this local folder as
follows:

1. If the `HUGGINGFACE_HUB_CACHE` environment variable is defined, it is
   used
2. Else, if the configuration file for the package contains a `cachedir` field
   inside the `task_config` section, it will be used
3. If that field contains a `false` value, then **no** specific cache directory
   will be defined (so the HuggingFace internal default will be used)
4. Else, a default is chosen: the `var/piisa/hf-cache` subfolder in
   the virtualenv that holds the package


## Usage

The package does not have any user-facing entry points (except for two auxiliary
console scripts, see [below](#auxiliary-scripts)). Instead, upon installation it
defines a plugin entry point. This plugin is automatically picked up by the
scripts and classes in [pii-extract-base], and thus its functionality is exposed
to them.

The task created by the plugin is a standard [PII task] object, using the
`pii_extract.build.task.MultiPiiTask` class definition. It will be called,
as all PII task objects, with a `DocumentChunk` object containing the data to
analyze. The chunk **must** contain language specification in its metadata, so
that the plugin knows which language to use (unless the plugin task has been
built with *only one* language; in that case if the chunk does not contain
a language specification, it will use that single language).


## Configuration

Runtime behaviour is governed by a [PIISA configuration file], which sets up which
models from the HuggingFace Hub will be downloaded and used (note that the
configuration defines the total set of languages available for detection, but
it is also possible to initialize the plugin with a _subset_ of the configuration
languages).

The [default configuration file] defines detection for `Person` and `Location`
PII instances for English, Spanish and French, using the [WikiNEuRal] multilingual
NER model available in the Hugging Face Hub.

However, a configuration file can
also define a different model per language, and a different set of PII to detect
for each model (and also different aggregation strategies to merge the model
output). There is [another example available].


## Auxiliary scripts

### Information

`pii-extract-transformers-info` is a command-line script which provides
information about the plugin capabilities: 
  * `version`: installed package versions
  * `models`: list of configured Transdormers models
  * `model-entities`: the total list of entities each configured model can
	 generate
  * `pii-entities`: the PIISA tasks that this plugin will create, by translating
	from the entities detected by the models (this depends on the PIISA config
	used)


### Testing

`pii-extract-transformers-detect` is a command-line script to do initial
testing: it performs PII detection by processing a text chunk through one of the
models defined in the plugin configuration.

Note that this script instantiates the plugin task directly, i.e. it does *not*
go through the standard PIISA software stack (which would execute the task via
plugin loading into the pii-extract framework). For the same reason, it *only*
executes this detection task, ignoring any other pii-extract plugins that
might be available.


## Building

The provided [Makefile] can be used to process the package:
 * `make pkg` will build the Python package, creating a file that can be
   installed with `pip`
 * `make unit` will launch all unit tests (using [pytest], so pytest must be
   available)
 * `make install` will install the package in a Python virtualenv. The
   virtualenv will be chosen as, in this order:
     - the one defined in the `VENV` environment variable, if it is defined
     - if there is a virtualenv activated in the shell, it will be used
     - otherwise, a default is chosen as `/opt/venv/pii` (it will be
       created if it does not exist)


[Transformers]: https://huggingface.co/docs/transformers/main/en/index
[Install PyTorch]: https://pytorch.org/get-started/locally/
[will be cached]: https://huggingface.co/docs/huggingface_hub/guides/manage-cache

[pii-data]: https://github.com/piisa/pii-data
[pii-extract-base]: https://github.com/piisa/pii-extract-base
[pii task descriptors]: https://github.com/piisa/pii-extract-base/tree/main/doc/task-descriptor.md
[Makefile]: Makefile
[pytest]: https://docs.pytest.org
[default configuration file]: src/pii_extract_plg_transformers/resources/plugin-config.json
[PIISA configuration file]: doc/configuration.md
[another example available]: doc/examples.md
[PII task]: https://github.com/piisa/pii-extract-base/blob/main/doc/task-implementation.md
[WikiNEuRal]: https://huggingface.co/Babelscape/wikineural-multilingual-ner
