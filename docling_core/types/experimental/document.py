"""Models for the Docling Document data type."""

import mimetypes
import re
import typing
from typing import Any, Dict, Final, List, Optional, Tuple, Union

import pandas as pd
from pydantic import (
    AnyUrl,
    BaseModel,
    ConfigDict,
    Field,
    StringConstraints,
    computed_field,
    field_validator,
    model_validator,
)
from tabulate import tabulate
from typing_extensions import Annotated

from docling_core.search.package import VERSION_PATTERN
from docling_core.types.base import _JSON_POINTER_REGEX
from docling_core.types.doc.tokens import DocumentToken
from docling_core.types.experimental import BoundingBox, Size
from docling_core.types.experimental.labels import DocItemLabel, GroupLabel

Uint64 = typing.Annotated[int, Field(ge=0, le=(2**64 - 1))]
LevelNumber = typing.Annotated[int, Field(ge=1, le=100)]
CURRENT_VERSION: Final = "1.0.0"


class BasePictureData(BaseModel):  # TBD
    """BasePictureData."""


class TableCell(BaseModel):
    """TableCell."""

    bbox: Optional[BoundingBox] = None
    row_span: int = 1
    col_span: int = 1
    start_row_offset_idx: int
    end_row_offset_idx: int
    start_col_offset_idx: int
    end_col_offset_idx: int
    text: str
    column_header: bool = False
    row_header: bool = False
    row_section: bool = False

    @model_validator(mode="before")
    @classmethod
    def from_dict_format(cls, data: Any) -> Any:
        """from_dict_format."""
        if isinstance(data, Dict):
            if "bbox" not in data or data["bbox"] is None:
                return data
            text = data["bbox"].get("token", "")
            if not len(text):
                text_cells = data.pop("text_cell_bboxes", None)
                if text_cells:
                    for el in text_cells:
                        text += el["token"] + " "

                text = text.strip()
            data["text"] = text

        return data


class BaseTableData(BaseModel):  # TBD
    """BaseTableData."""

    table_cells: List[TableCell] = []
    num_rows: int = 0
    num_cols: int = 0

    @computed_field  # type: ignore
    @property
    def grid(
        self,
    ) -> List[List[TableCell]]:
        """grid."""
        # Initialise empty table data grid (only empty cells)
        table_data = [
            [
                TableCell(
                    text="",
                    start_row_offset_idx=i,
                    end_row_offset_idx=i + 1,
                    start_col_offset_idx=j,
                    end_col_offset_idx=j + 1,
                )
                for j in range(self.num_cols)
            ]
            for i in range(self.num_rows)
        ]

        # Overwrite cells in table data for which there is actual cell content.
        for cell in self.table_cells:
            for i in range(
                min(cell.start_row_offset_idx, self.num_rows),
                min(cell.end_row_offset_idx, self.num_rows),
            ):
                for j in range(
                    min(cell.start_col_offset_idx, self.num_cols),
                    min(cell.end_col_offset_idx, self.num_cols),
                ):
                    table_data[i][j] = cell

        return table_data


class DocumentOrigin(BaseModel):
    """FileSource."""

    mimetype: str  # the mimetype of the original file
    binary_hash: Uint64  # the binary hash of the original file.
    # TODO: Change to be Uint64 and provide utility method to generate

    filename: str  # The name of the original file, including extension, without path.
    # Could stem from filesystem, source URI, Content-Disposition header, ...

    uri: Optional[AnyUrl] = (
        None  # any possible reference to a source file,
        # from any file handler protocol (e.g. https://, file://, s3://)
    )

    @field_validator("binary_hash", mode="before")
    @classmethod
    def parse_hex_string(cls, value):
        """parse_hex_string."""
        if isinstance(value, str):
            try:
                # Convert hex string to an integer
                hash_int = Uint64(value, 16)
                # Mask to fit within 64 bits (unsigned)
                return (
                    hash_int & 0xFFFFFFFFFFFFFFFF
                )  # TODO be sure it doesn't clip uint64 max
            except ValueError:
                raise ValueError(f"Invalid sha256 hexdigest: {value}")
        return value  # If already an int, return it as is.

    @field_validator("mimetype")
    @classmethod
    def validate_mimetype(cls, v):
        """validate_mimetype."""
        # Check if the provided MIME type is valid using mimetypes module
        if v not in mimetypes.types_map.values():
            raise ValueError(f"'{v}' is not a valid MIME type")
        return v


