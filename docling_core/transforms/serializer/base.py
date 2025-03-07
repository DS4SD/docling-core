#
# Copyright IBM Corp. 2024 - 2025
# SPDX-License-Identifier: MIT
#

"""Define base classes for serialization."""
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional, Union

from pydantic import AnyUrl, BaseModel

from docling_core.types.doc.base import ImageRefMode
from docling_core.types.doc.document import (
    DocItem,
    DoclingDocument,
    Formatting,
    InlineGroup,
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
    ) -> str:
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
    ) -> str:
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
        image_mode: ImageRefMode,
        **kwargs,
    ) -> str:
        """Serializes the passed item."""
        ...

    # helper function
    def _serialize_captions(
        self,
        item: PictureItem,
        doc_serializer: "BaseDocSerializer",
        doc: DoclingDocument,
        separator: Optional[str] = None,
        **kwargs,
    ) -> str:
        parts: list[str] = [cap.resolve(doc).text for cap in item.captions]
        res = (separator or "\n").join(parts)
        res = doc_serializer.post_process(text=res)
        return res

    # helper function
    def _serialize_content(
        self,
        item: PictureItem,
        doc_serializer: "BaseDocSerializer",
        doc: DoclingDocument,
        separator: Optional[str] = None,
        visited: Optional[set[str]] = None,
        **kwargs,
    ) -> str:
        parts = doc_serializer.get_parts(  # FIXME
            node=item,
            traverse_pictures=True,
            # list_level=list_level,
            # is_inline_scope=is_inline_scope,
            visited=visited,
        )
        res = (separator or " ").join(parts)
        # NOTE: we do no postprocessing since already done as needed
        return res

    # helper function
    def _serialize_annotations(
        self,
        item: PictureItem,
        doc_serializer: "BaseDocSerializer",
        doc: DoclingDocument,
        separator: Optional[str] = None,
        **kwargs,
    ) -> str:
        ann_parts: list[str] = []
        for annotation in item.annotations:
            if isinstance(annotation, PictureClassificationData):
                predicted_class = (
                    annotation.predicted_classes[0].class_name
                    if annotation.predicted_classes
                    else None
                )
                if predicted_class is not None:
                    ann_parts.append(f"Picture type: {predicted_class}")
            elif isinstance(annotation, PictureMoleculeData):
                ann_parts.append(f"SMILES: {annotation.smi}")
            elif isinstance(annotation, PictureDescriptionData):
                ann_parts.append(f"Description: {annotation.text}")

        ann_txt = (separator or "\n").join(ann_parts)
        ann_txt = doc_serializer.post_process(text=ann_txt)
        return ann_txt


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
        visited: set[str],  # refs of visited items
        **kwargs,
    ) -> str:
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
        is_inline_scope: bool,
        visited: set[str],  # refs of visited items
        **kwargs,
    ) -> str:
        """Serializes the passed item."""
        ...


class BaseDocSerializer(BaseModel, ABC):
    """Base class for document serializers."""

    doc: DoclingDocument

    text_serializer: BaseTextSerializer
    table_serializer: BaseTableSerializer
    picture_serializer: BasePictureSerializer
    list_serializer: BaseListSerializer
    inline_serializer: BaseInlineSerializer

    include_formatting: bool = False  # added here since applied on text globally
    include_hyperlinks: bool = False  # added here since applied on text globally
    image_mode: ImageRefMode = ImageRefMode.EMBEDDED

    class Config:
        """Pydantic config."""

        arbitrary_types_allowed = True

    @abstractmethod
    def serialize(self, **kwargs) -> str:
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
    ) -> list[str]:
        """Get the components to be combined for serializing this node."""
        my_visited: set[str] = visited if visited is not None else set()
        parts: list[str] = []

        label_blocklist = {
            DocItemLabel.CAPTION,
            # TODO more?
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
                txt = self.list_serializer.serialize(
                    item=item,
                    doc_serializer=self,
                    doc=self.doc,
                    list_level=list_level,
                    is_inline_scope=is_inline_scope,
                    visited=my_visited,
                )
            elif isinstance(item, InlineGroup):
                txt = self.inline_serializer.serialize(
                    item=item,
                    doc_serializer=self,
                    doc=self.doc,
                    list_level=list_level,
                    is_inline_scope=is_inline_scope,
                    visited=my_visited,
                )
            ###########
            # doc items
            ###########
            elif isinstance(item, DocItem) and item.label in label_blocklist:
                continue
            elif isinstance(item, TextItem):
                txt = self.text_serializer.serialize(
                    item=item,
                    doc_serializer=self,
                    doc=self.doc,
                    is_inline_scope=is_inline_scope,
                )
            elif isinstance(item, TableItem):
                txt = self.table_serializer.serialize(
                    item=item,
                    doc_serializer=self,
                    doc=self.doc,
                )
            elif isinstance(item, PictureItem):
                txt = self.picture_serializer.serialize(
                    item=item,
                    doc_serializer=self,
                    doc=self.doc,
                    visited=my_visited,
                    image_mode=self.image_mode,
                )
                # ...
            else:
                continue  # ignore other items

            if txt:
                parts.append(txt)
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
