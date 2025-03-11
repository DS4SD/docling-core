#
# Copyright IBM Corp. 2024 - 2025
# SPDX-License-Identifier: MIT
#

"""Define base classes for serialization."""
import sys
from abc import ABC, abstractmethod
from functools import cached_property
from pathlib import Path
from typing import Optional, Union

from pydantic import AnyUrl, BaseModel, computed_field

from docling_core.types.doc.base import ImageRefMode
from docling_core.types.doc.document import (
    DEFAULT_CONTENT_LAYERS,
    DOCUMENT_TOKENS_EXPORT_LABELS,
    ContentLayer,
    DocItem,
    DoclingDocument,
    FloatingItem,
    Formatting,
    FormItem,
    InlineGroup,
    KeyValueItem,
    NodeItem,
    OrderedList,
    PictureClassificationData,
    PictureDescriptionData,
    PictureItem,
    PictureMoleculeData,
    TableItem,
    TextItem,
    UnorderedList,
)
from docling_core.types.doc.labels import DocItemLabel

_DEFAULT_LABELS = DOCUMENT_TOKENS_EXPORT_LABELS


class SerializationResult(BaseModel):
    """SerializationResult."""

    text: str


# class GroundedSerializationResult(BaseModel):
#     """GroundedSerializationResult."""

#     doc_items: List[DocItem]


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
        image_placeholder: str,
        image_mode: ImageRefMode,
        **kwargs,
    ) -> SerializationResult:
        """Serializes the passed item."""
        ...

    # helper function
    def _serialize_content(
        self,
        item: PictureItem,
        doc_serializer: "BaseDocSerializer",
        doc: DoclingDocument,
        separator: Optional[str] = None,
        visited: Optional[set[str]] = None,
        **kwargs,
    ) -> SerializationResult:
        parts = doc_serializer.get_parts(  # FIXME
            node=item,
            traverse_pictures=True,
            # list_level=list_level,
            # is_inline_scope=is_inline_scope,
            visited=visited,
        )
        text_res = (separator or " ").join([p.text for p in parts])
        # NOTE: we do no postprocessing since already done as needed
        return SerializationResult(text=text_res)

    # helper function
    def _serialize_annotations(
        self,
        item: PictureItem,
        doc_serializer: "BaseDocSerializer",
        doc: DoclingDocument,
        separator: Optional[str] = None,
        **kwargs,
    ) -> SerializationResult:
        text_parts: list[str] = []
        for annotation in item.annotations:
            if isinstance(annotation, PictureClassificationData):
                predicted_class = (
                    annotation.predicted_classes[0].class_name
                    if annotation.predicted_classes
                    else None
                )
                if predicted_class is not None:
                    text_parts.append(f"Picture type: {predicted_class}")
            elif isinstance(annotation, PictureMoleculeData):
                text_parts.append(f"SMILES: {annotation.smi}")
            elif isinstance(annotation, PictureDescriptionData):
                text_parts.append(f"Description: {annotation.text}")

        text_res = (separator or "\n").join(text_parts)
        text_res = doc_serializer.post_process(text=text_res)
        return SerializationResult(text=text_res)


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
        list_level: int,
        is_inline_scope: bool,
        visited: Optional[set[str]] = None,  # refs of visited items
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
        list_level: int,
        visited: Optional[set[str]] = None,  # refs of visited items
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


