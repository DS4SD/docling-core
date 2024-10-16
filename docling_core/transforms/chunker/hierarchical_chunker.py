#
# Copyright IBM Corp. 2024 - 2024
# SPDX-License-Identifier: MIT
#

"""Chunker implementation leveraging the document structure."""

from __future__ import annotations

import logging
from typing import Any, ClassVar, Iterator, Optional

from pydantic import BaseModel, Field, conlist

from docling_core.transforms.chunker import BaseChunker
from docling_core.transforms.chunker.base import BaseChunk
from docling_core.types.doc import DoclingDocument as DLDocument
from docling_core.types.doc.document import (
    DocItem,
    LevelNumber,
    ListItem,
    SectionHeaderItem,
    TextItem,
)
from docling_core.types.doc.labels import DocItemLabel

_KEY_PATHS = "paths"
_KEY_PROVS = "provs"
_KEY_HEADINGS = "headings"

_KEY_DOC_ITEMS = "doc_items"

_logger = logging.getLogger(__name__)


class ChunkMeta(BaseModel):
    """Data model for specific chunk metadata."""

    # TODO align paths typewith _JSON_POINTER_REGEX
    doc_items: conlist(DocItem, min_length=1) = Field(  # type: ignore
        default=None,
        alias=_KEY_DOC_ITEMS,
    )
    headings: Optional[conlist(str, min_length=1)] = Field(  # type: ignore
        default=None,
        alias=_KEY_HEADINGS,
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

            if isinstance(item, DocItem):

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
                else:
                    continue  # TODO refine to ignore some cases & raise otherwise?
                c = Chunk(
                    text=text,
                    meta=ChunkMeta(
                        doc_items=[item],
                        headings=[heading_by_level[k] for k in sorted(heading_by_level)]
                        or None,
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
