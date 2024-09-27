#
# Copyright IBM Corp. 2024 - 2024
# SPDX-License-Identifier: MIT
#

"""Define the main types."""

from docling_core.types.doc.base import (
    BaseCell,
    BaseText,
    BoundingBox,
    PageDimensions,
    PageReference,
    Prov,
    Ref,
    Table,
    TableCell,
)
from docling_core.types.doc.document import (
    CCSDocumentDescription as DocumentDescription,
)
from docling_core.types.doc.document import CCSFileInfoObject as FileInfoObject
from docling_core.types.doc.document import ExportedCCSDocument as Document
from docling_core.types.gen.generic import Generic
from docling_core.types.rec.record import Record

__all__ = [
    "BaseCell",
    "BaseText",
    "BoundingBox",
    "Document",
    "DocumentDescription",
    "FileInfoObject",
    "Generic",
    "PageDimensions",
    "PageReference",
    "Prov",
    "Record",
    "Ref",
    "Table",
    "TableCell",
]
