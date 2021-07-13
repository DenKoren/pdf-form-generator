#!/usr/bin/env python

from typing import Dict, Optional, Union, BinaryIO, AnyStr

import sys
import yaml

import pdfrw

import const


def read_values(values: Union[BinaryIO, AnyStr]) -> Dict:
    if type(values) is str or type(values) is bytes:
        with open(values) as f:
            data: Dict = yaml.safe_load(f)
    else:
        data: Dict = yaml.safe_load(values)

    return data.get('field_values', {})


def fill_pdf(input_pdf, field_values: Optional[Dict] = None, output_pdf: Union[BinaryIO, AnyStr] = sys.stdout):
    if field_values is None:
        field_values = {}

    template_pdf = pdfrw.PdfReader(input_pdf)
    for page in template_pdf.pages:
        annotations = page[const.KEY_ANNOTATIONS]
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
                        annotation.update(pdfrw.PdfDict(
                            AS=pdfrw.PdfName('Yes')))
                else:
                    annotation.update(
                        pdfrw.PdfDict(V=str(value))
                    )
                    annotation.update(pdfrw.PdfDict(AP=''))

    template_pdf.Root.AcroForm.update(pdfrw.PdfDict(NeedAppearances=pdfrw.PdfObject('true')))  # NEW
    pdfrw.PdfWriter().write(output_pdf, template_pdf)


pdf_form = sys.argv[1]
form_values = sys.stdin
if len(sys.argv) >= 3:
    form_values = sys.argv[2]
    if form_values == '-':
        form_values = sys.stdin

pdf_output = sys.stdout.buffer
if len(sys.argv) >= 4:
    pdf_output = sys.argv[3]
    if pdf_output == '-':
        pdf_output = sys.stdout.buffer

data_dict = read_values(form_values)
fill_pdf(input_pdf=pdf_form,
         field_values=data_dict,
         output_pdf=pdf_output)
