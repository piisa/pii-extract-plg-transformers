"""
Command-line script to show information about the plugin
"""

import sys
import argparse
from operator import itemgetter

from typing import List, TextIO

from pii_data import VERSION as VERSION_DATA
from pii_data.helper.exception import ProcException
from pii_data.helper.logger import PiiLogger

from pii_extract import VERSION as VERSION_EXTRACT
from pii_extract.gather.parser import parse_task_descriptor
from pii_extract.gather.collection.sources.utils import RawTaskDefaults
from pii_extract.gather.collection.task_collection import filter_piid
from pii_extract.build.build import build_task

from .. import VERSION
from .. import defs
from ..plugin_loader import load_plugin_config
from ..task.utils import hf_cachedir, transformers_version
from ..task import TaskCollector


class Processor:

    def __init__(self, args: argparse.Namespace, debug: bool = False):
        self.args = args
        self.debug = debug
        self.log = PiiLogger(__name__, debug=True) if debug else None


    def _init_pipelines(self):
        """
        Initialize the Transformers pipelines
        """
        config = load_plugin_config(self.args.config)
        hf_cachedir(config.get("cachedir"))
        try:
            from ..task.pipeline import create_pipelines
            return create_pipelines(config[defs.CFG_TASK],
                                    languages=self.args.lang, logger=self.log)
        except Exception as e:
            raise ProcException("cannot create Transformers pipelines: {}",
                                e) from e


    def proc_version(self, out: TextIO):
        """
        List package versions
        """
        print(". Installed package versions", file=out)
        version = {"PII data": VERSION_DATA,
                   "PII extract-base": VERSION_EXTRACT,
                   "PII Transformers plugin": VERSION,
                   "Transformers": transformers_version()}
        for n, v in version.items():
            print(f"{n:>25}: {v}")


    def proc_models(self, out: TextIO):
        """
        Print Transformers models loaded
        """
        print(f". Available pipelines (lang={self.args.lang})", flush=True)
        pipelines = self._init_pipelines()
        param = {"type": "model_type", "name": "_name_or_path"}
        for lang, pp in sorted(pipelines.items(), key=itemgetter(0)):
            name = pp.model.__class__.__name__
            cfg = pp.model.config
            print(f"{lang}:   {name}")
            for f, a in param.items():
                print(f"{f:>10}:", getattr(cfg, a, ""))
            #print(pp.model.config)


    def proc_model_entities(self, out: TextIO):
        """
        Print entities defined in the models
        """
        print(f". Labels defined in models (lang={self.args.lang})", flush=True)
        pipelines = self._init_pipelines()
        try:
            from ..task.pipeline import ner_labels

            for lang, pp in pipelines.items():
                labels = ner_labels(pp)
                print(f"{lang}:", ", ".join(labels))
        except Exception as e:
            raise ProcException("cannot get model labels: {}", e) from e


    def proc_pii_entities(self, out: TextIO):
        """
        Print entity recognizers
        """
        config = load_plugin_config(self.args.config)

        # Get the Presidio task descriptor
        tc = TaskCollector(config, languages=self.args.lang, debug=self.debug)
        raw_tdesc = tc.gather_tasks()

        # Ensure it is normalized
        reformat = RawTaskDefaults()
        tdesc = reformat(raw_tdesc)

        print(f". PII entities defined from plugin models (lang={self.args.lang})")
        for td in tdesc:
            # Create the task definition (inc. pii demultiplexing)
            tdef = parse_task_descriptor(td)

            # Filter by language
            if self.args.lang:
                lset = set(self.args.lang)
                tdef["piid"] = filter_piid(tdef["piid"], lang=lset)

            # Build the task
            task = build_task(tdef)

            # Now traverse the pii_info list
            for t in task.pii_info:
                nam = f"{t.pii.name}, {t.subtype}" if t.subtype else t.pii.name
                method = task.get_method(t)
                print(f"  {nam:40} {t.lang:5} {method}")



def parse_args(args: List[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=f"Show information about the plugin (version {VERSION})")

    opt_com1 = argparse.ArgumentParser(add_help=False)
    c1 = opt_com1.add_argument_group('Configuration options')
    c1.add_argument("--config", nargs="+",
                    help="add PIISA configuration file(s)")
    c1.add_argument("--lang", nargs='+', help="language to select")

    opt_com2 = argparse.ArgumentParser(add_help=False)
    c1 = opt_com2.add_argument_group('Task selection options')

    opt_com3 = argparse.ArgumentParser(add_help=False)
    c2 = opt_com3.add_argument_group("Other")
    c2.add_argument("--debug", action="store_true", help="debug mode")
    c2.add_argument('--reraise', action='store_true',
                    help='re-raise exceptions on errors')

    subp = parser.add_subparsers(help='command', dest='cmd')

    subp.add_parser('version', help='show version information for components',
                    parents=[opt_com1, opt_com3])

    subp1 = subp.add_parser('models',
                            help='information about configured models',
                            parents=[opt_com1, opt_com3])

    subp1 = subp.add_parser('model-entities',
                            help='information about entities defined in Transformer models',
                            parents=[opt_com1, opt_com3])

    subp1 = subp.add_parser('pii-entities',
                            help='information about PII tasks defined via the plugin',
                            parents=[opt_com1, opt_com3])

    parsed = parser.parse_args(args)
    if not parsed.cmd:
        parser.print_usage()
        sys.exit(1)
    return parsed


def main(args: List[str] = None):
    if args is None:
        args = sys.argv[1:]
    args = parse_args(args)

    try:
        proc = Processor(args, args.debug)
        mth_name = 'proc_' + args.cmd.replace('-', '_')
        mth = getattr(proc, mth_name)
        mth(sys.stdout)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        if args.reraise:
            raise
        else:
            sys.exit(1)


if __name__ == "__main__":
    main()
