import hashlib
import typing
from typing import Any, Dict, List, Optional, Tuple, Union

import pandas as pd
from pydantic import (
    AnyUrl,
    BaseModel,
    ConfigDict,
    Field,
    computed_field,
    model_validator,
)
from tabulate import tabulate

from docling_core.types.doc.tokens import DocumentToken
from docling_core.types.experimental.base import BoundingBox, Size

Uint64 = typing.Annotated[int, Field(ge=0, le=(2**64 - 1))]
LevelNumber = typing.Annotated[int, Field(ge=1, le=100)]


class BaseFigureData(BaseModel):  # TBD
    pass


class TableCell(BaseModel):
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
        if isinstance(data, Dict):
            if not "bbox" in data or data["bbox"] == None:
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
    table_cells: List[TableCell] = []
    num_rows: int = 0
    num_cols: int = 0

    @computed_field  # type: ignore
    @property
    def grid(
        self,
    ) -> List[
        List[TableCell]
    ]:  # TODO compute grid representation on the fly from table_cells

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


class FileInfo(BaseModel):
    document_hash: str


class RefItem(BaseModel):
    cref: str = Field(alias="$ref")

    # This method makes RefItem compatible with DocItem
    def get_ref(self):
        return self

    model_config = ConfigDict(
        populate_by_name=True,
    )

    def resolve(self, doc: "DoclingDocument"):
        path_components = self.cref.split("/")
        if len(path_components) > 2:
            _, path, index_str = path_components
        else:
            _, path = path_components
            index_str = None

        if index_str:
            index = int(index_str)
            obj = doc.__getattribute__(path)[index]
        else:
            obj = doc.__getattribute__(path)

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

    def get_ref(self):
        return RefItem(cref=f"#{self.dloc.split('#')[1]}")

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

    def get_location_tokens(
        self,
        new_line: str,
        page_w: float,
        page_h: float,
        xsize: int = 100,
        ysize: int = 100,
        add_page_index: bool = True,
    ) -> str:
        """Get the location string for the BaseCell."""
        if not len(self.prov):
            return ""

        location = ""
        for prov in self.prov:

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
    orig: str  # untreated representation
    text: str  # sanitized representation

    def export_to_document_tokens(
        self,
        new_line: str = "\n",
        page_w: float = 0.0,
        page_h: float = 0.0,
        xsize: int = 100,
        ysize: int = 100,
        add_location: bool = True,
        add_content: bool = True,
        add_page_index: bool = True,
    ):
        """Export text element to document tokens format."""
        body = f"<{self.label}>"
        # body = f"<{self.name}>"

        assert DocumentToken.is_known_token(
            body
        ), f"failed DocumentToken.is_known_token({body})"

        if add_location:
            body += self.get_location_tokens(
                new_line="",
                page_w=page_w,
                page_h=page_h,
                xsize=xsize,
                ysize=ysize,
                add_page_index=add_page_index,
            )

        if add_content and self.text is not None:
            body += self.text.strip()

        body += f"</{self.label}>{new_line}"

        return body


class Section(TextItem):
    level: LevelNumber = 1


class FloatingItem(DocItem):
    captions: List[RefItem] = []
    references: List[RefItem] = []
    footnotes: List[RefItem] = []
    image: Optional[ImageRef] = None


