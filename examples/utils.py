from pathlib import Path

from pydantic import AnyUrl

from docling_core.types.doc.document import (  # BoundingBox,
    DoclingDocument,
    Formatting,
    GraphCell,
    GraphData,
    GraphLink,
    TableCell,
    TableData,
)
from docling_core.types.doc.labels import (
    DocItemLabel,
    GraphCellLabel,
    GraphLinkLabel,
    GroupLabel,
)

def construct_test_doc() -> DoclingDocument:

    doc = DoclingDocument(name="Untitled 1")

    title = doc.add_title(
        text="Title of the Document"
    )  # can be done if such information is present, or ommitted.

    chapter1 = doc.add_group(
        label=GroupLabel.CHAPTER, name="Introduction"
    )  # can be done if such information is present, or ommitted.

    doc.add_heading(
        parent=chapter1,
        text="1. Introduction",
        level=1,
    )

    tab_caption = doc.add_text(
        label=DocItemLabel.CAPTION, text="This is the caption of table 1."
    )

    # Make some table cells
    table_cells = []
    table_cells.append(
        TableCell(
            row_span=2,
            start_row_offset_idx=0,
            end_row_offset_idx=2,
            start_col_offset_idx=0,
            end_col_offset_idx=1,
            text="Product",
        )
    )
    table_cells.append(
        TableCell(
            col_span=2,
            start_row_offset_idx=0,
            end_row_offset_idx=1,
            start_col_offset_idx=1,
            end_col_offset_idx=3,
            text="Years",
        )
    )
    table_cells.append(
        TableCell(
            start_row_offset_idx=1,
            end_row_offset_idx=2,
            start_col_offset_idx=1,
            end_col_offset_idx=2,
            text="2016",
        )
    )
    table_cells.append(
        TableCell(
            start_row_offset_idx=1,
            end_row_offset_idx=2,
            start_col_offset_idx=2,
            end_col_offset_idx=3,
            text="2017",
        )
    )
    table_cells.append(
        TableCell(
            start_row_offset_idx=2,
            end_row_offset_idx=3,
            start_col_offset_idx=0,
            end_col_offset_idx=1,
            text="Apple",
        )
    )
    table_cells.append(
        TableCell(
            start_row_offset_idx=2,
            end_row_offset_idx=3,
            start_col_offset_idx=1,
            end_col_offset_idx=2,
            text="49823",
        )
    )
    table_cells.append(
        TableCell(
            start_row_offset_idx=2,
            end_row_offset_idx=3,
            start_col_offset_idx=2,
            end_col_offset_idx=3,
            text="695944",
        )
    )
    table_data = TableData(num_rows=3, num_cols=3, table_cells=table_cells)
    doc.add_table(data=table_data, caption=tab_caption)

    g2 = doc.add_group(label=GroupLabel.LIST, parent=None)
    doc.add_list_item(text="item 1 of neighboring list", parent=g2)
    nli2 = doc.add_list_item(text="item 2 of neighboring list", parent=g2)

    g2_subgroup = doc.add_group(label=GroupLabel.LIST, parent=nli2)
    doc.add_list_item(text="item 1 of sub list", parent=g2_subgroup)

    inline1 = doc.add_group(label=GroupLabel.INLINE, parent=g2_subgroup)
    doc.add_text(
        label=DocItemLabel.PARAGRAPH,
        text="Here a code snippet:",
        parent=inline1,
    )
    doc.add_code(text="<p>Hello world</p>", parent=inline1)
    doc.add_text(
        label=DocItemLabel.PARAGRAPH, text="(to be displayed inline)", parent=inline1
    )

    inline2 = doc.add_group(label=GroupLabel.INLINE, parent=g2_subgroup)
    doc.add_text(
        label=DocItemLabel.PARAGRAPH,
        text="Here a formula:",
        parent=inline2,
    )
    doc.add_text(label=DocItemLabel.FORMULA, text="E=mc^2", parent=inline2)
    doc.add_text(
        label=DocItemLabel.PARAGRAPH, text="(to be displayed inline)", parent=inline2
    )

    doc.add_text(label=DocItemLabel.PARAGRAPH, text="Here a code block:", parent=None)
    doc.add_code(text='print("Hello world")', parent=None)

    doc.add_text(
        label=DocItemLabel.PARAGRAPH, text="Here a formula block:", parent=None
    )
    doc.add_text(label=DocItemLabel.FORMULA, text="E=mc^2", parent=None)

    graph = GraphData(
        cells=[
            GraphCell(
                label=GraphCellLabel.KEY,
                cell_id=0,
                text="number",
                orig="#",
            ),
            GraphCell(
                label=GraphCellLabel.VALUE,
                cell_id=1,
                text="1",
                orig="1",
            ),
        ],
        links=[
            GraphLink(
                label=GraphLinkLabel.TO_VALUE,
                source_cell_id=0,
                target_cell_id=1,
            ),
            GraphLink(label=GraphLinkLabel.TO_KEY, source_cell_id=1, target_cell_id=0),
        ],
    )

    doc.add_key_values(graph=graph)

    doc.add_form(graph=graph)

    # doc.add_text(label=DocItemLabel.PARAGRAPH, text="This should be escaped: <p>Hello world</p>", parent=None)

    inline_fmt = doc.add_group(label=GroupLabel.INLINE)
    doc.add_text(
        label=DocItemLabel.PARAGRAPH, text="Some formatting chops:", parent=inline_fmt
    )
    doc.add_text(
        label=DocItemLabel.PARAGRAPH,
        text="bold",
        parent=inline_fmt,
        formatting=Formatting(bold=True),
    )
    doc.add_text(
        label=DocItemLabel.PARAGRAPH,
        text="italic",
        parent=inline_fmt,
        formatting=Formatting(italic=True),
    )
    doc.add_text(
        label=DocItemLabel.PARAGRAPH,
        text="underline",
        parent=inline_fmt,
        formatting=Formatting(underline=True),
    )
    doc.add_text(
        label=DocItemLabel.PARAGRAPH,
        text="strikethrough",
        parent=inline_fmt,
        formatting=Formatting(strikethrough=True),
    )
    doc.add_text(
        label=DocItemLabel.PARAGRAPH,
        text="hyperlink",
        parent=inline_fmt,
        hyperlink=Path("."),
    )
    doc.add_text(label=DocItemLabel.PARAGRAPH, text="&", parent=inline_fmt)
    doc.add_text(
        label=DocItemLabel.PARAGRAPH,
        text="everything at the same time.",
        parent=inline_fmt,
        formatting=Formatting(
            bold=True,
            italic=True,
            underline=True,
            strikethrough=True,
        ),
        hyperlink=AnyUrl("https://github.com/DS4SD/docling"),
    )

    return doc
