from typing import List, Tuple, Optional

import os
import sys

from reportlab.pdfgen import canvas
from reportlab.pdfbase import acroform
from reportlab.lib.colors import transparent
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm

from PyPDF4 import PdfFileWriter, PdfFileReader, pdf

FORM_FONT_SIZE_DEFAULT = 10
FORM_FONT_NAME_DEFAULT = 'Helvetica'

FIELD_FLAG_MULTILINE = 'multiline'
FIELD_FLAG_NO_SCROLL = 'doNotScroll'


class TextField:
    def __init__(self,
                 name: str,
                 x: float,
                 y: float,
                 width: float,
                 tooltip: str = '',
                 flags: List = None,
                 height: float = FORM_FONT_SIZE_DEFAULT * 1.5,
                 maxlen: int = 100,
                 font_size: int = FORM_FONT_SIZE_DEFAULT
                 ):
        self.name: str = name
        self.x: float = x
        self.y: float = y
        self.width: float = width
        self.tooltip: str = tooltip
        self.flags: List = flags
        self.height: float = height
        self.maxlen: int = maxlen
        self.font_size: int = font_size


class Form:
    def __init__(self, form: acroform.AcroForm):
        self.form: acroform.AcroForm = form

    def add_text(self, field: TextField):
        flags = field.flags
        if flags is None:
            flags = [FIELD_FLAG_NO_SCROLL]

        self.form.textfield(name=field.name,
                            tooltip=field.tooltip,
                            x=field.x * mm,
                            y=field.y * mm,
                            width=field.width * mm,
                            height=field.height,
                            maxlen=field.maxlen,
                            fillColor=transparent,
                            borderWidth=0,
                            fontName=FORM_FONT_NAME_DEFAULT,
                            fontSize=field.font_size,
                            fieldFlags=' '.join(flags),
                            )


def date_field(name: str,
               x: float,
               y: float,
               flags: List = None) -> Tuple[TextField, TextField, TextField]:
    date = TextField(f"{name}-day", x, y, 11, "день", flags)
    month = TextField(f"{name}-month", x + 12.5, y, 27, "месяц", flags)
    year = TextField(f"{name}-year", x + 41, y, 14, "год", flags)

    return date, month, year


def number_field(name: str,
                 x: float,
                 y: float,
                 width: float = 11,
                 tooltip: str = "число",
                 flags: List = None):
    return TextField(name, x, y, width, tooltip, flags)


def tenant_info(x: float,
                y: float):
    surname = TextField("tenant_info-surname", x+10.5, y, 63.4, "Фамилия"),
    name = TextField("tenant_info-name", x+10.5, y-5, 63.4, "Имя"),
    parent_name = TextField("tenant_info-parent_name", x+10.5, y-10, 63.4, "Отчество"),
    birth = TextField("tenant_info-birth", x+27.5, y-15, 46.4, "дата"),

    registration = TextField("tenant_info-registration", x, y-37.9, 75, "Адрес регистрации",
                             flags=[FIELD_FLAG_MULTILINE], height=51, maxlen=400),

    id_series = number_field("tenant_info-passport-series", x+26.7, y-43, tooltip='серия'),
    id_number = number_field("tenant_info-passport-number", x+41.6, y-43, 33, tooltip='номер'),
    id_issuer = TextField("tenant_info-passport-issuer", x, y-65.8, 75, "Адрес регистрации",
                          flags=[FIELD_FLAG_MULTILINE], height=51, maxlen=400),
    id_issue_date = *date_field("tenant_info-passport-issue_date", x+17, y-75.9),

    signature_date = *date_field("tenant_info-signature-date", x+17, y-91.4),

    return (*surname,
            *name,
            *parent_name,
            *birth,
            *registration,
            *id_series,
            *id_number,
            *id_issuer,
            *id_issue_date,
            *signature_date)


def create_form(pages: List[List[TextField]], filename: str = 'simple_form.pdf'):
    c = canvas.Canvas(
        filename=filename,
        pagesize=A4,
    )

    c.setFont("Helvetica", 10)

    form = Form(c.acroForm)

    for page in pages:
        for field in page:
            form.add_text(field)

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


def create_and_attach_form(original_document: str,
                           result_document: str):
    form_config: List[List[TextField]] = [
        [
            *date_field("contract-date", 131, 279.9),
            TextField("contract-number", 156.8, 265.7, 32, 'номер договора', height=18, font_size=16),

            TextField("tenant-name", 61, 245.9, 126, 'ФИО Арендатора'),

            TextField("harp-name", 28, 199.3, 86.5, 'Название арфы'),
            number_field("harp-strings_count", 127.5, 199.3),
            TextField("harp-inventory_number", 153.5, 199.3, 27, "инвентарный номер"),
            number_field("harp-keys_count", 63.7, 192.8),
            number_field("harp-legs_count", 89.4, 186.4),
            TextField("harp-additionals_1", 28, 179.75, 152, "любая дополнительная информация"),
            TextField("harp-additionals_2", 28, 173.35, 152, "любая дополнительная информация"),
            number_field("harp-contract-number", 73.7, 156.7, tooltip="номер договора", width=20),
            *date_field("harp-contract-date", 99, 156.7),
            TextField("harp-price-digits", 74, 145.2, 115, "стоимость числом"),
            TextField("harp-price-text", 29, 140.1, 145, "стоимость прописью"),
        ],
        [
            number_field("contract-payment-day", 25.5, 156.6),
            TextField("contract-payment-digits", 25.5, 151.5, 41, "сумма числом"),
            TextField("contract-payment-text", 68.8, 151.5, 119, "сумма прописью"),
            TextField("contract-insurance-digits", 122.8, 134.8, 66, "сумма числом"),
            TextField("contract-insurance-text", 27.5, 129.7, 147, "сумма прописью"),
        ],
        [
            *date_field("contract-end_date", 123.7, 70.2),
        ],
        [
            TextField("contract-additionals", 19.5, 160, 168, "дополнительные условия договора",
                      flags=[FIELD_FLAG_MULTILINE], height=51),

            *date_field("renter-signature-date", 38, 37.9),

            *tenant_info(112, 129.3)
        ]
    ]

    form_file = os.path.join(os.path.dirname(result_document), "form.pdf")

    create_form(pages=form_config, filename=form_file)
    attach_form(original_document=original_document, form=form_file, result_document=result_document)

    os.remove(form_file)


if __name__ == '__main__':
    document = "./example.pdf"
    if len(sys.argv) >= 1:
        document = sys.argv[1]

    result = "./result.pdf"
    if len(sys.argv) >= 2:
        result = sys.argv[2]

    create_and_attach_form(document, result)