class RefItem(BaseModel):
    """RefItem."""

    cref: str = Field(alias="$ref", pattern=_JSON_POINTER_REGEX)

    # This method makes RefItem compatible with DocItem
    def get_ref(self):
        """get_ref."""
        return self

    model_config = ConfigDict(
        populate_by_name=True,
    )

    def resolve(self, doc: "DoclingDocument"):
        """resolve."""
        path_components = self.cref.split("/")
        if (num_comps := len(path_components)) == 3:
            _, path, index_str = path_components
            index = int(index_str)
            obj = doc.__getattribute__(path)[index]
        elif num_comps == 2:
            _, path = path_components
            obj = doc.__getattribute__(path)
        else:
            raise RuntimeError(f"Unsupported number of path components: {num_comps}")
        return obj


class ImageRef(BaseModel):
    """ImageRef."""

    mimetype: str
    dpi: int
    size: Size
    uri: AnyUrl

    @field_validator("mimetype")
    @classmethod
    def validate_mimetype(cls, v):
        """validate_mimetype."""
        # Check if the provided MIME type is valid using mimetypes module
        if v not in mimetypes.types_map.values():
            raise ValueError(f"'{v}' is not a valid MIME type")
        return v


class ProvenanceItem(BaseModel):
    """ProvenanceItem."""

    page_no: int
    bbox: BoundingBox
    charspan: Tuple[int, int]


class NodeItem(BaseModel):
    """NodeItem."""

    self_ref: str = Field(pattern=_JSON_POINTER_REGEX)
    parent: Optional[RefItem] = None
    children: List[RefItem] = []

    model_config = ConfigDict(extra="forbid")

    def get_ref(self):
        """get_ref."""
        return RefItem(cref=self.self_ref)


class GroupItem(NodeItem):  # Container type, can't be a leaf node
    """GroupItem."""

    name: str = (
        "group"  # Name of the group, e.g. "Introduction Chapter",
        # "Slide 5", "Navigation menu list", ...
    )
    label: GroupLabel = GroupLabel.UNSPECIFIED


class DocItem(
    NodeItem
):  # Base type for any element that carries content, can be a leaf node
    """DocItem."""

    label: DocItemLabel
    prov: List[ProvenanceItem] = []

    def get_location_tokens(
        self,
        doc: "DoclingDocument",
        new_line: str,
        xsize: int = 100,
        ysize: int = 100,
        add_page_index: bool = True,
    ) -> str:
        """Get the location string for the BaseCell."""
        if not len(self.prov):
            return ""

        location = ""
        for prov in self.prov:
            page_w, page_h = doc.pages[prov.page_no].size.as_tuple()

            page_i = -1
            if add_page_index:
                page_i = prov.page_no

            loc_str = DocumentToken.get_location(
                bbox=prov.bbox.to_bottom_left_origin(page_h).as_tuple(),
                page_w=page_w,
                page_h=page_h,
                xsize=xsize,
                ysize=ysize,
                page_i=page_i,
            )
            location += f"{loc_str}{new_line}"

        return location


class TextItem(DocItem):
    """TextItem."""

    orig: str  # untreated representation
    text: str  # sanitized representation

    def export_to_document_tokens(
        self,
        doc: "DoclingDocument",
        new_line: str = "\n",
        xsize: int = 100,
        ysize: int = 100,
        add_location: bool = True,
        add_content: bool = True,
        add_page_index: bool = True,
    ):
        r"""Export text element to document tokens format.

        :param doc: "DoclingDocument":
        :param new_line: str:  (Default value = "\n")
        :param xsize: int:  (Default value = 100)
        :param ysize: int:  (Default value = 100)
        :param add_location: bool:  (Default value = True)
        :param add_content: bool:  (Default value = True)
        :param add_page_index: bool:  (Default value = True)

        """
        body = f"<{self.label.value}>"

        # TODO: This must be done through an explicit mapping.
        # assert DocumentToken.is_known_token(
        #    body
        # ), f"failed DocumentToken.is_known_token({body})"

        if add_location:
            body += self.get_location_tokens(
                doc=doc,
                new_line="",
                xsize=xsize,
                ysize=ysize,
                add_page_index=add_page_index,
            )

        if add_content and self.text is not None:
            body += self.text.strip()

        body += f"</{self.label.value}>{new_line}"

        return body


