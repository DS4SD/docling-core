#
# Copyright IBM Corp. 2024 - 2024
# SPDX-License-Identifier: MIT
#

"""Chunker implementation leveraging the document structure."""

from __future__ import annotations

import logging
from typing import Any, ClassVar, Iterator, Optional

from pandas import DataFrame
from pydantic import BaseModel, Field, conlist

from docling_core.transforms.chunker import BaseChunker
from docling_core.transforms.chunker.base import BaseChunk
from docling_core.types.doc import DoclingDocument as DLDocument
from docling_core.types.doc.document import (
    DocItem,
    LevelNumber,
    ListItem,
    SectionHeaderItem,
    TableItem,
    TextItem,
)
from docling_core.types.doc.labels import DocItemLabel

_KEY_DOC_ITEMS = "doc_items"
_KEY_HEADINGS = "headings"
_KEY_CAPTIONS = "captions"

_logger = logging.getLogger(__name__)


class ChunkMeta(BaseModel):
    """Data model for specific chunk metadata."""

    # TODO align paths typewith _JSON_POINTER_REGEX
    doc_items: conlist(DocItem, min_length=1) = Field(  # type: ignore
        alias=_KEY_DOC_ITEMS,
    )
    headings: Optional[conlist(str, min_length=1)] = Field(  # type: ignore
        default=None,
        alias=_KEY_HEADINGS,
    )
    captions: Optional[conlist(str, min_length=1)] = Field(  # type: ignore
        default=None,
        alias=_KEY_CAPTIONS,
    )

    excluded_embed: ClassVar[list[str]] = [_KEY_DOC_ITEMS]
    excluded_llm: ClassVar[list[str]] = [_KEY_DOC_ITEMS]

    def export_json_dict(self) -> dict[str, Any]:
        """Helper method for exporting non-None keys to JSON mode.

        Returns:
            dict[str, Any]: The exported dictionary.
        """
        return self.model_dump(mode="json", by_alias=True, exclude_none=True)


class Chunk(BaseChunk):
    """Data model for specific chunk."""

    meta: ChunkMeta

    def export_json_dict(self) -> dict[str, Any]:
        """Helper method for exporting non-None keys to JSON mode.

        Returns:
            dict[str, Any]: The exported dictionary.
        """
        return self.model_dump(mode="json", by_alias=True, exclude_none=True)


class HierarchicalChunker(BaseChunker):
    """Chunker implementation leveraging the document layout."""

    merge_list_items: bool = True
    delim: str = "\n"

    @classmethod
    def _triplet_serialize(cls, table_df: DataFrame) -> str:

        # copy header as first row and shift all rows by one
        table_df.loc[-1] = table_df.columns  # type: ignore[call-overload]
        table_df.index = table_df.index + 1
        table_df = table_df.sort_index()

        rows = [item.strip() for item in table_df.iloc[:, 0].to_list()]
        cols = [item.strip() for item in table_df.iloc[0, :].to_list()]

        nrows = table_df.shape[0]
        ncols = table_df.shape[1]
        texts = [
            f"{rows[i]}, {cols[j]} = {str(table_df.iloc[i, j]).strip()}"
            for i in range(1, nrows)
            for j in range(1, ncols)
        ]
        output_text = ". ".join(texts)

        return output_text

    def chunk(self, dl_doc: DLDocument, **kwargs: Any) -> Iterator[BaseChunk]:
        r"""Chunk the provided document.

        Args:
            dl_doc (DLDocument): document to chunk

        Yields:
            Iterator[Chunk]: iterator over extracted chunks
        """
        heading_by_level: dict[LevelNumber, str] = {}
        list_items: list[TextItem] = []
        for item, level in dl_doc.iterate_items():
            captions = None
            if isinstance(item, DocItem):

                # first handle any merging needed
                if self.merge_list_items:
                    if isinstance(
                        item, ListItem
                    ) or (  # TODO remove when all captured as ListItem:
                        isinstance(item, TextItem)
                        and item.label == DocItemLabel.LIST_ITEM
                    ):
                        list_items.append(item)
                        continue
                    elif list_items:  # need to yield
                        yield Chunk(
                            text=self.delim.join([i.text for i in list_items]),
                            meta=ChunkMeta(
                                doc_items=list_items,
                                headings=[
                                    heading_by_level[k]
                                    for k in sorted(heading_by_level)
                                ]
                                or None,
                            ),
                        )
                        list_items = []  # reset

                if isinstance(
                    item, SectionHeaderItem
                ) or (  # TODO remove when all captured as SectionHeaderItem:
                    isinstance(item, TextItem)
                    and item.label == DocItemLabel.SECTION_HEADER
                ):
                    # TODO second branch not needed after cleanup above:
                    level = item.level if isinstance(item, SectionHeaderItem) else 1
                    heading_by_level[level] = item.text

                    # remove headings of higher level as they just went out of scope
                    keys_to_del = [k for k in heading_by_level if k > level]
                    for k in keys_to_del:
                        heading_by_level.pop(k, None)
                    continue

                if isinstance(item, TextItem) or (
                    (not self.merge_list_items) and isinstance(item, ListItem)
                ):
                    text = item.text
                elif isinstance(item, TableItem):
                    table_df = item.export_to_dataframe()
                    if table_df.shape[0] < 1 or table_df.shape[1] < 2:
                        # at least two cols needed, as first column contains row headers
                        continue
                    text = self._triplet_serialize(table_df=table_df)
                    captions = [
                        c.text for c in [r.resolve(dl_doc) for r in item.captions]
                    ] or None
                else:
                    continue
                c = Chunk(
                    text=text,
                    meta=ChunkMeta(
                        doc_items=[item],
                        headings=[heading_by_level[k] for k in sorted(heading_by_level)]
                        or None,
                        captions=captions,
                    ),
                )
                yield c

        if self.merge_list_items and list_items:  # need to yield
            yield Chunk(
                text=self.delim.join([i.text for i in list_items]),
                meta=ChunkMeta(
                    doc_items=list_items,
                    headings=[heading_by_level[k] for k in sorted(heading_by_level)]
                    or None,
                ),
            )
