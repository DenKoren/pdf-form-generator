#!/usr/bin/env python

from typing import Dict, Optional, Union, BinaryIO, AnyStr

import sys
import pdfrw

from core import const
from core.settings import FieldValues


def read_values(values: Union[BinaryIO, AnyStr]) -> FieldValues:
    if type(values) is str or type(values) is bytes:
        return FieldValues.from_file(values)

    return FieldValues.from_stream(values)


def fill_pdf(input_pdf, field_values: Optional[Dict] = None, output_pdf: Union[BinaryIO, AnyStr] = sys.stdout):
    if field_values is None:
        field_values = {}

    template_pdf: pdfrw.PdfReader = pdfrw.PdfReader(input_pdf)
    page: pdfrw.PdfDict
    for page in template_pdf.pages:
        annotations: Optional[pdfrw.PdfArray] = page[const.KEY_ANNOTATIONS]
        if annotations is None:
            continue

        for annotation in annotations:
            if annotation[const.KEY_SUBTYPE] == const.SUBTYPE_WIDGET:

                annotation_name = annotation.get(const.ANNOT_NAME)
                if annotation_name is None:
                    continue

                annotation_name = annotation_name.decode()  # restore original annotation name to make comparison work
                value = field_values.get(annotation_name)

                if value is None:
                    continue

                if type(value) == bool:
                    if value:
                        annotation.update(
                            pdfrw.PdfDict(AS=pdfrw.PdfName('Yes'))
                        )
                else:
                    annotation.update(
                        pdfrw.PdfDict(
                            V=str(value),
                            AP=''
                        )
                    )

    template_pdf.Root.AcroForm.update(pdfrw.PdfDict(NeedAppearances=pdfrw.PdfObject('true')))
    pdfrw.PdfWriter().write(output_pdf, template_pdf)


def main():
    pdf_form = sys.argv[1]
    if pdf_form == '-':
        pdf_form = sys.stdin

    values_source = sys.stdin
    if len(sys.argv) > 2 and sys.argv[2] != '-':
        values_source = sys.argv[2]

    pdf_output = sys.stdout.buffer
    if len(sys.argv) > 3 and sys.argv[3] != '-':
        pdf_output = sys.argv[3]

    field_values = read_values(values_source)
    fill_pdf(input_pdf=pdf_form,
             field_values=field_values.data,
             output_pdf=pdf_output)


if __name__ == '__main__':
    main()