class SectionHeaderItem(TextItem):
    """SectionItem."""

    label: typing.Literal[DocItemLabel.SECTION_HEADER] = DocItemLabel.SECTION_HEADER
    level: LevelNumber


class FloatingItem(DocItem):
    """FloatingItem."""

    captions: List[RefItem] = []
    references: List[RefItem] = []
    footnotes: List[RefItem] = []
    image: Optional[ImageRef] = None


class PictureItem(FloatingItem):
    """PictureItem."""

    label: typing.Literal[DocItemLabel.PICTURE] = DocItemLabel.PICTURE

    data: BasePictureData

    def export_to_document_tokens(
        self,
        doc: "DoclingDocument",
        new_line: str = "\n",
        xsize: int = 100,
        ysize: int = 100,
        add_location: bool = True,
        add_caption: bool = True,
        add_content: bool = True,  # not used at the moment
        add_page_index: bool = True,
    ):
        r"""Export picture to document tokens format.

        :param doc: "DoclingDocument":
        :param new_line: str:  (Default value = "\n")
        :param xsize: int:  (Default value = 100)
        :param ysize: int:  (Default value = 100)
        :param add_location: bool:  (Default value = True)
        :param add_caption: bool:  (Default value = True)
        :param add_content: bool:  (Default value = True)
        :param # not used at the momentadd_page_index: bool:  (Default value = True)

        """
        body = f"{DocumentToken.BEG_FIGURE.value}{new_line}"

        if add_location:
            body += self.get_location_tokens(
                doc=doc,
                new_line=new_line,
                xsize=xsize,
                ysize=ysize,
                add_page_index=add_page_index,
            )

        if add_caption and len(self.captions):
            text = ""
            for cap in self.captions:
                text += cap.resolve(doc).text

            if len(text):
                body += f"{DocumentToken.BEG_CAPTION.value}"
                body += f"{text.strip()}"
                body += f"{DocumentToken.END_CAPTION.value}"
                body += f"{new_line}"

        body += f"{DocumentToken.END_FIGURE.value}{new_line}"

        return body


