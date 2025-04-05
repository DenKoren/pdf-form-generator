#!/usr/bin/env python

from typing import Optional

import os
import click

from reportlab.pdfgen import canvas
import reportlab.lib.colors as colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm

from PyPDF4 import PdfFileWriter, PdfFileReader, pdf

from core.settings import FormSettings
from core.pdf_filler import fill_pdf

FIELD_FLAG_MULTILINE = 'multiline'
FIELD_FLAG_NO_SCROLL = 'doNotScroll'


def create_form(settings: FormSettings, form_name: str, filename: str = 'simple_form.pdf', debug: bool = False):
    c = canvas.Canvas(
        filename=filename,
        pagesize=A4,
    )

    c.setFont("Helvetica", 10)

    form_fields_settings = settings.form(form_name)
    form = c.acroForm

    for page_fields in form_fields_settings:
        for field in page_fields:
            border_width = field.border_width if field.border_width else 0
            border_color = field.border_color if field.border_color else "black"
            if debug:
                border_color = "red"
                border_width = 2

            form.textfield(
                name=field.name,
                tooltip=field.tooltip,
                x=field.x * mm,
                y=field.y * mm,
                width=field.w * mm,
                height=field.h,
                maxlen=field.maxlen,
                fillColor=field.fill_color if field.fill_color else colors.transparent,
                borderWidth=border_width,
                borderColor=getattr(colors, border_color),
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
                           result_document: str,
                           debug: bool = False):

    form_file = os.path.join(os.path.dirname(result_document), "form.pdf")
    create_form(settings, form_name, form_file, debug)
    attach_form(original_document=original_document, form=form_file, result_document=result_document)

    os.remove(form_file)

    if debug:
        os.rename(result_document, form_file)
        field_ids = settings.form_field_ids(form_name)
        field_values = {field_id: field_id for field_id in field_ids}
        fill_pdf(input_pdf=form_file,
                 field_values=field_values,
                 output_pdf=result_document)



@click.command()
@click.option('--debug', 
              is_flag=True, 
              help="Debug mode. Makes all inputs to be visible and contain IDs.")
@click.argument('form_definitions', required=True, type=click.Path(exists=True))
@click.argument('form_name', required=True)
@click.argument('original_document', required=True, type=click.Path(exists=True))
@click.argument('result_document', required=False, type=click.Path(exists=False))
@click.help_option('--help', '-h', help="Show this message and exit.")
def cli(form_definitions, form_name, original_document, result_document, debug):
    """Create and attach a PDF form to an existing document.
    
    This program takes a form definition file, creates a PDF form, and attaches it to
    an existing PDF document. The result is saved as a new PDF file.
    """
    if result_document is None:
        result_document = os.path.join(os.path.dirname(original_document), "result.pdf")

    settings = FormSettings.from_file(form_definitions)
    create_and_attach_form(settings=settings,
                           form_name=form_name,
                           original_document=original_document,
                           result_document=result_document,
                           debug=debug)

if __name__ == '__main__':
    cli()
