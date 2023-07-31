"""
Command-line test script to launch the detection process on a text buffer
"""

import sys
import argparse

from typing import List, Iterable

from pii_data.types.doc import DocumentChunk
from pii_data.types.piicollection import PiiDetector, PiiCollection

from pii_extract.build.task import BasePiiTask
from pii_extract.build import build_task
from pii_extract.gather.parser import parse_task_descriptor

from .. import VERSION
from ..task.collector import TaskCollector
from ..plugin_loader import load_plugin_config



def parse_args(args: List[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=f"Perform PII detection on data using the Transformers plugin (version {VERSION})")

    g0 = parser.add_argument_group("Input/output paths")
    g00 = g0.add_mutually_exclusive_group(required=True)
    g00.add_argument("--input-data", help="string to process")
    g00.add_argument("--input-file", help="text file to process")
    g0.add_argument("--outfile", help="destination file")

    g1 = parser.add_argument_group("Specification")
    g1.add_argument("--lang", help="set document language")
    g1.add_argument("--configfile", "--config", nargs="+",
                    help="add a custom configuration file")

    g3 = parser.add_argument_group("Other")
    g3.add_argument("--debug", action="store_true", help="debug mode")
    g3.add_argument('--reraise', action='store_true',
                    help='re-raise exceptions on errors')

    return parser.parse_args(args)


def create_task_object(config, lang: Iterable[str],
                       debug: bool = False) -> BasePiiTask:
    """
    Create the PiiTask object for this plugin
    """
    if isinstance(lang, str):
        lang = [lang]

    # Gather the plugin tasks. Take the first one (there is actually only one)
    c = TaskCollector(config, lang, debug)
    tasklist = c.gather_tasks()
    taskdesc = list(tasklist)[0]

    # Parse the task descriptor to build the task definition
    taskdef = parse_task_descriptor(taskdesc)

    # Build the task from the definition
    return build_task(taskdef)


def process(input_data: str = None, input_file: str = None, outfile: str = None,
            lang: str = None, configfile: str = None, debug: bool = False,
            **kwargs):
    """
    Do the processing
    """
    # Read data
    if input_file:
        if debug:
            print("# Loading text:", input_file, file=sys.stderr)
        with open(input_file, encoding="utf-8") as f:
            input_data = f.read()

    # Create the task
    config = load_plugin_config(configfile)
    task = create_task_object(config, lang, debug)

    # Perform detection
    chunk = DocumentChunk(id="1", data=input_data, context={"lang": lang})
    results = task.find(chunk)

    # Prepare output container
    tinfo = task.task_info
    det = PiiDetector(source=tinfo.source, name=tinfo.name,
                      version=tinfo.version, method=tinfo.method)
    piic = PiiCollection()
    for p in results:
        piic.add(p, det)
    if debug:
        print("# Entities detected:", len(piic), file=sys.stderr)

    if len(piic) == 0:
        return

    # Save results
    if outfile:
        if debug:
            print("# Saving to:", outfile, file=sys.stderr)
        with open(outfile, "w", encoding="utf-8") as f:
            piic.dump(f, format="jsonl")
        return

    # Print out
    for pii in piic:
        for n, v in pii.asdict().items():
            print(f"{n:>12}", v)
        print()


def main(args: List[str] = None):
    """
    Entry point
    """
    if args is None:
        args = sys.argv[1:]
    nargs = parse_args(args)
    args = vars(nargs)
    reraise = args.pop("reraise")
    try:
        process(**args)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        if reraise:
            raise
        else:
            sys.exit(1)


if __name__ == "__main__":
    main()