class TableItem(FloatingItem):
    """TableItem."""

    data: BaseTableData
    label: typing.Literal[DocItemLabel.TABLE] = DocItemLabel.TABLE

    def export_to_dataframe(self) -> pd.DataFrame:
        """Export the table as a Pandas DataFrame."""
        if self.data is None or self.data.num_rows == 0 or self.data.num_cols == 0:
            return pd.DataFrame()

        # Count how many rows are column headers
        num_headers = 0
        for i, row in enumerate(self.data.grid):
            if len(row) == 0:
                raise RuntimeError(
                    f"Invalid table. {len(row)=} but {self.data.num_cols=}."
                )

            any_header = False
            for cell in row:
                if cell.column_header:
                    any_header = True
                    break

            if any_header:
                num_headers += 1
            else:
                break

        # Create the column names from all col_headers
        columns: Optional[List[str]] = None
        if num_headers > 0:
            columns = ["" for _ in range(self.data.num_cols)]
            for i in range(num_headers):
                for j, cell in enumerate(self.data.grid[i]):
                    col_name = cell.text
                    if columns[j] != "":
                        col_name = f".{col_name}"
                    columns[j] += col_name

        # Create table data
        table_data = [
            [cell.text for cell in row] for row in self.data.grid[num_headers:]
        ]

        # Create DataFrame
        df = pd.DataFrame(table_data, columns=columns)

        return df

    def export_to_html(self) -> str:
        """Export the table as html."""
        body = ""
        nrows = self.data.num_rows
        ncols = self.data.num_cols

        if not len(self.data.table_cells):
            return ""
        for i in range(nrows):
            body += "<tr>"
            for j in range(ncols):
                cell: TableCell = self.data.grid[i][j]

                rowspan, rowstart = (
                    cell.row_span,
                    cell.start_row_offset_idx,
                )
                colspan, colstart = (
                    cell.col_span,
                    cell.start_col_offset_idx,
                )

                if rowstart != i:
                    continue
                if colstart != j:
                    continue

                content = cell.text.strip()
                celltag = "td"
                if cell.column_header:
                    celltag = "th"

                opening_tag = f"{celltag}"
                if rowspan > 1:
                    opening_tag += f' rowspan="{rowspan}"'
                if colspan > 1:
                    opening_tag += f' colspan="{colspan}"'

                body += f"<{opening_tag}>{content}</{celltag}>"
            body += "</tr>"
        body = f"<table>{body}</table>"

        return body

    def export_to_document_tokens(
        self,
        doc: "DoclingDocument",
        new_line: str = "\n",
        xsize: int = 100,
        ysize: int = 100,
        add_location: bool = True,
        add_caption: bool = True,
        add_content: bool = True,
        add_cell_location: bool = True,
        add_cell_label: bool = True,
        add_cell_text: bool = True,
        add_page_index: bool = True,
    ):
        r"""Export table to document tokens format.

        :param doc: "DoclingDocument":
        :param new_line: str:  (Default value = "\n")
        :param xsize: int:  (Default value = 100)
        :param ysize: int:  (Default value = 100)
        :param add_location: bool:  (Default value = True)
        :param add_caption: bool:  (Default value = True)
        :param add_content: bool:  (Default value = True)
        :param add_cell_location: bool:  (Default value = True)
        :param add_cell_label: bool:  (Default value = True)
        :param add_cell_text: bool:  (Default value = True)
        :param add_page_index: bool:  (Default value = True)

        """
        body = f"{DocumentToken.BEG_TABLE.value}{new_line}"

        if add_location:
            body += self.get_location_tokens(
                doc=doc,
                new_line=new_line,
                xsize=xsize,
                ysize=ysize,
                add_page_index=add_page_index,
            )

        if add_caption and len(self.captions):
            text = ""
            for cap in self.captions:
                text += cap.resolve(doc).text

            if len(text):
                body += f"{DocumentToken.BEG_CAPTION.value}"
                body += f"{text.strip()}"
                body += f"{DocumentToken.END_CAPTION.value}"
                body += f"{new_line}"

        if add_content and len(self.data.table_cells) > 0:
            for i, row in enumerate(self.data.grid):
                body += f"<row_{i}>"
                for j, col in enumerate(row):

                    text = ""
                    if add_cell_text:
                        text = col.text.strip()

                    cell_loc = ""
                    if (
                        col.bbox is not None
                        and add_cell_location
                        and add_page_index
                        and len(self.prov) > 0
                    ):
                        page_w, page_h = doc.pages[self.prov[0].page_no].size.as_tuple()
                        cell_loc = DocumentToken.get_location(
                            bbox=col.bbox.to_bottom_left_origin(page_h).as_tuple(),
                            page_w=page_w,
                            page_h=page_h,
                            xsize=xsize,
                            ysize=ysize,
                            page_i=self.prov[0].page_no,
                        )
                    elif (
                        col.bbox is not None
                        and add_cell_location
                        and not add_page_index
                        and len(self.prov) > 0
                    ):
                        page_w, page_h = doc.pages[self.prov[0].page_no].size.as_tuple()

                        cell_loc = DocumentToken.get_location(
                            bbox=col.bbox.to_bottom_left_origin(page_h).as_tuple(),
                            page_w=page_w,
                            page_h=page_h,
                            xsize=xsize,
                            ysize=ysize,
                            page_i=-1,
                        )

                    cell_label = ""
                    if add_cell_label:
                        if col.column_header:
                            cell_label = "<col_header>"
                        elif col.row_header:
                            cell_label = "<row_header>"
                        elif col.row_section:
                            cell_label = "<row_section>"
                        else:
                            cell_label = "<body>"

                    body += f"<col_{j}>{cell_loc}{cell_label}{text}</col_{j}>"

                body += f"</row_{i}>{new_line}"

        body += f"{DocumentToken.END_TABLE.value}{new_line}"

        return body


