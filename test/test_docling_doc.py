import yaml

from docling_core.types.experimental.document import (
    BaseFigureData,
    BaseTableData,
    DoclingDocument,
    FileInfo,
    TableCell,
)


def test_load_serialize_doc():
    # Read YAML file
    with open("test/data/experimental/dummy_doc.yaml", "r") as fp:
        dict_from_yaml = yaml.safe_load(fp)

    doc = DoclingDocument.model_validate(dict_from_yaml)

    # Objects can be accessed
    text_item = doc.texts[0]

    # access members
    text_item.text
    text_item.prov[0].page_no

    # Objects that are references need explicit resolution for now:
    obj = doc.texts[2]  # Text item with parent
    parent = obj.parent.resolve(doc=doc)  # it is a figure

    obj2 = parent.children[0].resolve(
        doc=doc
    )  # Child of figure must be the same as obj

    assert obj == obj2
    assert obj is obj2

    doc_dumped = doc.model_dump(mode="json", by_alias=True)
    out_yaml = yaml.safe_dump(doc_dumped)

    doc_reload = DoclingDocument.model_validate(yaml.safe_load(out_yaml))

    assert doc_reload == doc  # must be equal
    assert doc_reload is not doc  # can't be identical

    ### Iterate all elements

    for item in doc.iterate_elements():
        print(f"Item: {item}")


def test_construct_doc():

    doc = DoclingDocument(description={}, file_info=FileInfo(document_hash="xyz"))

    # group, heading, paragraph, table, figure, title, list, provenance
    doc.add_paragraph(label="text", text="Author 1\nAffiliation 1")
    doc.add_paragraph(label="text", text="Author 2\nAffiliation 2")

    chapter1 = doc.add_group(
        name="Introduction"
    )  # can be done if such information is present, or ommitted.
    doc.add_heading(
        parent=chapter1, label="section_header", text="1. Introduction", level=1
    )
    doc.add_paragraph(
        parent=chapter1,
        label="text",
        text="This paper introduces the biggest invention ever made. ...",
    )
    mylist = doc.add_group(parent=chapter1, name="whateverlist")
    doc.add_paragraph(
        parent=mylist,
        label="list_item",
        text="Cooks your favourite meal before you know you want it.",
    )
    doc.add_paragraph(
        parent=mylist, label="list_item", text="Cleans up all your dishes."
    )
    doc.add_paragraph(
        parent=mylist,
        label="list_item",
        text="Drains your bank account without consent.",
    )
    # Make some table cells
    table_cells = []
    table_cells.append(
        TableCell(
            row_span=2,
            start_row_offset_idx=0,
            end_row_offset_idx=1,
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
    table_el = BaseTableData(num_rows=3, num_cols=3, table_cells=table_cells)
    doc.add_table(data=table_el)

    fig_caption = doc.add_paragraph(
        label="caption", text="This is the caption of figure 1."
    )
    doc.add_figure(data=BaseFigureData(), caption=fig_caption.get_ref())

    ### Iterate all elements

    for item in doc.iterate_elements():
        print(f"Item: {item}")

    ### Serialize and deserialize stuff

    yaml_dump = yaml.safe_dump(doc.model_dump(mode="json", by_alias=True))

    # print(f"\n\n{yaml_dump}")

    DoclingDocument.model_validate(yaml.safe_load(yaml_dump))
