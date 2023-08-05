"""
These are the converter functions for the NTCIR-10 Math converter package.
"""

from logging import getLogger
from multiprocessing import Pool
from pathlib import Path
from zipfile import ZipFile

from lxml import etree
from lxml.etree import Element, SubElement, QName
from tqdm import tqdm


LOGGER = getLogger(__name__)
PARAGRAPH_XPATH = ".//xhtml:div[contains(concat(' ', normalize-space(@class), ' '), ' para ')]"
NAMESPACES = {
    "m": "http://www.w3.org/1998/Math/MathML",
    "xhtml": "http://www.w3.org/1999/xhtml",
}


def get_judged_identifiers(input_file):
    """
    Extracts the names of judged documents and the identifiers of their judged elements from
    relevance in the NTCIR-10 Math format.

    Parameters
    ----------
    input_file : file
        The input file containing relevance judgements in the NTCIR-10 Math format.

    Yields
    ------
    (str, str)
        Judged document names and the judged element identifiers
    """
    for line in tqdm(list(input_file)):
        identifier = line.split(' ')[2]
        document_basename, element_id = identifier.split('#')
        document = Path(document_basename).with_suffix(".xhtml")
        yield document.name, element_id


def convert_judgements(input_file, output_file, identifier_map):
    """
    Converts relevance judgements from the NTCIR-10 Math format to the NTCIR-11 Math-2, and the
    NTCIR-12 MathIR format.

    Parameters
    ----------
    input_file : file
        The input file containing relevance judgements in the NTCIR-10 Math format.
    output_file : file
        The output file that will contain relevance judgements in the NTCIR-11 Math-2, and the
        NTCIR-12 MathIR format.
    identifier_map : dict of (str, str)
        A mapping between element identifiers, and paragraph identifiers.
    """
    input_lines = list(input_file)
    output_lines = []
    for line in tqdm(input_lines):
        topic, unused, identifier, score = line.split(' ')
        if identifier not in identifier_map:
            LOGGER.warning("Skipping identifier %s, as it appears outside a paragraph", identifier)
        else:
            output_lines.append("%s %s %s %d" % (
                topic, unused, identifier_map[identifier], int(score)))
    LOGGER.info("%d / %d input / output relevance judgements", len(input_lines), len(output_lines))
    output_file.write('\n'.join(output_lines))




def process_dataset(input_root_dir, output_root_dir=None, judged_identifiers=None, num_workers=1):
    """
    Processes the NTCIR-10 Math XHTML5 dataset, building a mapping between element identifiers, and
    paragraph identifiers, and optionally also building an equivalent dataset in the NTCIR-11
    Math-2, and NTCIR-12 MathIR XHTML5 format.

    Parameters
    ----------
    input_root_dir : pathlib.Path
        The input directory containing the NTCIR-10 Math XHTML5 dataset.
    output_root_dir : pathlib.Path or None, optional
        The output directory that will contain the dataset from the input directory converted to the
        NTCIR-11 Math-2, and the NTCIR-12 MathIR XHTML5 format. If None, no conversion will be
        performed.
    judged_identifiers : dict of (str, set of str) or None, optional
        The names of judged documents and the identifiers of their judged elements. This constrains
        the documents that are actually processed when we are not building a dataset, and the
        elements whose identifiers are recorded in the mapping between element identifiers, and
        paragraph identifiers.
    num_workers : int, optional
        The number of processes that will process the documents in the NTCIR-10 Math dataset.

    Returns
    -------
    dict of (str, str)
        A mapping between element identifiers, and paragraph identifiers.
    """
    dataset_identifier_map = {}
    if output_root_dir:
        LOGGER.info("Converting dataset %s -> %s", input_root_dir, output_root_dir)
    if judged_identifiers is not None:
        LOGGER.info("Building a mapping between element identifiers, and paragraph identifiers")
    arguments = []
    for input_file in (
            input_file for input_file in input_root_dir.glob("**/*.xhtml")
            if output_root_dir or judged_identifiers is None
            or input_file.name in judged_identifiers):
        output_dir = input_file.relative_to(input_root_dir).with_suffix("")
        if output_root_dir:
            LOGGER.debug("Creating directory %s", output_root_dir / output_dir)
            (output_root_dir / output_dir).mkdir(parents=True)
        if judged_identifiers is not None and input_file.name in judged_identifiers:
            judged_element_identifiers = judged_identifiers[input_file.name]
        else:
            judged_element_identifiers = None
        arguments.append((input_file, output_root_dir, output_dir, judged_element_identifiers))
    with Pool(num_workers) as pool:
        for document_identifier_map in tqdm(
                pool.imap_unordered(_process_document_worker, arguments),
                total=len(arguments)):
            dataset_identifier_map.update(document_identifier_map)
    return dataset_identifier_map


def _process_document_worker(args):
    input_file, output_root_dir, output_dir, judged_element_identifiers = args
    document_identifier_map = {}
    LOGGER.debug("Processing document %s", input_file)
    with input_file.open("rt") as f:
        input_tree = etree.parse(f)
    input_paragraphs = input_tree.xpath(PARAGRAPH_XPATH, namespaces=NAMESPACES)
    for input_paragraph_num, input_paragraph in enumerate(input_paragraphs):
        if "id" not in input_paragraph.attrib:
            LOGGER.warning(
                "Skipping a paragraph in document %s, because it lacks an identifier", input_file)
            continue
        LOGGER.debug(
            "Processing paragraph %s in document %s", input_paragraph.attrib["id"], input_file)
        output_file = Path(
            "%s_1_%d" % (
                str(input_file.with_suffix("").name), input_paragraph_num + 1
            )).with_suffix(".xhtml.zip")
        for input_element in input_paragraph.findall(".//*[@id]"):
            if judged_element_identifiers is not None and \
                    input_element.attrib["id"] in judged_element_identifiers:
                ntcir10_identifier = "%s#%s" % (
                    str(input_file.with_suffix("").name), input_element.attrib["id"])
                ntcir11_12_identifier = str(output_file.with_suffix("").with_suffix("").name)
                LOGGER.debug("Mapping %s -> %s", ntcir10_identifier, ntcir11_12_identifier)
                if ntcir10_identifier in document_identifier_map \
                        and document_identifier_map[ntcir10_identifier] != ntcir11_12_identifier:
                    LOGGER.warning(
                        "Duplicate element with element id %s occurs in paragraphs %s, and %s",
                        ntcir10_identifier, document_identifier_map[ntcir10_identifier],
                        ntcir11_12_identifier)
                else:
                    document_identifier_map[ntcir10_identifier] = ntcir11_12_identifier
        if output_root_dir:
            LOGGER.debug("Creating ZIP archive %s", output_root_dir / output_dir / output_file)
            with ZipFile((output_root_dir / output_dir / output_file).open("wb"), "w") as zip_file:
                LOGGER.debug(
                    "Creating archived file %s/%s",
                    (output_root_dir / output_dir / output_file),
                    output_file.with_suffix("").name)
                html = Element(QName(NAMESPACES["xhtml"], "html"), {}, {None: NAMESPACES["xhtml"]})
                head = SubElement(html, QName(NAMESPACES["xhtml"], "head"))
                SubElement(head, QName(NAMESPACES["xhtml"], "meta"), {
                    "http-equiv": "Content-Type",
                    "content": "application/xhtml+xml; charset=UTF-8"
                })
                body = SubElement(html, QName(NAMESPACES["xhtml"], "body"))
                body.append(input_paragraph)
                zip_file.writestr(output_file.with_suffix("").name, etree.tostring(html))
    return document_identifier_map
