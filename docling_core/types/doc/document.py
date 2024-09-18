from typing import Any, Dict, List, Optional, Tuple, Union

from pydantic import AnyUrl, BaseModel, Field

from docling_core.types.doc.base import BoundingBox, Size


class FigureData(BaseModel):  # TBD
    pass


class TableData(BaseModel):  # TBD
    pass


class RefItem(BaseModel):
    cref: str = Field(alias="$ref")

    def resolve(self, doc: "DoclingDocument"):
        _, path, index_str = self.cref.split("/")
        index = int(index_str)
        obj = doc.__getattribute__(path)[index]
        return obj


class ImageRef(BaseModel):
    format: str  # png, etc.
    dpi: int  # ...
    size: Size
    uri: AnyUrl


class ProvenanceItem(BaseModel):
    page_no: int
    bbox: BoundingBox
    charspan: Tuple[int, int]


class DocItem(BaseModel):
    dloc: str  # format spec ({document_hash}{json-path})
    hash: int
    label: str
    parent: Optional[RefItem]
    children: List[RefItem]
    prov: List[ProvenanceItem]


class TextItem(DocItem):
    orig: str  # untreated representation
    text: str  # sanitized representation


class FloatingItem(DocItem):
    caption: Optional[Union[RefItem, TextItem]]
    references: List[Union[RefItem, TextItem]]
    footnotes: List[Union[RefItem, TextItem]]
    data: Any
    image: Optional[ImageRef]


class FigureItem(DocItem):
    data: FigureData


class TableItem(DocItem):
    data: TableData


class KeyValueItem(DocItem):
    pass

ContentItem = Union[TextItem, FigureItem, TableItem, KeyValueItem]


class DocumentContent(BaseModel):
    furniture: List[RefItem] = []
    body: List[RefItem] = []
    texts: List[TextItem] = []
    figures: List[FigureItem] = []
    tables: List[TableItem] = []
    key_value_items: List[KeyValueItem] = []

class PageItem(DocumentContent):
    hash: str  # page hash
    size: Size
    image: Optional[ImageRef]
    num_elements: int


class DoclingDocument(DocumentContent):
    description: Any
    file_info: Any
    pages: Dict[int, PageItem] = {}  # empty as default
