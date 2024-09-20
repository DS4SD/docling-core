import hashlib
import typing
from typing import Any, Dict, List, Optional, Tuple, Union

from pydantic import AnyUrl, BaseModel, ConfigDict, Field, computed_field

from docling_core.types.experimental.base import BoundingBox, Size

# Uint64 = conint(ge=0, le=(2**64 - 1))  # type: ignore[valid-type]
Uint64 = typing.Annotated[int, Field(ge=0, le=(2**64 - 1))]
LevelNumber = typing.Annotated[int, Field(ge=1, le=100)]


class BaseFigureData(BaseModel):  # TBD
    pass


class BaseTableData(BaseModel):  # TBD
    pass


class FileInfo(BaseModel):
    document_hash: str


class RefItem(BaseModel):
    cref: str = Field(alias="$ref")

    model_config = ConfigDict(
        populate_by_name=True,
    )

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


class NodeItem(BaseModel):
    dloc: str  # format spec ({document_hash}{json-path})
    parent: Optional[RefItem] = None
    children: List[RefItem] = []

    @computed_field  # type: ignore
    @property
    def hash(self) -> Uint64:  # TODO align with hasher on deepsearch-glm
        if not len(self.dloc):
            return 0
        hash_object = hashlib.sha256(self.dloc.encode("utf-8"))

        # Convert the hash to an integer
        hash_int = int.from_bytes(hash_object.digest(), "big")

        # Mask it to fit within 64 bits
        return Uint64(hash_int & 0xFFFFFFFFFFFFFFFF)  # 64-bit unsigned integer mask


class GroupItem(NodeItem):  # Container type, can't be a leaf node
    name: str


class DocItem(
    NodeItem
):  # Base type for any element that carries content, can be a leaf node
    label: str
    prov: List[ProvenanceItem] = []


class TextItem(DocItem):
    orig: str  # untreated representation
    text: str  # sanitized representation


class Section(TextItem):
    level: LevelNumber = 1


class FloatingItem(DocItem):
    caption: Optional[RefItem] = None
    references: List[RefItem] = []
    footnotes: List[RefItem] = []
    image: Optional[ImageRef] = None


class FigureItem(FloatingItem):
    data: BaseFigureData


class TableItem(FloatingItem):
    data: BaseTableData


class KeyValueItem(DocItem):
    pass


ContentItem = Union[TextItem, FigureItem, TableItem, KeyValueItem]


class DocumentContent(BaseModel):
    furniture: GroupItem = GroupItem(
        name="_root_", dloc="#/furniture"
    )  # List[RefItem] = []
    body: GroupItem = GroupItem(name="_root_", dloc="#/body")  # List[RefItem] = []
    groups: List[GroupItem] = []
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
    file_info: FileInfo
    pages: Dict[int, PageItem] = {}  # empty as default

    # def add_furniture_group(self, name: str):
    #    group = GroupItem(name=name)
    #    self.furniture.children.append(group)
    #    return group
    def resolve_cref(self, obj):
        path = obj.dloc.split("#")[1]
        return path

    def add_group(self, name: str, parent: Optional[GroupItem] = None) -> GroupItem:
        if not parent:
            parent = self.body
            parent_cref = "#/body"
        else:
            parent_cref = self.resolve_cref(parent)

        group_index = len(self.groups)
        cref = f"#/groups/{group_index}"
        dloc = f"{self.file_info.document_hash}{cref}"

        group = GroupItem(name=name, dloc=dloc, parent=RefItem(cref=parent_cref))
        self.groups.append(group)
        parent.children.append(RefItem(cref=cref))

        return group

    def add_paragraph(
        self,
        label: str,
        text: str,
        orig: Optional[str] = None,
        prov: Optional[ProvenanceItem] = None,
        parent: Optional[GroupItem] = None,
        item_cls=TextItem,
    ):
        if not parent:
            parent = self.body
            parent_cref = "#/body"
        else:
            parent_cref = self.resolve_cref(parent)

        if not orig:
            orig = text

        text_index = len(self.texts)
        cref = f"#/texts/{text_index}"
        dloc = f"{self.file_info.document_hash}{cref}"
        text_item = item_cls(
            label=label,
            text=text,
            orig=orig,
            dloc=dloc,
            parent=RefItem(cref=parent_cref),
        )
        if prov:
            text_item.prov.append(prov)

        self.texts.append(text_item)
        parent.children.append(RefItem(cref=cref))

        return text_item

    def add_table(
        self,
        data: BaseTableData,
        caption: Optional[RefItem] = None,
        prov: Optional[ProvenanceItem] = None,
        parent: Optional[GroupItem] = None,
    ):
        if not parent:
            parent = self.body

        table_index = len(self.tables)
        cref = f"#/tables/{table_index}"
        dloc = f"{self.file_info.document_hash}{cref}"

        tbl_item = TableItem(label="table", data=data, dloc=dloc, parent=parent)
        if prov:
            tbl_item.prov.append(prov)
        if caption:
            tbl_item.caption = caption

        self.tables.append(tbl_item)
        parent.children.append(RefItem(cref=cref))

        return tbl_item

    def add_figure(
        self,
        data: BaseFigureData,
        caption: Optional[RefItem] = None,
        prov: Optional[ProvenanceItem] = None,
        parent: Optional[GroupItem] = None,
    ):
        if not parent:
            parent = self.body

        figure_index = len(self.figures)
        cref = f"#/figures/{figure_index}"
        dloc = f"{self.file_info.document_hash}{cref}"

        fig_item = FigureItem(label="figure", data=data, dloc=dloc, parent=parent)
        if prov:
            fig_item.prov.append(prov)
        if caption:
            fig_item.caption = caption

        self.figures.append(fig_item)
        parent.children.append(RefItem(cref=cref))

        return fig_item

    def add_heading(
        self,
        label: str,
        text: str,
        orig: Optional[str] = None,
        level: LevelNumber = 1,
        prov: Optional[ProvenanceItem] = None,
        parent: Optional[GroupItem] = None,
    ):
        item: Section = self.add_paragraph(
            label, text, orig, prov, parent, item_cls=Section
        )
        item.level = level
        return item
