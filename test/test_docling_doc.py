import yaml
import pytest
from docling_core.types import DoclingDocument, BoundingBox
from docling_core.types.doc.document import ProvenanceItem


def test_load_serialize_doc():
    # Read YAML file
    with open("test/data/newdoc/dummy_doc.yaml", "r") as fp:
        dict_from_yaml = yaml.safe_load(fp)

    doc = DoclingDocument.model_validate(dict_from_yaml)

    # Objects can be accessed
    text_item = doc.texts[0]

    # access members
    text_item.text
    text_item.prov[0].page_no

    # Objects that are references need explicit resolution for now:
    obj = doc.body[2].resolve(doc=doc)  # Text item with parent
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

def test_construct_doc():
    doc = DoclingDocument(description={}, file_info={})

    # group, heading, paragraph, table, figure, title, list, provenance
    doc.add_title()
    doc.add_paragraph(text="Author 1\nAffiliation 1").add_provenance(ProvenanceItem(page_no=1, bbox=BoundingBox(t=12, l=5, r=230, b=40), charspan=(0,22)))
    doc.add_paragraph(text="Author 2\nAffiliation 2")

    chapter1 = doc.add_group(name="Introduction")
    chapter1.add_heading(text="1. Introduction", level=2)
    chapter1.add_paragraph(text="This paper introduces the biggest invention ever made. ...")
    mylist = chapter1.add_group()
    mylist.add_item(text="Cooks your favourite meal before you know you want it.")
    mylist.add_item(text="Cleans up all your dishes.")
    mylist.add_item(text="Drains your bank account without consent.")



    sec = doc.add_section(text="1. Introduction")

    list = sec.add_child(label="container")
    list.add_child()
    list.add_child()

