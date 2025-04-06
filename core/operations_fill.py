"""
Fill a PDF form with values from a YAML file.

Is stored as a separate module to allow as small imports as possible, 
avoiding reportlab and PyPDF4 dependencies and allowing the module
to be used in restricted containers where reportlab deps cannot be compiled.
"""

from typing import Optional, Dict, Union, AnyStr, BinaryIO

import pdfrw

import core.const as const


def fill_form(
    input_pdf,
    field_values: Optional[Dict] = None,
    output_pdf: Union[BinaryIO, AnyStr] = None,
):
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

                annotation_name = (
                    annotation_name.decode()
                )  # restore original annotation name to make comparison work
                value = field_values.get(annotation_name)

                if value is None:
                    continue

                if type(value) == bool:
                    if value:
                        annotation.update(pdfrw.PdfDict(AS=pdfrw.PdfName("Yes")))
                else:
                    annotation.update(pdfrw.PdfDict(V=str(value), AP=""))

    template_pdf.Root.AcroForm.update(
        pdfrw.PdfDict(NeedAppearances=pdfrw.PdfObject("true"))
    )
    pdfrw.PdfWriter().write(output_pdf, template_pdf)
