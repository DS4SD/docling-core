#
# Copyright IBM Corp. 2024 - 2024
# SPDX-License-Identifier: MIT
#

"""Define the main types."""

from docling_core.types.legacy.base import BoundingBox as LegacyBoundingBox # noqa
from docling_core.types.legacy.base import Table  # noqa
from docling_core.types.legacy.base import TableCell  # noqa
from docling_core.types.legacy.base import (  # noqa
    BaseCell,
    BaseText,
    PageDimensions,
    PageReference,
    Prov,
    Ref,
)
from docling_core.types.legacy.document import (  # noqa
    CCSDocumentDescription as DocumentDescription,
)
from docling_core.types.legacy.document import CCSFileInfoObject as FileInfoObject  # noqa
from docling_core.types.legacy.document import ExportedCCSDocument as Document  # noqa
from docling_core.types.gen.generic import Generic  # noqa
from docling_core.types.rec.record import Record  # noqa

from docling_core.types.doc.document import DoclingDocument, DocItem, TextItem, FloatingItem, TableItem, FigureItem, TableData, FigureData, PageItem
from docling_core.types.doc.base import CoordOrigin, BoundingBox