class BaseDocSerializer(BaseModel, ABC):
    """Base class for document serializers."""

    doc: DoclingDocument

    include_formatting: bool = True  # added here since applied on text globally
    include_hyperlinks: bool = True  # added here since applied on text globally
    image_placeholder: str = "<!-- image -->"  # TODO this is too type-specific
    image_mode: ImageRefMode = ImageRefMode.PLACEHOLDER

    # this filtering criteria are non-recursive;
    # e.g. if a list group node is outside the range and some of its children items are
    # within, they will be serialized
    start: int = 0
    stop: int = sys.maxsize
    labels: set[DocItemLabel] = _DEFAULT_LABELS
    layers: set[ContentLayer] = DEFAULT_CONTENT_LAYERS
    pages: Optional[set[int]] = None

    # @computed_field  # type: ignore
    # @cached_property
    # def text_serializer(self) -> BaseTextSerializer:
    #     """Text serializer property."""
    #     return self._create_text_serializer()

    # @computed_field  # type: ignore
    # @cached_property
    # def table_serializer(self) -> BaseTableSerializer:
    #     """Table serializer property."""
    #     return self._create_table_serializer()

    # @computed_field  # type: ignore
    # @cached_property
    # def picture_serializer(self) -> BasePictureSerializer:
    #     """Picture serializer property."""
    #     return self._create_picture_serializer()

    # @computed_field  # type: ignore
    # @cached_property
    # def key_value_serializer(self) -> BaseKeyValueSerializer:
    #     """Key value serializer property."""
    #     return self._create_key_value_serializer()

    # @computed_field  # type: ignore
    # @cached_property
    # def form_serializer(self) -> BaseFormSerializer:
    #     """Serializer property."""
    #     return self._create_form_serializer()

    # @computed_field  # type: ignore
    # @cached_property
    # def fallback_serializer(self) -> BaseFallbackSerializer:
    #     """Serializer property."""
    #     return self._create_fallback_serializer()

    # @computed_field  # type: ignore
    # @cached_property
    # def list_serializer(self) -> BaseListSerializer:
    #     """Serializer property."""
    #     return self._create_list_serializer()

    # @computed_field  # type: ignore
    # @cached_property
    # def inline_serializer(self) -> BaseInlineSerializer:
    #     """Serializer property."""
    #     return self._create_inline_serializer()

    # @abstractmethod
    # def _create_text_serializer(self) -> BaseTextSerializer:
    #     raise NotImplementedError()

    # @abstractmethod
    # def _create_table_serializer(self) -> BaseTableSerializer:
    #     raise NotImplementedError()

    # @abstractmethod
    # def _create_picture_serializer(self) -> BasePictureSerializer:
    #     raise NotImplementedError()

    # @abstractmethod
    # def _create_key_value_serializer(self) -> BaseKeyValueSerializer:
    #     raise NotImplementedError()

    # @abstractmethod
    # def _create_form_serializer(self) -> BaseFormSerializer:
    #     raise NotImplementedError()

    # @abstractmethod
    # def _create_fallback_serializer(self) -> BaseFallbackSerializer:
    #     raise NotImplementedError()

    # @abstractmethod
    # def _create_list_serializer(self) -> BaseListSerializer:
    #     raise NotImplementedError()

    # @abstractmethod
    # def _create_inline_serializer(self) -> BaseInlineSerializer:
    #     raise NotImplementedError()

    # def stuff(self):
    #     return self._create_text_serializer()

    text_serializer: BaseTextSerializer
    table_serializer: BaseTableSerializer
    picture_serializer: BasePictureSerializer
    key_value_serializer: BaseKeyValueSerializer
    form_serializer: BaseFormSerializer
    fallback_serializer: BaseFallbackSerializer

    list_serializer: BaseListSerializer
    inline_serializer: BaseInlineSerializer

    @computed_field  # type: ignore
    @cached_property
    def excluded(self) -> list[str]:
        """References to excluded items."""
        _excluded: list[str] = [
            item.self_ref
            for ix, (item, _) in enumerate(
                self.doc.iterate_items(
                    with_groups=True,
                    traverse_pictures=True,
                )
            )
            if (
                (ix < self.start or ix >= self.stop)
                or (
                    isinstance(item, DocItem)
                    and (
                        item.label not in self.labels
                        or item.content_layer not in self.layers
                        or (
                            self.pages is not None
                            and (
                                (not item.prov)
                                or item.prov[0].page_no not in self.pages
                            )
                        )
                    )
                )
            )
        ]

        return _excluded

    class Config:
        """Pydantic config."""

        arbitrary_types_allowed = True

    # def serialize_list(
    #     self,
    #     *,
    #     item: Union[UnorderedList, OrderedList],
    #     list_level: int = 0,
    #     is_inline_scope: bool = False,
    #     visited: Optional[set[str]] = None,  # refs of visited items
    #     **kwargs,
    # ) -> SerializationResult:
    #     """Serializes the passed item."""
    #     if item not in self.excluded.trees:
    #         text = self.list_serializer.serialize(
    #             item=item,
    #             doc_serializer=self,
    #             doc=self.doc,
    #             list_level=list_level,
    #             is_inline_scope=is_inline_scope,
    #             visited=visited,
    #         )
    #     else:
    #         text = ""
    #     return SerializationResult(text=text)

    @abstractmethod
    def serialize(self, **kwargs) -> SerializationResult:
        """Run the serialization."""
        ...

    def serialize_bold(self, text: str) -> str:
        """Hook for bold formatting serialization."""
        return text

    def serialize_italic(self, text: str) -> str:
        """Hook for italic formatting serialization."""
        return text

    def serialize_underline(self, text: str) -> str:
        """Hook for underline formatting serialization."""
        return text

    def serialize_strikethrough(self, text: str) -> str:
        """Hook for strikethrough formatting serialization."""
        return text

    def serialize_hyperlink(self, text: str, hyperlink: Union[AnyUrl, Path]) -> str:
        """Hook for hyperlink serialization."""
        return text

    # making some assumptions about the kwargs it can pass
    def get_parts(
        self,
        *,
        node: Optional[NodeItem] = None,
        traverse_pictures: bool = False,
        # from_element: int,
        # to_element: int,
        # strict_text: bool,
        # escaping_underscores: bool,
        # image_placeholder: str,
        # image_mode: ImageRefMode,
        # text_width: int,
        # page_no: Optional[int],
        # included_content_layers: set[ContentLayer],
        list_level: int = 0,
        is_inline_scope: bool = False,
        visited: Optional[set[str]] = None,  # refs of visited items
    ) -> list[SerializationResult]:
        """Get the components to be combined for serializing this node."""
        my_visited: set[str] = visited if visited is not None else set()
        parts: list[SerializationResult] = []

        label_blocklist = {
            DocItemLabel.CAPTION,
            DocItemLabel.FOOTNOTE,
            # TODO more? Perhaps push down to iterate_items?
        }
        for ix, (item, _) in enumerate(
            self.doc.iterate_items(
                root=node,
                with_groups=True,
                traverse_pictures=traverse_pictures,
                # ...
            )
        ):
            if item.self_ref in my_visited:
                continue
            else:
                my_visited.add(item.self_ref)

            ########
            # groups
            ########
            if isinstance(item, (UnorderedList, OrderedList)):
                part = self.list_serializer.serialize(
                    item=item,
                    doc_serializer=self,
                    doc=self.doc,
                    list_level=list_level,
                    is_inline_scope=is_inline_scope,
                    visited=my_visited,
                )
            elif isinstance(item, InlineGroup):
                part = self.inline_serializer.serialize(
                    item=item,
                    doc_serializer=self,
                    doc=self.doc,
                    list_level=list_level,
                    visited=my_visited,
                )
            ###########
            # doc items
            ###########
            elif isinstance(item, DocItem) and item.label in label_blocklist:
                continue
            elif isinstance(item, TextItem):
                part = (
                    self.text_serializer.serialize(
                        item=item,
                        doc_serializer=self,
                        doc=self.doc,
                        is_inline_scope=is_inline_scope,
                    )
                    if item.self_ref not in self.excluded
                    else SerializationResult(text="")
                )
            elif isinstance(item, TableItem):
                part = self.table_serializer.serialize(
                    item=item,
                    doc_serializer=self,
                    doc=self.doc,
                )
            elif isinstance(item, PictureItem):
                part = self.picture_serializer.serialize(
                    item=item,
                    doc_serializer=self,
                    doc=self.doc,
                    visited=my_visited,
                    image_placeholder=self.image_placeholder,
                    image_mode=self.image_mode,
                )
            elif isinstance(item, KeyValueItem):
                part = self.key_value_serializer.serialize(
                    item=item,
                    doc_serializer=self,
                    doc=self.doc,
                )
            elif isinstance(item, FormItem):
                part = self.form_serializer.serialize(
                    item=item,
                    doc_serializer=self,
                    doc=self.doc,
                )
            else:
                part = self.fallback_serializer.serialize(
                    item=item,
                    doc_serializer=self,
                    doc=self.doc,
                )
            if part.text:
                parts.append(part)
        return parts

    def post_process(
        self,
        text: str,
        *,
        formatting: Optional[Formatting] = None,
        hyperlink: Optional[Union[AnyUrl, Path]] = None,
        **kwargs,
    ) -> str:
        """Apply some text post-processing steps."""
        res = text
        if self.include_formatting and formatting:
            if formatting.bold:
                res = self.serialize_bold(text=res)
            if formatting.italic:
                res = self.serialize_italic(text=res)
            if formatting.underline:
                res = self.serialize_underline(text=res)
            if formatting.strikethrough:
                res = self.serialize_strikethrough(text=res)
        if self.include_hyperlinks and hyperlink:
            res = self.serialize_hyperlink(text=res, hyperlink=hyperlink)
        return res

    # helper function
    def serialize_captions(
        self,
        item: FloatingItem,
        # doc_serializer: "BaseDocSerializer",
        # doc: DoclingDocument,
        separator: Optional[str] = None,
        **kwargs,
    ) -> SerializationResult:
        """Serialize the item's captions."""
        text_parts: list[str] = [
            it.text
            for cap in item.captions
            if isinstance(it := cap.resolve(self.doc), TextItem)
            and it.self_ref not in self.excluded
        ]
        text_res = (separator or "\n").join(text_parts)
        text_res = self.post_process(text=text_res)
        return SerializationResult(text=text_res)
