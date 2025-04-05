from typing import Dict, Optional, Union, BinaryIO, AnyStr

import pdfrw
from reportlab.pdfgen import canvas
import reportlab.lib.colors as colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from PyPDF4 import PdfFileWriter, PdfFileReader, pdf

from core import const
from core.settings import FormSettings


def create_form(
    settings: FormSettings,
    form_name: str,
    filename: str = "simple_form.pdf",
    debug: bool = False,
):
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
                fieldFlags=" ".join(field.flags),
            )

        c.showPage()

    c.save()


def attach_form(
    original_document: str = "original.pdf",
    form: str = "form.pdf",
    result_document: str = "result.pdf",
):
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
    result_writer._root_object.update(
        {pdf.NameObject("/AcroForm"): form_reader.trailer["/Root"]["/AcroForm"]}
    )

    with open(result_document, "wb") as out:
        result_writer.write(out)


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
