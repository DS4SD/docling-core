from PIL import Image as PILImage

from docling_core.types.doc import DoclingDocument

pg_doctags = "Assistant: <doctag><page_header><loc_159><loc_60><loc_366><loc_66>Header</page_header><text><loc_109><loc_78><loc_393><loc_97>Hello World</text></doctag><end_of_utterance>"


def test_doctags_load():
    doc = DoclingDocument(name="Document")
    pg_image = PILImage.new("RGB", (500, 500), "white")
    doc.load_from_document_tokens([pg_doctags], [pg_image])
    # assert ...