class KeyValueItem(DocItem):
    """KeyValueItem."""


ContentItem = Union[TextItem, SectionHeaderItem, PictureItem, TableItem, KeyValueItem]


class PageItem(BaseModel):
    """PageItem."""

    # A page carries separate root items for furniture and body,
    # only referencing items on the page
    size: Size
    image: Optional[ImageRef] = None
    page_no: int


class DescriptionItem(BaseModel):
    """DescriptionItem."""


class DoclingDocument(BaseModel):
    """DoclingDocument."""

    schema_name: typing.Literal["DoclingDocument"] = "DoclingDocument"
    version: Annotated[str, StringConstraints(pattern=VERSION_PATTERN, strict=True)] = (
        CURRENT_VERSION
    )
    description: DescriptionItem
    name: str  # The working name of this document, without extensions
    # (could be taken from originating doc, or just "Untitled 1")
    origin: Optional[DocumentOrigin] = (
        None  # DoclingDocuments may specify an origin (converted to DoclingDocument).
        # This is optional, e.g. a DoclingDocument could also be entirely
        # generated from synthetic data.
    )

    furniture: GroupItem = GroupItem(
        name="_root_", self_ref="#/furniture"
    )  # List[RefItem] = []
    body: GroupItem = GroupItem(name="_root_", self_ref="#/body")  # List[RefItem] = []

    groups: List[GroupItem] = []
    texts: List[Union[SectionHeaderItem, TextItem]] = []
    pictures: List[PictureItem] = []
    tables: List[TableItem] = []
    key_value_items: List[KeyValueItem] = []

    pages: Dict[int, PageItem] = {}  # empty as default

    def add_group(
        self,
        label: Optional[GroupLabel] = None,
        name: Optional[str] = None,
        parent: Optional[GroupItem] = None,
    ) -> GroupItem:
        """add_group.

        :param label: Optional[GroupLabel]:  (Default value = None)
        :param name: Optional[str]:  (Default value = None)
        :param parent: Optional[GroupItem]:  (Default value = None)

        """
        if not parent:
            parent = self.body

        group_index = len(self.groups)
        cref = f"#/groups/{group_index}"

        group = GroupItem(self_ref=cref, parent=parent.get_ref())
        if name is not None:
            group.name = name
        if label is not None:
            group.label = label

        self.groups.append(group)
        parent.children.append(RefItem(cref=cref))

        return group

    def add_text(
        self,
        label: str,
        text: str,
        orig: Optional[str] = None,
        prov: Optional[ProvenanceItem] = None,
        parent: Optional[GroupItem] = None,
    ):
        """add_paragraph.

        :param label: str:
        :param text: str:
        :param orig: Optional[str]:  (Default value = None)
        :param prov: Optional[ProvenanceItem]:  (Default value = None)
        :param parent: Optional[GroupItem]:  (Default value = None)

        """
        if not parent:
            parent = self.body

        if not orig:
            orig = text

        text_index = len(self.texts)
        cref = f"#/texts/{text_index}"
        text_item = TextItem(
            label=label,
            text=text,
            orig=orig,
            self_ref=cref,
            parent=parent.get_ref(),
        )
        if prov:
            text_item.prov.append(prov)

        self.texts.append(text_item)
        parent.children.append(RefItem(cref=cref))

        return text_item

    def add_table(
        self,
        data: BaseTableData,
        caption: Optional[Union[TextItem, RefItem]] = None,  # This is not cool yet.
        prov: Optional[ProvenanceItem] = None,
        parent: Optional[GroupItem] = None,
    ):
        """add_table.

        :param data: BaseTableData:
        :param caption: Optional[Union[TextItem:
        :param RefItem]]:  (Default value = None)
        :param # This is not cool yet.prov: Optional[ProvenanceItem]
        :param parent: Optional[GroupItem]:  (Default value = None)

        """
        if not parent:
            parent = self.body

        table_index = len(self.tables)
        cref = f"#/tables/{table_index}"

        tbl_item = TableItem(
            label=DocItemLabel.TABLE, data=data, self_ref=cref, parent=parent.get_ref()
        )
        if prov:
            tbl_item.prov.append(prov)
        if caption:
            tbl_item.captions.append(caption.get_ref())

        self.tables.append(tbl_item)
        parent.children.append(RefItem(cref=cref))

        return tbl_item

    def add_picture(
        self,
        data: BasePictureData,
        caption: Optional[Union[TextItem, RefItem]] = None,
        prov: Optional[ProvenanceItem] = None,
        parent: Optional[GroupItem] = None,
    ):
        """add_picture.

        :param data: BasePictureData:
        :param caption: Optional[Union[TextItem:
        :param RefItem]]:  (Default value = None)
        :param prov: Optional[ProvenanceItem]:  (Default value = None)
        :param parent: Optional[GroupItem]:  (Default value = None)

        """
        if not parent:
            parent = self.body

        picture_index = len(self.pictures)
        cref = f"#/pictures/{picture_index}"

        fig_item = PictureItem(
            label=DocItemLabel.PICTURE,
            data=data,
            self_ref=cref,
            parent=parent.get_ref(),
        )
        if prov:
            fig_item.prov.append(prov)
        if caption:
            fig_item.captions.append(caption.get_ref())

        self.pictures.append(fig_item)
        parent.children.append(RefItem(cref=cref))

        return fig_item

    def add_heading(
        self,
        text: str,
        orig: Optional[str] = None,
        level: LevelNumber = 1,
        prov: Optional[ProvenanceItem] = None,
        parent: Optional[GroupItem] = None,
    ):
        """add_heading.

        :param label: DocItemLabel:
        :param text: str:
        :param orig: Optional[str]:  (Default value = None)
        :param level: LevelNumber:  (Default value = 1)
        :param prov: Optional[ProvenanceItem]:  (Default value = None)
        :param parent: Optional[GroupItem]:  (Default value = None)

        """
        if not parent:
            parent = self.body

        if not orig:
            orig = text

        text_index = len(self.texts)
        cref = f"#/texts/{text_index}"
        section_header_item = SectionHeaderItem(
            level=level,
            text=text,
            orig=orig,
            self_ref=cref,
            parent=parent.get_ref(),
        )
        if prov:
            section_header_item.prov.append(prov)

        self.texts.append(section_header_item)
        parent.children.append(RefItem(cref=cref))

        return section_header_item

    def num_pages(self):
        """num_pages."""
        return len(self.pages.values())

    def validate_tree(self, root) -> bool:
        """validate_tree."""
        res = []
        for child_ref in root.children:
            child = child_ref.resolve(self)
            if child.parent.resolve(self) != root:
                return False
            res.append(self.validate_tree(child))

        return all(res) or len(res) == 0

    def iterate_items(
        self,
        root: Optional[NodeItem] = None,
        with_groups: bool = False,
        traverse_pictures: bool = True,
        page_no: Optional[int] = None,
        _level: int = 0,  # fixed parameter, carries through the node nesting level
    ) -> typing.Iterable[Tuple[NodeItem, int]]:  # tuple of node and level
        """iterate_elements.

        :param root: Optional[NodeItem]:  (Default value = None)
        :param with_groups: bool:  (Default value = False)
        :param traverse_pictures: bool:  (Default value = True)
        :param page_no: Optional[int]:  (Default value = None)
        :param _level:  (Default value = 0)
        :param # fixed parameter:
        :param carries through the node nesting level:
        """
        if not root:
            root = self.body

        if not isinstance(root, GroupItem) or with_groups:
            if isinstance(root, DocItem):
                if page_no is not None:
                    for prov in root.prov:
                        if prov.page_no == page_no:
                            yield root, _level
                else:
                    yield root, _level
            else:
                yield root, _level

        # Traverse children
        for child_ref in root.children:
            child = child_ref.resolve(self)

            if isinstance(child, NodeItem):
                # If the child is a NodeItem, recursively traverse it
                if not isinstance(child, PictureItem) or traverse_pictures:
                    yield from self.iterate_items(
                        child, _level=_level + 1, with_groups=with_groups
                    )

    def print_element_tree(self):
        """print_element_tree."""
        for ix, (item, level) in enumerate(self.iterate_items(with_groups=True)):
            if isinstance(item, GroupItem):
                print(" " * level, f"{ix}: {item.label.value} with name={item.name}")
            elif isinstance(item, DocItem):
                print(" " * level, f"{ix}: {item.label.value}")

    def export_to_markdown(
        self,
        delim: str = "\n\n",
        from_element: int = 0,
        to_element: Optional[int] = None,
        labels: list[DocItemLabel] = [
            DocItemLabel.TITLE,
            DocItemLabel.SECTION_HEADER,
            DocItemLabel.PARAGRAPH,
            DocItemLabel.CAPTION,
            DocItemLabel.TABLE,
            DocItemLabel.TEXT,
        ],
        strict_text: bool = False,
    ) -> str:
        r"""Serialize to Markdown.

        Operates on a slice of the document's main_text as defined through arguments
        main_text_start and main_text_stop; defaulting to the whole main_text.

        :param delim: Delimiter to use when concatenating the various
                Markdown parts. Defaults to "\n\n".
        :type delim: str
        :param from_element: Body slicing start index (inclusive).
                Defaults to 0.
        :type from_element: int
        :param to_element: Body slicing stop index
                (exclusive). Defaults to None.
        :type to_element: Optional[int]
        :param delim: str:  (Default value = "\n\n")
        :param from_element: int:  (Default value = 0)
        :param to_element: Optional[int]:  (Default value = None)
        :param labels: list[DocItemLabel]
        :param "subtitle-level-1":
        :param "paragraph":
        :param "caption":
        :param "table":
        :param "Text":
        :param "text":
        :param ]:
        :param strict_text: bool:  (Default value = False)
        :returns: The exported Markdown representation.
        :rtype: str
        """
        has_title = False
        prev_text = ""
        md_texts: list[str] = []

        skip_count = 0
        for ix, (item, level) in enumerate(self.iterate_items(self.body)):
            if skip_count < from_element:
                skip_count += 1
                continue  # skip as many items as you want

            if to_element and ix >= to_element:
                break

            markdown_text = ""

            if isinstance(item, DocItem):
                item_type = item.label

                if isinstance(item, TextItem) and item_type in labels:
                    text = item.text

                    # ignore repeated text
                    if prev_text == text or text is None:
                        continue
                    else:
                        prev_text = text

                    # first title match
                    if item_type == "title" and not has_title:
                        if strict_text:
                            markdown_text = f"{text}"
                        else:
                            markdown_text = f"# {text}"
                        has_title = True

                    # secondary titles
                    elif item_type in {"title", "subtitle-level-1"} or (
                        has_title and item_type == "title"
                    ):
                        if strict_text:
                            markdown_text = f"{text}"
                        else:
                            markdown_text = f"## {text}"

                    # normal text
                    else:
                        markdown_text = text

                elif (
                    isinstance(item, TableItem)
                    and item.data
                    and item_type in labels
                    and not strict_text
                ):
                    table = []
                    for row in item.data.grid:
                        tmp = []
                        for col in row:
                            tmp.append(col.text)
                        table.append(tmp)

                    if len(table) > 1 and len(table[0]) > 0:
                        try:
                            md_table = tabulate(
                                table[1:], headers=table[0], tablefmt="github"
                            )
                        except ValueError:
                            md_table = tabulate(
                                table[1:],
                                headers=table[0],
                                tablefmt="github",
                                disable_numparse=True,
                            )

                        markdown_text = md_table

            if markdown_text:
                md_texts.append(markdown_text)

        result = delim.join(md_texts)
        return result

    def export_to_document_tokens(
        self,
        delim: str = "\n\n",
        from_element: int = 0,
        to_element: Optional[int] = None,
        labels: list[DocItemLabel] = [
            DocItemLabel.TITLE,
            DocItemLabel.SECTION_HEADER,
            DocItemLabel.PARAGRAPH,
            DocItemLabel.CAPTION,
            DocItemLabel.TABLE,
            DocItemLabel.TEXT,
        ],
        xsize: int = 100,
        ysize: int = 100,
        add_location: bool = True,
        add_content: bool = True,
        add_page_index: bool = True,
        # table specific flags
        add_table_cell_location: bool = False,
        add_table_cell_label: bool = True,
        add_table_cell_text: bool = True,
    ) -> str:
        r"""Exports the document content to an DocumentToken format.

        Operates on a slice of the document's body as defined through arguments
        from_element and to_element; defaulting to the whole main_text.

        :param delim: str:  (Default value = "\n\n")
        :param from_element: int:  (Default value = 0)
        :param to_element: Optional[int]:  (Default value = None)
        :param labels: list[DocItemLabel]
        :param xsize: int:  (Default value = 100)
        :param ysize: int:  (Default value = 100)
        :param add_location: bool:  (Default value = True)
        :param add_content: bool:  (Default value = True)
        :param add_page_index: bool:  (Default value = True)
        :param # table specific flagsadd_table_cell_location: bool
        :param add_table_cell_label: bool:  (Default value = True)
        :param add_table_cell_text: bool:  (Default value = True)
        :returns: The content of the document formatted as a DocTags string.
        :rtype: str
        """
        new_line = ""
        if delim:
            new_line = "\n"

        doctags = f"{DocumentToken.BEG_DOCUMENT.value}{new_line}"

        # pagedims = self.get_map_to_page_dimensions()

        skip_count = 0
        for ix, (item, level) in enumerate(self.iterate_items(self.body)):
            if skip_count < from_element:
                skip_count += 1
                continue  # skip as many items as you want

            if to_element and ix >= to_element:
                break

            if not isinstance(item, DocItem):
                continue

            prov = item.prov

            page_i = -1

            if add_location and len(self.pages) and len(prov) > 0:

                page_i = prov[0].page_no
                page_dim = self.pages[page_i].size

                float(page_dim.width)
                float(page_dim.height)

            item_type = item.label
            if isinstance(item, TextItem) and (item_type in labels):

                doctags += item.export_to_document_tokens(
                    doc=self,
                    new_line=new_line,
                    xsize=xsize,
                    ysize=ysize,
                    add_location=add_location,
                    add_content=add_content,
                    add_page_index=add_page_index,
                )

            elif isinstance(item, TableItem) and (item_type in labels):

                doctags += item.export_to_document_tokens(
                    doc=self,
                    new_line=new_line,
                    xsize=xsize,
                    ysize=ysize,
                    add_caption=True,
                    add_location=add_location,
                    add_content=add_content,
                    add_cell_location=add_table_cell_location,
                    add_cell_label=add_table_cell_label,
                    add_cell_text=add_table_cell_text,
                    add_page_index=add_page_index,
                )

            elif isinstance(item, PictureItem) and (item_type in labels):

                doctags += item.export_to_document_tokens(
                    doc=self,
                    new_line=new_line,
                    xsize=xsize,
                    ysize=ysize,
                    add_caption=True,
                    add_location=add_location,
                    add_content=add_content,
                    add_page_index=add_page_index,
                )

        doctags += DocumentToken.END_DOCUMENT.value

        return doctags

    def add_page(self, page_no: int, size: Size) -> PageItem:
        """add_page.

        :param page_no: int:
        :param size: Size:

        """
        pitem = PageItem(page_no=page_no, size=size)

        self.pages[page_no] = pitem
        return pitem

    @field_validator("version")
    @classmethod
    def check_version_is_compatible(cls, v: str) -> str:
        """Check if this document version is compatible with current version."""
        current_match = re.match(VERSION_PATTERN, CURRENT_VERSION)
        doc_match = re.match(VERSION_PATTERN, v)
        if (
            doc_match is None
            or current_match is None
            or doc_match["major"] != current_match["major"]
            or doc_match["minor"] > current_match["minor"]
        ):
            raise ValueError(
                f"incompatible version {v} with schema version {CURRENT_VERSION}"
            )
        else:
            return CURRENT_VERSION

    @model_validator(mode="after")  # type: ignore
    @classmethod
    def validate_document(cls, d: "DoclingDocument"):
        """validate_document."""
        if not d.validate_tree(d.body) or not d.validate_tree(d.furniture):
            raise ValueError("Document hierachy is inconsistent.")

        return d
