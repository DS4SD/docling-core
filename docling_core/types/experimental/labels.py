from enum import Enum


class PageLabel(str, Enum):
    # DocLayNet v2
    CAPTION = "caption"
    FOOTNOTE = "footnote"
    FORMULA = "formula"
    LIST_ITEM = "list_item"
    PAGE_FOOTER = "page_footer"
    PAGE_HEADER = "page_header"
    PICTURE = "picture"
    SECTION_HEADER = "section_header"
    TABLE = "table"
    TEXT = "text"
    TITLE = "title"
    DOCUMENT_INDEX = "document_index"
    CODE = "code"
    CHECKBOX_SELECTED = "checkbox_selected"
    CHECKBOX_UNSELECTED = "checkbox_unselected"
    FORM = "form"
    KEY_VALUE_REGION = "key_value_region"

    # Additional labels for markup-based formats (e.g. HTML, Word)
    LIST = "list"  # group label for list container (not the list-items)
    PARAGRAPH = "paragraph"  # explicitly a paragraph and not arbitrary text
    REFERENCE = "reference"

    # To be completed...


class TableLabel(str, Enum):
    COLUMN_HEADER = "col_header"
    ROW_HEADER = "row_header"
    SECTION = "row_section"
    BODY = "body"
