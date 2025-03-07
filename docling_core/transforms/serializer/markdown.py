#
# Copyright IBM Corp. 2024 - 2025
# SPDX-License-Identifier: MIT
#

"""Define classes for Markdown serialization."""
import html
from pathlib import Path
from typing import Optional, Union

from pydantic import AnyUrl
from tabulate import tabulate
from typing_extensions import override

from docling_core.transforms.serializer import (
    BaseDocSerializer,
    BaseListSerializer,
    BasePictureSerializer,
    BaseTableSerializer,
    BaseTextSerializer,
)
from docling_core.transforms.serializer.base import BaseInlineSerializer
from docling_core.types.doc.base import ImageRefMode
from docling_core.types.doc.document import (
    CodeItem,
    DoclingDocument,
    Formatting,
    FormulaItem,
    ImageRef,
    InlineGroup,
    OrderedList,
    PictureItem,
    SectionHeaderItem,
    TableItem,
    TextItem,
    TitleItem,
    UnorderedList,
)


class MarkdownTextSerializer(BaseTextSerializer):
    """Markdown-specific text item serializer."""

    @override
    def serialize(
        self,
        *,
        item: TextItem,
        doc_serializer: BaseDocSerializer,
        doc: DoclingDocument,
        is_inline_scope: bool = False,
        **kwargs,
    ) -> str:
        """Serializes the passed item."""
        do_escape_html = True
        if isinstance(item, TitleItem):
            res = f"# {item.text}"
        elif isinstance(item, SectionHeaderItem):
            res = f"{(item.level + 1) * '#'} {item.text}"
        elif isinstance(item, CodeItem):
            res = f"`{item.text}`" if is_inline_scope else f"```\n{item.text}\n```"
            do_escape_html = False
        elif isinstance(item, FormulaItem):
            res = f"${item.text}$" if is_inline_scope else f"$${item.text}$$"
            do_escape_html = False  # TODO: review
        else:
            res = item.text
        res = doc_serializer.post_process(
            text=res,
            do_escape_html=do_escape_html,
            formatting=item.formatting,
            hyperlink=item.hyperlink,
        )
        return res


class MarkdownTableSerializer(BaseTableSerializer):
    """Markdown-specific table item serializer."""

    @override
    def serialize(
        self,
        *,
        item: TableItem,
        doc_serializer: BaseDocSerializer,
        doc: DoclingDocument,
        **kwargs,
    ) -> str:
        """Serializes the passed item."""
        rows = [
            [
                # make sure that md tables are not broken
                # due to newline chars in the text
                col.text.replace("\n", " ")
                for col in row
            ]
            for row in item.data.grid
        ]

        if len(rows) > 1 and len(rows[0]) > 0:
            try:
                text = tabulate(rows[1:], headers=rows[0], tablefmt="github")
            except ValueError:
                text = tabulate(
                    rows[1:],
                    headers=rows[0],
                    tablefmt="github",
                    disable_numparse=True,
                )
        else:
            text = ""
        return text


class MarkdownPictureSerializer(BasePictureSerializer):
    """Markdown-specific picture item serializer."""

    @override
    def serialize(
        self,
        *,
        item: PictureItem,
        doc_serializer: BaseDocSerializer,
        doc: DoclingDocument,
        image_mode: ImageRefMode,
        **kwargs,
    ):
        """Serializes the passed item."""
        parts: list[str] = []

        cap_txt = self._serialize_captions(
            item=item,
            doc_serializer=doc_serializer,
            doc=doc,
            separator="\n",
        )
        if cap_txt:
            parts.append(cap_txt)

        img_txt = self._serialize_image_part(
            item=item,
            doc=doc,
            image_mode=image_mode,
        )
        if img_txt:
            parts.append(img_txt)
        res = "\n\n".join(parts)
        return res

    def _serialize_image_part(
        self,
        item: PictureItem,
        doc: DoclingDocument,
        image_mode: ImageRefMode,
        **kwargs,
    ) -> str:
        default_response = "<!-- image -->"
        error_response = (
            "<!-- 🖼️❌ Image not available. "
            "Please use `PdfPipelineOptions(generate_picture_images=True)`"
            " -->"
        )
        if image_mode == ImageRefMode.PLACEHOLDER:
            res = default_response
        elif image_mode == ImageRefMode.EMBEDDED:
            # short-cut: we already have the image in base64
            if (
                isinstance(item.image, ImageRef)
                and isinstance(item.image.uri, AnyUrl)
                and item.image.uri.scheme == "data"
            ):
                text = f"![Image]({item.image.uri})"
                res = text
            else:
                # get the item.image._pil or crop it out of the page-image
                img = item.get_image(doc=doc)

                if img is not None:
                    imgb64 = item._image_to_base64(img)
                    text = f"![Image](data:image/png;base64,{imgb64})"

                    res = text
                else:
                    res = error_response
        elif image_mode == ImageRefMode.REFERENCED:
            if not isinstance(item.image, ImageRef) or (
                isinstance(item.image.uri, AnyUrl) and item.image.uri.scheme == "data"
            ):
                res = default_response
            else:
                res = f"![Image]({str(item.image.uri)})"
        else:
            res = default_response
        return res


