from typing import List, Tuple

import os
import sys

from reportlab.pdfgen import canvas
from reportlab.pdfbase import acroform
from reportlab.lib.colors import transparent
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm

from PyPDF4 import PdfFileWriter, PdfFileReader

FORM_TEXT_SIZE_DEFAULT = 10
FORM_TEXT_FONT_DEFAULT = 'Helvetica'

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
                 height: float = FORM_TEXT_SIZE_DEFAULT * 1.5,
                 maxlen: int = 100,
                 ):
        self.name = name
        self.x = x
        self.y = y
        self.width = width
        self.tooltip = tooltip
        self.flags = flags
        self.height = height
        self.maxlen = maxlen


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
                            fontName=FORM_TEXT_FONT_DEFAULT,
                            fontSize=FORM_TEXT_SIZE_DEFAULT,
                            fieldFlags=' '.join(flags),
                            )


def date_field(name: str,
               x: float,
               y: float,
               flags: List = None) -> Tuple[TextField, TextField, TextField]:
    date = TextField(f"{name}.day", x, y, 11, "день", flags)
    month = TextField(f"{name}.month", x + 12.5, y, 27, "месяц", flags)
    year = TextField(f"{name}.year", x + 41, y, 14, "год", flags)

    return date, month, year


def number_field(name: str,
                 x: float,
                 y: float,
                 width: float = 11,
                 tooltip: str = "число",
                 flags: List = None):
    return TextField(name, x, y, width, tooltip, flags)


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
        original_page = None
        form_page = None

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

    with open(result_document, 'wb') as out:
        result_writer.write(out)


def create_and_attach_form(original_document: str,
                           result_document: str):
    form_config: List[List[TextField]] = [
        [
            *date_field("contract.date", 131, 279.7),
            TextField("contract.number", 164, 266, 20, 'номер договора'),

            TextField("tenant.name", 61, 245.5, 126, 'ФИО Арендатора'),

            TextField("harp.name", 28, 199.1, 86.5, 'Название арфы'),
            number_field("harp.strings_count", 116, 199.1),
            TextField("harp.inventory_number", 152.5, 199.1, 27, "инвентарный номер"),
            number_field("harp.keys_count", 63.7, 192.7),
            number_field("harp.legs_count", 89.4, 186.2),
            TextField("harp.additionals_1", 28, 179.7, 150, "любая дополнительная информация"),
            TextField("harp.additionals_2", 28, 173.2, 150, "любая дополнительная информация"),
            number_field("harp.contract.number", 73.7, 156.5, tooltip="номер договора"),
            *date_field("harp.contract.date", 90, 156.5),
            TextField("harp.price.digits", 74, 145, 115, "стоимость числом"),
            TextField("harp.price.text", 29, 140, 145, "стоимость прописью"),
        ],
        [
            number_field("contract.payment.date", 25.5, 156.5),
            TextField("contract.payment.digits", 25.5, 151.4, 41, "сумма числом"),
            TextField("contract.payment.text", 68.8, 151.4, 119, "сумма прописью"),
            TextField("contract.insurance.digits", 122.8, 134.8, 66, "сумма числом"),
            TextField("contract.insurance.text", 27.5, 129.6, 147, "сумма прописью"),
        ],
        [
            *date_field("contract.end_date", 123.7, 51.1),
        ],
        [
            TextField("tenant_info.surname", 122.5, 160.3, 63.4, "Фамилия"),
            TextField("tenant_info.name", 122.5, 155.3, 63.4, "Имя"),
            TextField("tenant_info.parent_name", 122.5, 150.3, 63.4, "Отчество"),
            TextField("tenant_info.registration", 112, 127.6, 75, "Адрес регистрации",
                      flags=[FIELD_FLAG_MULTILINE], height=51, maxlen=400),
            number_field("tenant_info.passport.series", 138.7, 122.5, tooltip='серия'),
            number_field("tenant_info.passport.number", 153.6, 122.5, 33, tooltip='номер'),
            TextField("tenant_info.passport.issuer", 112, 99.7, 75, "Адрес регистрации",
                      flags=[FIELD_FLAG_MULTILINE], height=51, maxlen=400),
            *date_field("tenant_info.passport.issue_date", 129, 89.6),
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

