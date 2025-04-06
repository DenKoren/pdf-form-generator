import os
import click

from core.settings import FormSettings
from core.operations_gen import create_form, attach_form
from core.operations_fill import fill_form
from core.grid import DefaultGridSettings, GridSettings


def _add_form_to_file(
    settings: FormSettings,
    form_name: str,
    original_document: str,
    result_document: str,
    debug: bool = False,
    grid: GridSettings | None = None,
):
    form_file = os.path.join(os.path.dirname(result_document), "form.pdf")
    create_form(settings, form_name, form_file, debug, grid)
    attach_form(
        original_document=original_document,
        form=form_file,
        result_document=result_document,
    )

    os.remove(form_file)

    if debug:
        os.rename(result_document, form_file)
        field_ids = settings.form_field_ids(form_name)
        field_values = {field_id: field_id for field_id in field_ids}
        fill_form(
            input_pdf=form_file, field_values=field_values, output_pdf=result_document
        )


@click.command(name="create")
@click.option(
    "--debug",
    is_flag=True,
    help="Debug mode. Makes all inputs to be visible and contain IDs.",
)
@click.option(
    "--grid",
    is_flag=True,
    help="Add grid with coordinates to the form",
)
@click.argument("form_definitions", required=True, type=click.Path(exists=True))
@click.argument("form_name", required=True, type=str)
@click.argument(
    "form_file", required=False, type=click.Path(exists=False), default="form.pdf"
)
@click.help_option("--help", "-h", help="Show this message and exit.")
def create(form_definitions, form_name, form_file, debug, grid):
    """Create an empty PDF form form form definitions file.

    This file can then be merged with another existing PDF with text to get fillable PDF file.
    """
    settings = FormSettings.from_file(form_definitions)

    grid_settings = DefaultGridSettings if grid else None
    create_form(settings, form_name, form_file, debug, grid_settings)


@click.command(name="attach")
@click.option(
    "--debug",
    is_flag=True,
    help="Debug mode. Makes all inputs to be visible and contain IDs.",
)
@click.option(
    "--grid",
    is_flag=True,
    help="Add grid with coordinates to the form",
)
@click.argument("form_definitions", required=True, type=click.Path(exists=True))
@click.argument("form_name", required=True)
@click.argument("original_document", required=True, type=click.Path(exists=True))
@click.argument("result_document", required=False, type=click.Path(exists=False))
@click.help_option("--help", "-h", help="Show this message and exit.")
def attach(
    form_definitions, form_name, original_document, result_document, debug, grid
):
    """Create and attach a PDF form to an existing document.

    This program takes a form definition file, creates a PDF form, and attaches it to
    an existing PDF document. The result is saved as a new PDF file.
    """
    if result_document is None:
        result_document = os.path.join(os.path.dirname(original_document), "result.pdf")

    form_settings = FormSettings.from_file(form_definitions)
    grid_settings = DefaultGridSettings if grid else None

    _add_form_to_file(
        settings=form_settings,
        form_name=form_name,
        original_document=original_document,
        result_document=result_document,
        debug=debug,
        grid=grid_settings,
    )


@click.command(name="field-ids")
@click.argument("form_definitions", required=True, type=click.Path(exists=True))
@click.argument("form_name", required=True)
def field_ids(form_definitions, form_name):
    """Print all field IDs mentioned in a form.
    """
    settings = FormSettings.from_file(form_definitions)
    field_ids = sorted(list(settings.form_field_ids(form_name)))
    for field_id in field_ids:
        print(field_id)
