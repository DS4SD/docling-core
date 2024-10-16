#
# Copyright IBM Corp. 2024 - 2024
# SPDX-License-Identifier: MIT
#

"""Define base classes for chunking."""
from abc import ABC, abstractmethod
from typing import Any, Iterator

from pydantic import BaseModel

from docling_core.types.doc import DoclingDocument as DLDocument


class BaseChunk(BaseModel):
    """Data model for base chunk."""

    text: str
    meta: Any = None


class BaseChunker(BaseModel, ABC):
    """Base class for Chunker."""

    @abstractmethod
    def chunk(self, dl_doc: DLDocument, **kwargs) -> Iterator[BaseChunk]:
        """Chunk the provided document.

        Args:
            dl_doc (DLDocument): document to chunk

        Raises:
            NotImplementedError: in this abstract implementation

        Yields:
            Iterator[BaseChunk]: iterator over extracted chunks
        """
        raise NotImplementedError()
