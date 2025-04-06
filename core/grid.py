from dataclasses import dataclass
from typing import Optional

import reportlab.lib.colors as colors
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm


@dataclass
class GridLineSettings:
    width: float
    color: colors.Color


@dataclass
class GridStep:
    horizontal: float
    vertical: float


@dataclass
class GridSettings:
    main_line: GridLineSettings
    main_step: GridStep
    sub_line: GridLineSettings
    sub_step: GridStep
    show_labels: bool = True
    margin: tuple[float, float] = (10 * mm, 10 * mm)
    font_size: float = 8


DefaultGridSettings = GridSettings(
    main_line=GridLineSettings(width=0.5, color=colors.Color(0, 0, 1, alpha=0.3)),
    main_step=GridStep(horizontal=10 * mm, vertical=10 * mm),
    sub_line=GridLineSettings(width=0.2, color=colors.Color(0, 0, 1, alpha=0.1)),
    sub_step=GridStep(horizontal=2 * mm, vertical=2 * mm),
)


def draw_grid(
    c: canvas.Canvas,
    settings: GridSettings,
    page: tuple[float, float] = A4,
) -> None:
    page_width = page[0]
    page_height = page[1]
    margin_horizontal = settings.margin[0]
    margin_vertical = settings.margin[1]
    show_labels = settings.show_labels
    font_size = settings.font_size

    # Draw sub grid lines
    c.setStrokeColor(settings.sub_line.color)
    c.setLineWidth(settings.sub_line.width)

    # Draw vertical sub lines
    x = settings.main_step.horizontal
    while x < margin_horizontal:
        x += settings.sub_step.horizontal

    while x < page_width - margin_horizontal:
        c.line(x, margin_vertical, x, page_height - margin_vertical)
        x += settings.sub_step.horizontal

    # Draw horizontal sub lines
    y = settings.main_step.vertical
    while y < margin_vertical:
        y += settings.sub_step.vertical

    while y < page_height - margin_vertical:
        c.line(margin_horizontal, y, page_width - margin_horizontal, y)
        y += settings.sub_step.vertical

    # Draw main grid lines
    c.setStrokeColor(settings.main_line.color)
    c.setLineWidth(settings.main_line.width)

    # Draw vertical main lines with labels
    x = settings.main_step.horizontal
    while x < page_width - margin_horizontal:
        if show_labels:
            # Add label near the left end of the line
            c.setFont("Helvetica", font_size)
            c.drawString(x - 10, page_height - margin_vertical + 2, f"{(x/mm):05.1f}")
            c.drawString(x - 10, margin_vertical - font_size - 2, f"{(x/mm):05.1f}")

        c.line(x, margin_vertical, x, page_height - margin_vertical)
        x += settings.main_step.horizontal

    # Draw horizontal main lines with labels
    y = settings.main_step.vertical
    while y < page_height - margin_vertical:
        if show_labels:
            # Add label near the left end of the line
            c.setFont("Helvetica", font_size)
            c.drawString(margin_horizontal - font_size * mm, y - 3, f"{(y/mm):05.1f}")
            c.drawString(page_width - margin_horizontal + 2, y - 3, f"{(y/mm):05.1f}")

        c.line(margin_horizontal, y, page_width - margin_horizontal, y)
        y += settings.main_step.vertical
