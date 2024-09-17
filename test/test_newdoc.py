import yaml

from docling_core.types.newdoc.document import DoclingDocument

if __name__ == "__main__":
    # Read YAML file
    with open("data/newdoc/dummy_doc.yaml", "r") as fp:
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
