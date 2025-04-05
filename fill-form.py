#!/usr/bin/env python

from typing import Union, BinaryIO, AnyStr

import sys

from core.settings import FieldValues
from core.pdf_filler import fill_pdf


def read_values(values: Union[BinaryIO, AnyStr]) -> FieldValues:
    if type(values) is str or type(values) is bytes:
        return FieldValues.from_file(values)

    return FieldValues.from_stream(values)


def main():
    pdf_form = sys.argv[1]
    if pdf_form == "-":
        pdf_form = sys.stdin

    values_source = sys.stdin
    if len(sys.argv) > 2 and sys.argv[2] != "-":
        values_source = sys.argv[2]

    pdf_output = sys.stdout.buffer
    if len(sys.argv) > 3 and sys.argv[3] != "-":
        pdf_output = sys.argv[3]

    field_values = read_values(values_source)
    fill_pdf(input_pdf=pdf_form, field_values=field_values.data, output_pdf=pdf_output)


if __name__ == "__main__":
    main()
