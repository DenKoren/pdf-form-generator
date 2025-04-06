"""
Fill a PDF form with values from a YAML file.

Is stored as a separate module to allow as small imports as possible, 
avoiding reportlab and PyPDF4 dependencies and allowing the module
to be used in restricted containers where reportlab deps cannot be compiled.
"""

from typing import Union, BinaryIO, AnyStr

import sys
import click

from core.settings import FieldValues
from core.operations_fill import fill_form


def read_values(values: Union[BinaryIO, AnyStr]) -> FieldValues:
    if type(values) is str or type(values) is bytes:
        return FieldValues.from_file(values)

    return FieldValues.from_stream(values)


@click.command(name="fill")
@click.argument("pdf_form", type=click.Path(exists=True))
@click.argument("values_source", type=click.Path(exists=True), required=False)
@click.argument("pdf_output", type=click.Path(), required=False)
@click.help_option("--help", "-h", help="Show this message and exit.")
def fill(pdf_form, values_source, pdf_output):
    """Fill a PDF form with values from a YAML file.

    This program takes a PDF form and fills it with values from a YAML file.
    The result is saved as a new PDF file.

    If values_source is not specified or is '-', values are read from stdin.
    If pdf_output is not specified or is '-', output is written to stdout.
    """
    if pdf_form == "-":
        pdf_form = sys.stdin

    if values_source is None or values_source == "-":
        values_source = sys.stdin

    if pdf_form == values_source == sys.stdin:
        click.UsageError("fill command cannot get both PDF and values from stdin")

    if pdf_output is None or pdf_output == "-":
        pdf_output = sys.stdout.buffer

    field_values = read_values(values_source)
    fill_form(input_pdf=pdf_form, field_values=field_values.data, output_pdf=pdf_output)