class MarkdownListSerializer(BaseListSerializer):
    """Markdown-specific list serializer."""

    @override
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
        parts = doc_serializer.get_parts(
            node=item,
            # from_element=from_element,
            # to_element=to_element,
            # labels=labels,
            # strict_text=strict_text,
            # escaping_underscores=escaping_underscores,
            # image_placeholder=image_placeholder,
            # image_mode=image_mode,
            # text_width=text_width,
            # page_no=page_no,
            # included_content_layers=included_content_layers,
            list_level=list_level + 1,
            is_inline_scope=is_inline_scope,
            visited=visited,
        )
        intent_len = 4
        indent_str = list_level * intent_len * " "
        is_ol = isinstance(item, OrderedList)
        text = "\n".join(
            [
                # avoid additional marker on already evaled sublists
                (
                    c
                    if c and c[0] == " "
                    else f"{indent_str}{f'{i + 1}.' if is_ol else '-'} {c}"
                )
                for i, c in enumerate(parts)
            ]
        )
        # text = self._post_process(
        #     text=text,
        #     do_escape_html=False,  # already escaped as needed
        #     formatting=None,
        #     hyperlink=None,
        # )
        return text


class MarkdownInlineSerializer(BaseInlineSerializer):
    """Markdown-specific inline group serializer."""

    @override
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
        parts = doc_serializer.get_parts(
            node=item,
            # from_element=from_element,
            # to_element=to_element,
            # labels=labels,
            # strict_text=strict_text,
            # escaping_underscores=escaping_underscores,
            # image_placeholder=image_placeholder,
            # image_mode=image_mode,
            # text_width=text_width,
            # page_no=page_no,
            # included_content_layers=included_content_layers,
            list_level=list_level,
            is_inline_scope=True,
            visited=visited,
        )
        text = " ".join(parts)
        # text = self._post_process(
        #     text=text,
        #     do_escape_html=False,  # already escaped as needed
        #     formatting=None,
        #     hyperlink=None,
        # )
        return text


class MarkdownDocSerializer(BaseDocSerializer):
    """Markdown-specific document serializer."""

    text_serializer: BaseTextSerializer = MarkdownTextSerializer()
    table_serializer: BaseTableSerializer = MarkdownTableSerializer()
    picture_serializer: BasePictureSerializer = MarkdownPictureSerializer()
    list_serializer: BaseListSerializer = MarkdownListSerializer()
    inline_serializer: BaseInlineSerializer = MarkdownInlineSerializer()

    @override
    def serialize_bold(self, text):
        """Apply Markdown-specific bold serialization."""
        return f"**{text}**"

    @override
    def serialize_italic(self, text):
        """Apply Markdown-specific italic serialization."""
        return f"*{text}*"

    @override
    def serialize_strikethrough(self, text):
        """Apply Markdown-specific strikethrough serialization."""
        return f"~~{text}~~"

    @override
    def serialize_hyperlink(self, text, hyperlink):
        """Apply Markdown-specific hyperlink serialization."""
        return f"[{text}]({str(hyperlink)})"

    def post_process(
        self,
        text: str,
        *,
        do_escape_html: bool = True,
        # do_escape_underscores: bool = True,
        formatting: Optional[Formatting] = None,
        hyperlink: Optional[Union[AnyUrl, Path]] = None,
        **kwargs,
    ) -> str:
        """Apply some text post-processing steps."""
        res = text
        # if do_escape_underscores #and escaping_underscores:
        #     text = _escape_underscores(text)
        if do_escape_html:
            res = html.escape(res, quote=False)
        res = super().post_process(
            text=res,
            formatting=formatting,
            hyperlink=hyperlink,
        )
        return res

    @override
    def serialize(self, **kwargs) -> str:
        """Run the serialization."""
        parts = self.get_parts()
        return "\n\n".join(parts)
