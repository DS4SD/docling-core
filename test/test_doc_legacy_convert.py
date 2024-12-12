from pathlib import Path

import yaml

from docling_core.types.doc import DoclingDocument
from docling_core.types.doc.base import ImageRefMode
from docling_core.types.legacy_doc.document import ExportedCCSDocument as DsDocument
from docling_core.utils.legacy import (
    docling_document_to_legacy,
    legacy_to_docling_document,
)


def test_new_to_old():
    filename = "test/data/doc/2206.01062.yaml"

    with open(filename, "r") as fp:
        dict_from_yaml = yaml.safe_load(fp)

    doc = DoclingDocument.model_validate(dict_from_yaml)

    docling_document_to_legacy(doc)


def test_old_to_new():
    # filepath = Path("/Users/dol/Downloads/Santa%20Anna%2C%20Texas.es.json")
    # filepath = Path("/Users/dol/Downloads/NYSE_COTY_2023.es.json")
    # filepath = Path("/Users/dol/Downloads/Santa%20Anna%2C%20Texas.es.json")

    test_folder = Path("test/data/legacy_doc")
    for filepath in test_folder.glob("doc-*.json"):
        leg_doc = DsDocument.model_validate_json(filepath.read_text())

        doc = legacy_to_docling_document(leg_doc)

        # TODO: validate results

        doc.save_as_yaml(Path(filepath.with_suffix(".new.yaml").name))
        doc.save_as_markdown(Path(filepath.with_suffix(".new.md").name))
        doc.save_as_html(
            Path(filepath.with_suffix(".new.html").name),
            image_mode=ImageRefMode.EMBEDDED,
        )
