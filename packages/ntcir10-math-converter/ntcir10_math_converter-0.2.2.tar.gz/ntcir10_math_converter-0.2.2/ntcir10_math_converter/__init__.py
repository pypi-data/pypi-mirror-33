"""
The NTCIR-10 Math Converter package converts NTCIR-10 Math XHTML5 dataset and relevance judgements
to the NTCIR-11 Math-2, and NTCIR-12 MathIR XHTML5 format.
"""

from .converter import convert_judgements, get_judged_identifiers, process_dataset  # noqa:E401


__author__ = "Vit Novotny"
__version__ = "0.2.2"
__license__ = "MIT"
