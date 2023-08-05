"""
This is the command-line interface for the NTCIR-10 Math converter package.
"""

from argparse import ArgumentParser
import logging
from logging import getLogger
from pathlib import Path
from sys import stdout

from .converter import convert_judgements, get_judged_identifiers, process_dataset


LOG_FILE = Path("__main__.log")
LOG_FORMAT = "%(asctime)s : %(levelname)s : %(message)s"
ROOT_LOGGER = getLogger()
LOGGER = getLogger(__name__)


def main():
    """ Main entry point of the app """
    ROOT_LOGGER.setLevel(logging.DEBUG)

    file_handler = logging.StreamHandler(LOG_FILE.open("wt"))
    formatter = logging.Formatter(LOG_FORMAT)
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.DEBUG)
    ROOT_LOGGER.addHandler(file_handler)

    terminal_handler = logging.StreamHandler(stdout)
    terminal_handler.setFormatter(formatter)
    terminal_handler.setLevel(logging.INFO)
    ROOT_LOGGER.addHandler(terminal_handler)

    LOGGER.debug("Parsing command-line arguments")
    parser = ArgumentParser(
        description="""
            Convert NTCIR-10 Math XHTML5 dataset and relevance judgements to the NTCIR-11 Math-2,
            and NTCIR-12 MathIR XHTML5 format.
        """)
    parser.add_argument(
        "--dataset", nargs='+', required=True, type=Path, help="""
            A path to a directory containing the NTCIR-10 Math XHTML5 dataset, and a path to a
            non-existent directory that will contain resulting dataset in the NTCIR-11 Math-2, and
            NTCIR-12 MathIR XHTML5 format. If only the path to the NTCIR-10 Math dataset is
            specified, the dataset will be read to find out the mapping between element identifiers,
            and paragraph identifiers. This is required for converting the relevance judgements.
        """)
    parser.add_argument(
        "--judgements", nargs='+', type=Path, help="""
            Paths to the files containing NTCIR-10 Math relevance judgements (odd arguments),
            followed by paths to the files that will contain resulting relevance judgements in the
            NTCIR-11 Math-2, and NTCIR-12 MathIR format (even arguments).
        """)
    parser.add_argument(
        "--num-workers", type=int, default=1, help="""
            The number of processes that will be used for processing the NTCIR-10 Math dataset.
            Defaults to %(default)d.
        """)
    args = parser.parse_args()

    LOGGER.debug("Performing sanity checks on the command-line arguments")
    input_dir = args.dataset[0]
    output_dir = args.dataset[1] / Path("xhtml5") if len(args.dataset) > 1 else None
    assert input_dir.exists() and input_dir.is_dir()
    if output_dir:
        assert not output_dir.exists()
    if args.judgements:
        assert len(args.judgements) % 2 == 0
    assert args.num_workers > 0

    if args.judgements:
        judged_identifiers = {}
        for i in range(len(args.judgements) // 2):
            input_file = args.judgements[2 * i]
            LOGGER.info(
                "Retrieving judged document names, and element identifiers from %s", input_file)
            with input_file.open("rt") as f:
                for document_name, element_identifier in get_judged_identifiers(f):
                    LOGGER.debug(
                        "Document %s, element id %s is judged", document_name, element_identifier)
                    if document_name not in judged_identifiers:
                        judged_identifiers[document_name] = set()
                    judged_identifiers[document_name].add(element_identifier)
    else:
        judged_identifiers = None

    if args.judgements:
        LOGGER.info("Processing dataset %s", input_dir)
    identifier_map = process_dataset(
        input_dir, output_dir, judged_identifiers, args.num_workers)

    if args.judgements:
        for i in range(len(args.judgements) // 2):
            input_file = args.judgements[2 * i]
            output_file = args.judgements[2 * i + 1]
            LOGGER.info(
                "Converting relevance judgements %s -> %s", input_file, output_file)
            with input_file.open("rt") as f1, output_file.open("wt") as f2:
                convert_judgements(f1, f2, identifier_map)


if __name__ == "__main__":
    """ This is executed when run from the command line """
    main()
