from typing import Dict, Optional

import sys
from datetime import date
import yaml

import pdfrw

import const


def read_values(values_file_path: str) -> Dict:
    with open(values_file_path) as f:
        data: Dict = yaml.safe_load(f)

    return data.get('field_values', {})


def fill_pdf(input_pdf_path, output_pdf_path, field_values: Optional[Dict] = None):
    if field_values is None:
        field_values = {}

    template_pdf = pdfrw.PdfReader(input_pdf_path)
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
    pdfrw.PdfWriter().write(output_pdf_path, template_pdf)


field_values_file = sys.argv[1]
pdf_template = sys.argv[2]
pdf_output = sys.argv[3]


data_dict = read_values(field_values_file)
fill_pdf(pdf_template, pdf_output, data_dict)
