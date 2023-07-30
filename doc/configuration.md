# Plugin configuration

The plugin is governed by a [PIISA configuration file]; there is one [default
file] included in the package resources. The format tag for the configuration
is `"piisa:config:extract-plg-transformers:main:v1`, and it has two
top-level elements:
 * `task_config` defines the models to use
 * `pii_list` defines the PII instances to be detected. 


## Engine configuration

The `task_config` element can contain the following fields:
 - `models`: a list of NLP models to be loaded
 - `aggregation`: default [aggregation strategy] technique, to be applied if no
   specific one is defined in a model
 - `reuse_engine`: cache the model pipelines built, and reuse them if another
   task object includes them in its configuration (default is `True`)
 - `cachedir`: define the [cache directory] where to store downloaded models.

The languages to be supported in a specific plugin instance will be the ones
that have an entry in the `models` list. See [below](#choosing-a-model) on
what models can be added.

Each model in the `models` list is a dictionary with the following elements:
 * `lang_code`: the language code for this model
 * `model`: the name of the model in the Hugging Face Hub (or the model
   filename, if it is to be loaded locally).
 * `tokenizer`: the name of the tokenizer to use (if different from the model
   name)
 * `aggregation`: the [aggregation strategy] to use to process the output of
   this model (if different from the default one)
 * `model_params`: an optional dictionary of parameters to pass to the model
   constructor


### Choosing a model

The [default configuration] defines models for English and Spanish, to detect
instances of PERSON and LOCATION. More models can be added as needed by adding
them to the configuration.

The model configured in an entry under the `models` list must be a Hugging
Face model suitable for a [token classification] pipeline. It can either be:
  * a local path (referring to a locally available model)
  * the name of the model in the Hub: look for NER [token classification models
    in the Hugging Face Hub]. The model will then be downloaded on first use,
    and stored in the [cache directory].

In order for the model to be directly usable, it needs to be in Hugging Face
Transformers format (not all models in the Hub are). If it is in another
format, it will generate an error such as

	  <model> does not appear to have a file named config.json.

You can check on the model page in the Hub if the `config.json` file is there;
if not that model needs to be downloaded and converted before it can be used.

Note also that some of the models in the Hub will require additional Python
packages. If those packages are not installed in the virtualenv, an exception
will be triggered when trying to use the model. Typically the exception message
will tell what is missing.

As an additional example, there is an [extended configuration] that adds 3
other languages to the model list, it can be tested with [some examples].


## PII List

The `pii_list` element contains a list of standard PIISA [pii task descriptors];
those will be the ones that the plugin makes available to the framework. In order
to create this list the following requirements must be met:
 * the PII descriptor must contain an additional `extra` field that contains the
   Transformers model label to be mapped to the descriptor
 * the entity language must have a loaded model defined in the
   `task_config` section (which in turn requires the model to be available in
   the system)
   

[PIISA configuration file]: https://github.com/piisa/piisa/blob/main/docs/configuration.md
[pii task descriptors]: https://github.com/piisa/pii-extract-base/tree/main/doc/task-descriptor.md

[default configuration]: ../src/pii_extract_plg_transformers/resources/plugin-config.json
[default file]: ../src/pii_extract_plg_transformers/resources/plugin-config.json

[extended configuration]: example5.json
[some examples]: examples.md

[cache directory]: ../README.md#cache-directory
[token classification models in the Hugging Face Hub]: https://huggingface.co/models?pipeline_tag=token-classification
[token classification]: https://huggingface.co/docs/transformers/v4.31.0/en/main_classes/pipelines#transformers.TokenClassificationPipeline
[aggregation strategy]: https://huggingface.co/docs/transformers/v4.31.0/en/main_classes/pipelines#transformers.TokenClassificationPipeline.aggregation_strategy
