from PIL import Image as PILImage

from docling_core.types.doc import DoclingDocument
from docling_core.types.doc.document import DocTagsDocument

pg_doctags = "Assistant: <doctag><page_header><loc_159><loc_60><loc_366><loc_66>Header</page_header><text><loc_109><loc_78><loc_393><loc_97>Hello World</text></doctag><end_of_utterance>"


def test_doctags_load():
    doc = DoclingDocument(name="Document")
    pg_image = PILImage.new("RGB", (500, 500), "white")

    doctags_doc = DocTagsDocument.from_doctags_and_image_pairs([pg_doctags], [pg_image])

    doc.load_from_doctags(doctags_doc)
    # print(doc.export_to_html())
