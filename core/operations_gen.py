from typing import Optional 

from reportlab.pdfgen import canvas
import reportlab.lib.colors as colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from PyPDF4 import PdfFileWriter, PdfFileReader, pdf

from core.settings import FormSettings
from core.grid import GridSettings, draw_grid


def create_form(
    settings: FormSettings,
    form_name: str,
    filename: str = "simple_form.pdf",
    debug: bool = False,
    grid: GridSettings | None = None,
):
    c = canvas.Canvas(
        filename=filename,
        pagesize=A4,
    )

    c.setFont("Helvetica", 10)

    form_fields_settings = settings.form(form_name)
    form = c.acroForm

    for page_fields in form_fields_settings:
        if grid is not None:
            draw_grid(c, grid)

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
