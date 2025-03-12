#
# Copyright IBM Corp. 2024 - 2025
# SPDX-License-Identifier: MIT
#

"""Define base classes for serialization."""
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional, Union

from pydantic import AnyUrl, BaseModel

from docling_core.types.doc.document import (
    DOCUMENT_TOKENS_EXPORT_LABELS,
    DoclingDocument,
    FloatingItem,
    FormItem,
    InlineGroup,
    KeyValueItem,
    NodeItem,
    OrderedList,
    PictureItem,
    TableItem,
    TextItem,
    UnorderedList,
)

_DEFAULT_LABELS = DOCUMENT_TOKENS_EXPORT_LABELS


class SerializationResult(BaseModel):
    """SerializationResult."""

    text: str


class BaseTextSerializer(ABC):
    """Base class for text item serializers."""

    @abstractmethod
    def serialize(
        self,
        *,
        item: TextItem,
        doc_serializer: "BaseDocSerializer",
        doc: DoclingDocument,
        **kwargs,
    ) -> SerializationResult:
        """Serializes the passed item."""
        ...


class BaseTableSerializer(ABC):
    """Base class for table item serializers."""

    @abstractmethod
    def serialize(
        self,
        *,
        item: TableItem,
        doc_serializer: "BaseDocSerializer",
        doc: DoclingDocument,
        **kwargs,
    ) -> SerializationResult:
        """Serializes the passed item."""
        ...


class BasePictureSerializer(ABC):
    """Base class for picture item serializers."""

    @abstractmethod
    def serialize(
        self,
        *,
        item: PictureItem,
        doc_serializer: "BaseDocSerializer",
        doc: DoclingDocument,
        **kwargs,
    ) -> SerializationResult:
        """Serializes the passed item."""
        ...


class BaseKeyValueSerializer(ABC):
    """Base class for key value item serializers."""

    @abstractmethod
    def serialize(
        self,
        *,
        item: KeyValueItem,
        doc_serializer: "BaseDocSerializer",
        doc: DoclingDocument,
        **kwargs,
    ) -> SerializationResult:
        """Serializes the passed item."""
        ...


class BaseFormSerializer(ABC):
    """Base class for form item serializers."""

    @abstractmethod
    def serialize(
        self,
        *,
        item: FormItem,
        doc_serializer: "BaseDocSerializer",
        doc: DoclingDocument,
        **kwargs,
    ) -> SerializationResult:
        """Serializes the passed item."""
        ...


class BaseListSerializer(ABC):
    """Base class for list serializers."""

    @abstractmethod
    def serialize(
        self,
        *,
        item: Union[UnorderedList, OrderedList],
        doc_serializer: "BaseDocSerializer",
        doc: DoclingDocument,
        **kwargs,
    ) -> SerializationResult:
        """Serializes the passed item."""
        ...


class BaseInlineSerializer(ABC):
    """Base class for inline serializers."""

    @abstractmethod
    def serialize(
        self,
        *,
        item: InlineGroup,
        doc_serializer: "BaseDocSerializer",
        doc: DoclingDocument,
        **kwargs,
    ) -> SerializationResult:
        """Serializes the passed item."""
        ...


class BaseFallbackSerializer(ABC):
    """Base fallback class for item serializers."""

    @abstractmethod
    def serialize(
        self,
        *,
        item: NodeItem,
        doc_serializer: "BaseDocSerializer",
        doc: DoclingDocument,
        **kwargs,
    ) -> SerializationResult:
        """Serializes the passed item."""
        ...


class BaseDocSerializer(ABC):
    """Base class for document serializers."""

    @abstractmethod
    def serialize(self, **kwargs) -> SerializationResult:
        """Run the serialization."""
        ...

    @abstractmethod
    def serialize_bold(self, text: str, **kwargs) -> str:
        """Hook for bold formatting serialization."""
        ...

    @abstractmethod
    def serialize_italic(self, text: str, **kwargs) -> str:
        """Hook for italic formatting serialization."""
        ...

    @abstractmethod
    def serialize_underline(self, text: str, **kwargs) -> str:
        """Hook for underline formatting serialization."""
        ...

    @abstractmethod
    def serialize_strikethrough(self, text: str, **kwargs) -> str:
        """Hook for strikethrough formatting serialization."""
        ...

    @abstractmethod
    def serialize_hyperlink(
        self, text: str, hyperlink: Union[AnyUrl, Path], **kwargs
    ) -> str:
        """Hook for hyperlink serialization."""
        ...

    @abstractmethod
    def get_parts(
        self,
        node: Optional[NodeItem] = None,
        **kwargs,
    ) -> list[SerializationResult]:
        """Get the components to be combined for serializing this node."""
        ...

    @abstractmethod
    def post_process(
        self,
        text: str,
        **kwargs,
    ) -> str:
        """Apply some text post-processing steps."""
        ...

    @abstractmethod
    def serialize_captions(
        self,
        item: FloatingItem,
        **kwargs,
    ) -> SerializationResult:
        """Serialize the item's captions."""
        ...

    @abstractmethod
    def get_excluded_nodes(self) -> list[str]:
        """Get references to excluded items."""
        ...