class FigureItem(FloatingItem):
    data: BaseFigureData

    def export_to_document_tokens(
        self,
        doc: "DoclingDocument",
        new_line: str = "\n",
        page_w: float = 0.0,
        page_h: float = 0.0,
        xsize: int = 100,
        ysize: int = 100,
        add_location: bool = True,
        add_caption: bool = True,
        add_content: bool = True,  # not used at the moment
        add_page_index: bool = True,
    ):
        """Export figure to document tokens format."""
        body = f"{DocumentToken.BEG_FIGURE.value}{new_line}"

        if add_location:
            body += self.get_location_tokens(
                new_line=new_line,
                page_w=page_w,
                page_h=page_h,
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
    data: BaseTableData

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

                rowspan, rowstart, rowend = (
                    cell.row_span,
                    cell.start_row_offset_idx,
                    cell.end_row_offset_idx,
                )
                colspan, colstart, colend = (
                    cell.col_span,
                    cell.start_col_offset_idx,
                    cell.end_col_offset_idx,
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
        page_w: float = 0.0,
        page_h: float = 0.0,
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
        """Export table to document tokens format."""
        body = f"{DocumentToken.BEG_TABLE.value}{new_line}"

        if add_location:
            body += self.get_location_tokens(
                new_line=new_line,
                page_w=page_w,
                page_h=page_h,
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
                        and self.prov is not None
                        and len(self.prov) > 0
                    ):
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
                    ):
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
                        cell_label = f"<{'col_header' if col.column_header else 'row_header' if col.row_header else 'row_section' if col.row_section else 'body'}>"

                    body += f"<col_{j}>{cell_loc}{cell_label}{text}</col_{j}>"

                body += f"</row_{i}>{new_line}"

        body += f"{DocumentToken.END_TABLE.value}{new_line}"

        return body


class KeyValueItem(DocItem):
    pass


ContentItem = Union[TextItem, FigureItem, TableItem, KeyValueItem]


class DocumentTrees(BaseModel):
    furniture: GroupItem = GroupItem(
        name="_root_", dloc="#/furniture"
    )  # List[RefItem] = []
    body: GroupItem = GroupItem(name="_root_", dloc="#/body")  # List[RefItem] = []


class PageItem(DocumentTrees):
    # A page carries separate root items for furniture and body, only referencing items on the page
    hash: str  # page hash
    size: Size
    image: Optional[ImageRef]
    num_elements: int
    page_no: int


class DoclingDocument(DocumentTrees):
    version: str = "0.0.1"  # = SemanticVersion(version="0.0.1")
    description: Any
    file_info: FileInfo

    groups: List[GroupItem] = []
    texts: List[TextItem] = []
    figures: List[FigureItem] = []
    tables: List[TableItem] = []
    key_value_items: List[KeyValueItem] = []

    pages: Dict[int, PageItem] = {}  # empty as default

    # def add_furniture_group(self, name: str):
    #    group = GroupItem(name=name)
    #    self.furniture.children.append(group)
    #    return group

    def add_group(self, name: str, parent: Optional[GroupItem] = None) -> GroupItem:
        if not parent:
            parent = self.body

        group_index = len(self.groups)
        cref = f"#/groups/{group_index}"
        dloc = f"{self.file_info.document_hash}{cref}"

        group = GroupItem(name=name, dloc=dloc, parent=parent.get_ref())
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
        if not parent:
            parent = self.body

        table_index = len(self.tables)
        cref = f"#/tables/{table_index}"
        dloc = f"{self.file_info.document_hash}{cref}"

        tbl_item = TableItem(
            label="table", data=data, dloc=dloc, parent=parent.get_ref()
        )
        if prov:
            tbl_item.prov.append(prov)
        if caption:
            tbl_item.captions.append(caption.get_ref())

        self.tables.append(tbl_item)
        parent.children.append(RefItem(cref=cref))

        return tbl_item

    def add_figure(
        self,
        data: BaseFigureData,
        caption: Optional[Union[TextItem, RefItem]] = None,
        prov: Optional[ProvenanceItem] = None,
        parent: Optional[GroupItem] = None,
    ):
        if not parent:
            parent = self.body

        figure_index = len(self.figures)
        cref = f"#/figures/{figure_index}"
        dloc = f"{self.file_info.document_hash}{cref}"

        fig_item = FigureItem(
            label="figure", data=data, dloc=dloc, parent=parent.get_ref()
        )
        if prov:
            fig_item.prov.append(prov)
        if caption:
            fig_item.captions.append(caption.get_ref())

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

    def num_pages(self):
        return len(self.pages.values())

    def build_page_trees(self):
        # TODO: For every PageItem, update the furniture and body trees from the main doc.
        pass

    def iterate_elements(
        self,
        root: Optional[NodeItem] = None,
        omit_groups: bool = True,
        traverse_figures: bool = True,
    ) -> typing.Iterable[NodeItem]:
        # Yield the current node
        if not root:
            root = self.body

        if omit_groups and not isinstance(root, GroupItem):
            yield root

        # Traverse children
        for child_ref in root.children:
            child = child_ref.resolve(self)

            if isinstance(child, NodeItem):
                # If the child is a NodeItem, recursively traverse it
                if not isinstance(child, FigureItem) or traverse_figures:
                    yield from self.iterate_elements(child)
            else:  # leaf
                yield child

    def export_to_markdown(
        self,
        delim: str = "\n\n",
        from_element: int = 0,
        to_element: Optional[int] = None,
        labels: list[str] = [
            "title",
            "subtitle-level-1",
            "paragraph",
            "caption",
            "table",
            "Text",
            "text",
        ],
        strict_text: bool = False,
    ) -> str:
        r"""Serialize to Markdown.

        Operates on a slice of the document's main_text as defined through arguments
        main_text_start and main_text_stop; defaulting to the whole main_text.

        Args:
            delim (str, optional): Delimiter to use when concatenating the various
                Markdown parts. Defaults to "\n\n".
            from_element (int, optional): Body slicing start index (inclusive).
                Defaults to 0.
            to_element (Optional[int], optional): Body slicing stop index
                (exclusive). Defaults to None.

        Returns:
            str: The exported Markdown representation.
        """
        has_title = False
        prev_text = ""
        md_texts: list[str] = []

        skip_count = 0
        if len(self.body.children):
            for ix, item in enumerate(self.iterate_elements(self.body)):
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
        labels: list[str] = [
            "title",
            "subtitle-level-1",
            "paragraph",
            "caption",
            "table",
            "figure",
            "text",
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

        Returns:
            str: The content of the document formatted as a DocTags string.
        """
        new_line = ""
        if delim:
            new_line = "\n"

        doctags = f"{DocumentToken.BEG_DOCUMENT.value}{new_line}"

        # pagedims = self.get_map_to_page_dimensions()

        skip_count = 0
        if len(self.body.children):
            for ix, item in enumerate(self.iterate_elements(self.body)):

                if skip_count < from_element:
                    skip_count += 1
                    continue  # skip as many items as you want

                if to_element and ix >= to_element:
                    break

                prov = item.prov

                page_i = -1
                page_w = 0.0
                page_h = 0.0

                if add_location and len(self.pages) and len(prov) > 0:

                    page_i = prov[0].page
                    page_dim = self.pages[page_i - 1].size

                    page_w = float(page_dim.width)
                    page_h = float(page_dim.height)

                item_type = item.label
                if isinstance(item, TextItem) and (item_type in labels):

                    doctags += item.export_to_document_tokens(
                        new_line=new_line,
                        page_w=page_w,
                        page_h=page_h,
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
                        page_w=page_w,
                        page_h=page_h,
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

                elif isinstance(item, FigureItem) and (item_type in labels):

                    doctags += item.export_to_document_tokens(
                        doc=self,
                        new_line=new_line,
                        page_w=page_w,
                        page_h=page_h,
                        xsize=xsize,
                        ysize=ysize,
                        add_caption=True,
                        add_location=add_location,
                        add_content=add_content,
                        add_page_index=add_page_index,
                    )

        doctags += DocumentToken.END_DOCUMENT.value

        return doctags
