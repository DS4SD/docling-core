import yaml

from docling_core.types.experimental.document import (
    BasePictureData,
    BaseTableData,
    DescriptionItem,
    DoclingDocument,
    TableCell,
    DocItem,
    TextItem,
)
from docling_core.types.experimental.labels import DocItemLabel, GroupLabel


def test_reference_doc():
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

    for item, level in doc.iterate_elements():
        print(f"Item: {item} at level {level}")


def test_parse_doc():
    with open(
        "test/data/experimental/2206.01062.experimental.yaml",
        "r",
    ) as fp:
        dict_from_yaml = yaml.safe_load(fp)

    doc = DoclingDocument.model_validate(dict_from_yaml)

    _test_export_methods(doc)
    _test_serialize_and_reload(doc)


def test_construct_doc():

    doc = _construct_doc()
    _test_export_methods(doc)
    _test_serialize_and_reload(doc)


def _test_serialize_and_reload(doc):
    ### Serialize and deserialize stuff
    yaml_dump = yaml.safe_dump(doc.model_dump(mode="json", by_alias=True))
    # print(f"\n\n{yaml_dump}")
    DoclingDocument.model_validate(yaml.safe_load(yaml_dump))


def _test_export_methods(doc):
    ### Iterate all elements
    doc.print_element_tree()
    ## Export stuff
    doc.export_to_markdown()
    doc.export_to_document_tokens()
    for table in doc.tables:
        table.export_to_html()
        table.export_to_dataframe()
        table.export_to_document_tokens(doc)
    for fig in doc.pictures:
        fig.export_to_document_tokens(doc)


def _construct_doc() -> DoclingDocument:
    doc = DoclingDocument(description=DescriptionItem(), name="Untitled 1")
    # group, heading, paragraph, table, figure, title, list, provenance
    doc.add_paragraph(label=DocItemLabel.TEXT, text="Author 1\nAffiliation 1")
    doc.add_paragraph(label=DocItemLabel.TEXT, text="Author 2\nAffiliation 2")

    chapter1 = doc.add_group(
        label=GroupLabel.CHAPTER, name="Introduction"
    )  # can be done if such information is present, or ommitted.

    doc.add_heading(
        parent=chapter1,
        text="1. Introduction",
        level=1,
    )
    doc.add_paragraph(
        parent=chapter1,
        label=DocItemLabel.TEXT,
        text="This paper introduces the biggest invention ever made. ...",
    )
    mylist = doc.add_group(parent=chapter1, label=GroupLabel.LIST)
    doc.add_paragraph(
        parent=mylist,
        label=DocItemLabel.LIST_ITEM,
        text="Cooks your favourite meal before you know you want it.",
    )
    doc.add_paragraph(
        parent=mylist, label=DocItemLabel.LIST_ITEM, text="Cleans up all your dishes."
    )
    doc.add_paragraph(
        parent=mylist,
        label=DocItemLabel.LIST_ITEM,
        text="Drains your bank account without consent.",
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
    table_el = BaseTableData(num_rows=3, num_cols=3, table_cells=table_cells)
    doc.add_table(data=table_el)

    fig_caption = doc.add_paragraph(
        label=DocItemLabel.CAPTION, text="This is the caption of figure 1."
    )
    fig_item = doc.add_picture(data=BasePictureData(), caption=fig_caption)

    return doc
    
def test_docitems():

    # Iterate over the derived classes of the BaseClass
    derived_classes = DocItem.__subclasses__()
    for dc in derived_classes:

        if issubclass(dc, TextItem):
            _ = dc(text="whatever", orig="whatever", dloc="sdvsd", label=DocItemLabel.TEXT)
            yaml_dump = yaml.safe_dump(_.model_dump(mode="json", by_alias=True))
            print(f"\n\n{yaml_dump}")
        else:            
            try:
                _ = dc()            
                yaml_dump = yaml.safe_dump(_.model_dump(mode="json", by_alias=True))
                
                print(f"\n\n{yaml_dump}")        
            except TypeError as e:
                print(f"Could not instantiate {dc.__name__}: {e}")
            except Exception as e:
                print(f"Could not instantiate {dc.__name__}: {e}")            
         
