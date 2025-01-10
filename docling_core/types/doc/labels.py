"""Models for the labels types."""

from enum import Enum


class DocItemLabel(str, Enum):
    """DocItemLabel."""

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
    PARAGRAPH = "paragraph"  # explicitly a paragraph and not arbitrary text
    REFERENCE = "reference"

    def __str__(self):
        """Get string value."""
        return str(self.value)


class GroupLabel(str, Enum):
    """GroupLabel."""

    UNSPECIFIED = "unspecified"
    LIST = (
        "list"  # group label for list container (not the list-items) (e.g. HTML <ul/>)
    )
    ORDERED_LIST = "ordered_list"  # List with enumeration (e.g. HTML <ol/>)
    CHAPTER = "chapter"
    SECTION = "section"
    SHEET = "sheet"
    SLIDE = "slide"
    FORM_AREA = "form_area"
    KEY_VALUE_AREA = "key_value_area"
    COMMENT_SECTION = "comment_section"

    def __str__(self):
        """Get string value."""
        return str(self.value)


class DocLinkLabel(str, Enum):
    """DocLinkLabel."""

    READING_ORDER = "reading_order"

    TO_CAPTION = "to_caption"
    TO_FOOTNOTE = "to_footnote"
    TO_VALUE = "to_value"
    TO_CHILD = "to_child"

    CONTINUED = "continued"

    def __str__(self):
        """Get string value."""
        return str(self.value)


class PictureClassificationLabel(str, Enum):
    """PictureClassificationLabel."""

    UNCLASSIFIED = "unclassified"

    # If more than one picture is grouped together, it
    # is generally not possible to assign a label
    PICTURE_GROUP = "picture_group"

    # General
    PIE_CHART = "pie_chart"
    BAR_CHART = "bar_chart"
    LINE_CHART = "line_chart"
    FLOW_CHART = "flow_chart"
    SCATTER_CHART = "scatter_chart"
    HEATMAP = "heatmap"

    NATURAL_IMAGE = "natural_image"

    # Chemistry
    MOLECULAR_STRUCTURE = "molecular_structure"
    MARKUSH_STRUCTURE = "markush_structure"

    # Company
    LOGO = "logo"
    SIGNATURE = "signature"

    # Geology/Geography
    GEOGRAPHIC_MAP = "geographic_map"
    STRATIGRAPHIC_CHART = "stratigraphic_chart"

    # Engineering
    CAD_DRAWING = "cad_drawing"
    ELECTRICAL_DIAGRAM = "electrical_diagram"

    def __str__(self):
        """Get string value."""
        return str(self.value)


class TableComponentLabel(str, Enum):
    """TableComponentLabel."""

    TABLE_ROW = "table_row"  # the most atomic row
    TABLE_COL = "table_column"  # the most atomic col
    TABLE_GROUP = (
        "table_group"  # table-cell group with at least 1 row- or col-span above 1
    )

    def __str__(self):
        """Get string value."""
        return str(self.value)


class TableCellLabel(str, Enum):
    """TableCellLabel."""

    COLUMN_HEADER = "col_header"
    ROW_HEADER = "row_header"
    ROW_SECTION = "row_section"
    BODY = "body"

    def __str__(self):
        """Get string value."""
        return str(self.value)
