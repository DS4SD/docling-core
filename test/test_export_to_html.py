from docling_core.types.doc.base import ImageRefMode
from docling_core.types.doc.document import DoclingDocument

DOC_WITH_MISSING_PAGE_IMAGE = {
    "body": {
        "children": [
            {"$ref": "#/texts/0"},
            {"$ref": "#/texts/1"},
        ],
        "content_layer": "body",
        "label": "unspecified",
        "name": "_root_",
        "self_ref": "#/body",
    },
    "form_items": [],
    "furniture": {
        "children": [],
        "content_layer": "furniture",
        "label": "unspecified",
        "name": "_root_",
        "self_ref": "#/furniture",
    },
    "groups": [],
    "key_value_items": [],
    "name": "2c3eaa76397e355e5132f2bee230936180583d132d3b4c28149c34e83fb87c23",
    "origin": {
        "binary_hash": 17809064254031518961,
        "filename": "2c3eaa76397e355e5132f2bee230936180583d132d3b4c28149c34e83fb87c23",
        "mimetype": "application/pdf",
    },
    "pages": {"1": {"page_no": 1, "size": {"height": 1754.0, "width": 1241.0}}},
    "pictures": [],
    "schema_name": "DoclingDocument",
    "tables": [],
    "texts": [
        {
            "children": [],
            "content_layer": "body",
            "label": "text",
            "orig": "Avec la même démarche que celle suivie pour la "
            "description de lamplification de type Doherty on notera "
            "les quantités de Fourier suivantes pour la fréquence "
            "fondamentale",
            "parent": {"$ref": "#/body"},
            "prov": [
                {
                    "bbox": {
                        "b": 985.3333129882812,
                        "coord_origin": "BOTTOMLEFT",
                        "l": 147.0,
                        "r": 1099.0,
                        "t": 1051.3333740234375,
                    },
                    "charspan": [0, 168],
                    "page_no": 1,
                }
            ],
            "self_ref": "#/texts/0",
            "text": "Avec la même démarche que celle suivie pour la "
            "description de lamplification de type Doherty on notera "
            "les quantités de Fourier suivantes pour la fréquence "
            "fondamentale",
        },
        {
            "children": [],
            "content_layer": "body",
            "label": "formula",
            "orig": "(II.24) 2 Imar",
            "parent": {"$ref": "#/body"},
            "prov": [
                {
                    "bbox": {
                        "b": 910.3333129882812,
                        "coord_origin": "BOTTOMLEFT",
                        "l": 624.3875122070312,
                        "r": 1098.0,
                        "t": 964.3186645507812,
                    },
                    "charspan": [0, 14],
                    "page_no": 1,
                }
            ],
            "self_ref": "#/texts/1",
            "text": "",
        },
    ],
    "version": "1.1.0",
}


def test_export_with_missing_page_image():
    doclingdoc = DoclingDocument.model_validate(DOC_WITH_MISSING_PAGE_IMAGE)
    actual = doclingdoc.export_to_html(
        image_mode=ImageRefMode.EMBEDDED,
    )
    expected = """<!DOCTYPE html>
<html lang="en">
<head>
    <link rel="icon" type="image/png"
    href="https://ds4sd.github.io/docling/assets/logo.png"/>
    <meta charset="UTF-8">
    <title>
    Powered by Docling
    </title>
    <style>
    html {
    background-color: LightGray;
    }
    body {
    margin: 0 auto;
    width:800px;
    padding: 30px;
    background-color: White;
    font-family: Arial, sans-serif;
    box-shadow: 10px 10px 10px grey;
    }
    figure{
    display: block;
    width: 100%;
    margin: 0px;
    margin-top: 10px;
    margin-bottom: 10px;
    }
    img {
    display: block;
    margin: auto;
    margin-top: 10px;
    margin-bottom: 10px;
    max-width: 640px;
    max-height: 640px;
    }
    table {
    min-width:500px;
    background-color: White;
    border-collapse: collapse;
    cell-padding: 5px;
    margin: auto;
    margin-top: 10px;
    margin-bottom: 10px;
    }
    th, td {
    border: 1px solid black;
    padding: 8px;
    }
    th {
    font-weight: bold;
    }
    table tr:nth-child(even) td{
    background-color: LightGray;
    }
    math annotation {
    display: none;
    }
    .formula-not-decoded {
    background: repeating-linear-gradient(
    45deg, /* Angle of the stripes */
    LightGray, /* First color */
    LightGray 10px, /* Length of the first color */
    White 10px, /* Second color */
    White 20px /* Length of the second color */
    );
    margin: 0;
    text-align: center;
    }
    </style>
    </head>
<p>Avec la même démarche que celle suivie pour la description de lamplification de type Doherty on notera les quantités de Fourier suivantes pour la fréquence fondamentale</p>
<div class="formula-not-decoded">Formula not decoded</div>
</html>"""
    assert actual == expected
