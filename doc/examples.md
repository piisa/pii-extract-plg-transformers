# Examples

The [default configuration] defines models for English and Spanish. There is
also another [example configuration](example5.json) available that extends it
to add French, German, Portuguese and Spanish. Its behaviour can be tested using
the `detect` script like this:


* English:

        pii-extract-transformers-detect --config example6.json --lang en --input-data "Hello. My name is Íñigo Montoya. You killed my father in Toledo"

* Spanish:

        pii-extract-transformers-detect --config example6.json --lang es --input-data "Hola. Mi nombre es Íñigo Montoya. Tú mataste a mi padre en Toledo"

* French:

        pii-extract-transformers-detect --config example6.json --lang fr --input-data "Salut. Je m'appelle Íñigo Montoya. Vous avez tué mon père à Toledo"

* German:

        pii-extract-transformers-detect --config example6.json --lang de --input-data "Hallo. Mein name is Íñigo Montoya. Du hast mein Vater in Toledo getötet"

* Portuguese:

        pii-extract-transformers-detect --config example6.json --lang pt --input-data "Olá. Meu nome é Iñigo Montoya. Você matou meu pai em Toledo"

* Italian:

        pii-extract-transformers-detect --config example6.json --lang pt --input-data "Ciao. Mi chiamo Iñigo Montoya. Tu hai ucciso mio padre a Toledo"


Note that the models defined in the configuration are only examples; the
Hugging Face Hub contains many models for NER Token Classification, and some
of them might be more appropriate than others for PII detection tasks.

Also, if a model is multilingual, it could be used for more than one language
(the example contains one such case). And while in this example config all the
models use the same labels for the entities, the configuration can also
accomodate models whose labels for the same entity are different; in that case
the entries in the `pii_list` field (which match model entities to PII
instances) would be deaggregated by language.


[default configuration]: ../src/pii_extract_plg_transformers/resources/plugin-config.json
