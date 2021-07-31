#!/usr/bin/env python

from typing import Optional

import os
import sys

from reportlab.pdfgen import canvas
from reportlab.lib.colors import transparent
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm

from PyPDF4 import PdfFileWriter, PdfFileReader, pdf

from core.settings import FormSettings

FIELD_FLAG_MULTILINE = 'multiline'
FIELD_FLAG_NO_SCROLL = 'doNotScroll'


def create_form(settings: FormSettings, form_name: str, filename: str = 'simple_form.pdf'):
    c = canvas.Canvas(
        filename=filename,
        pagesize=A4,
    )

    c.setFont("Helvetica", 10)

    default_border_width = 0
    if os.environ.get("ATTACH_FORM_DEBUG", "0") == "1":
        default_border_width = 1

    form_fields_settings = settings.form(form_name)
    form = c.acroForm

    for page_fields in form_fields_settings:
        for field in page_fields:
            form.textfield(
                name=field.name,
                tooltip=field.tooltip,
                x=field.x * mm,
                y=field.y * mm,
                width=field.w * mm,
                height=field.h,
                maxlen=field.maxlen,
                fillColor=transparent,
                borderWidth=field.border_width if field.border_width else default_border_width,
                fontName=field.font_name,
                fontSize=field.font_size,
                fieldFlags=' '.join(field.flags),
            )

        c.showPage()

    c.save()


def attach_form(original_document: str = 'original.pdf',
                form: str = 'form.pdf',
                result_document: str = 'result.pdf'):
    form_reader = PdfFileReader(form)
    form_size = form_reader.getNumPages()

    original_reader = PdfFileReader(original_document)
    original_size = original_reader.getNumPages()

    result_writer = PdfFileWriter()
    result_size = max(original_size, form_size)

    for page_num in range(result_size):
        original_page: Optional[pdf.PageObject] = None
        form_page: Optional[pdf.PageObject] = None

        if page_num < original_size:
            original_page = original_reader.getPage(pageNumber=page_num)

        if page_num < form_size:
            form_page = form_reader.getPage(pageNumber=page_num)

        page = original_page
        if page is None:
            # 'Form' document has more pages than original. Just use the form page 'as is'.
            page = form_page
        elif form_page is not None:
            # 'Form' has the page with the same number as in original document. Merge them.
            page.mergePage(form_page)

        result_writer.addPage(page)

    # Copy AcroForm objects 'as-is' to the new document to make other frameworks able
    # to see and fill form fields
    result_writer._root_object.update({
         pdf.NameObject("/AcroForm"): form_reader.trailer["/Root"]["/AcroForm"]
    })

    with open(result_document, 'wb') as out:
        result_writer.write(out)


def create_and_attach_form(settings: FormSettings,
                           form_name: str,
                           original_document: str,
                           result_document: str):

    form_file = os.path.join(os.path.dirname(result_document), "form.pdf")
    create_form(settings, form_name, form_file)
    attach_form(original_document=original_document, form=form_file, result_document=result_document)

    os.remove(form_file)


def main():
    settings_file = sys.argv[1]
    form_settings = FormSettings.from_file(settings_file)

    form_name = sys.argv[2]

    document = "./example.pdf"
    if len(sys.argv) > 3:
        document = sys.argv[3]

    result = "./result.pdf"
    if len(sys.argv) > 4:
        result = sys.argv[4]

    create_and_attach_form(settings=form_settings,
                           form_name=form_name,
                           original_document=document,
                           result_document=result)


if __name__ == '__main__':
    main()
