#
# Copyright IBM Corp. 2024 - 2024
# SPDX-License-Identifier: MIT
#

"""Tokens used in the docling document model."""

from enum import Enum
from typing import Tuple


class DocumentToken(Enum):
    """Class to represent an LLM friendly representation of a Document."""

    BEG_DOCUMENT = "<document>"
    END_DOCUMENT = "</document>"

    BEG_TITLE = "<title>"
    END_TITLE = "</title>"

    BEG_ABSTRACT = "<abstract>"
    END_ABSTRACT = "</abstract>"

    BEG_DOI = "<doi>"
    END_DOI = "</doi>"
    BEG_DATE = "<date>"
    END_DATE = "</date>"

    BEG_AUTHORS = "<authors>"
    END_AUTHORS = "</authors>"
    BEG_AUTHOR = "<author>"
    END_AUTHOR = "</author>"

    BEG_AFFILIATIONS = "<affiliations>"
    END_AFFILIATIONS = "</affiliations>"
    BEG_AFFILIATION = "<affiliation>"
    END_AFFILIATION = "</affiliation>"

    BEG_HEADER = "<section-header>"
    END_HEADER = "</section-header>"
    BEG_TEXT = "<text>"
    END_TEXT = "</text>"
    BEG_PARAGRAPH = "<paragraph>"
    END_PARAGRAPH = "</paragraph>"
    BEG_TABLE = "<table>"
    END_TABLE = "</table>"
    BEG_FIGURE = "<figure>"
    END_FIGURE = "</figure>"
    BEG_CAPTION = "<caption>"
    END_CAPTION = "</caption>"
    BEG_EQUATION = "<equation>"
    END_EQUATION = "</equation>"
    BEG_LIST = "<list>"
    END_LIST = "</list>"
    BEG_LISTITEM = "<list-item>"
    END_LISTITEM = "</list-item>"

    BEG_LOCATION = "<location>"
    END_LOCATION = "</location>"
    BEG_GROUP = "<group>"
    END_GROUP = "</group>"

    @classmethod
    def get_special_tokens(
        cls,
        max_rows: int = 100,
        max_cols: int = 100,
        max_pages: int = 1000,
        page_dimension: Tuple[int, int] = (100, 100),
    ):
        """Function to get all special document tokens."""
        special_tokens = [token.value for token in cls]

        # Adding dynamically generated row and col tokens
        for i in range(0, max_rows + 1):
            special_tokens += [f"<row_{i}>", f"</row_{i}>"]

        for i in range(0, max_cols + 1):
            special_tokens += [f"<col_{i}>", f"</col_{i}>"]

        for i in range(6):
            special_tokens += [f"<section-header-{i}>", f"</section-header-{i}>"]

        # Adding dynamically generated page-tokens
        for i in range(0, max_pages + 1):
            special_tokens.append(f"<page_{i}>")

        # Adding dynamically generated location-tokens
        for i in range(0, max(page_dimension[0] + 1, page_dimension[1] + 1)):
            special_tokens.append(f"<loc_{i}>")

        return special_tokens

    @staticmethod
    def get_row_token(row: int, beg=bool) -> str:
        """Function to get page tokens."""
        if beg:
            return f"<row_{row}>"
        else:
            return f"</row_{row}>"

    @staticmethod
    def get_col_token(col: int, beg=bool) -> str:
        """Function to get page tokens."""
        if beg:
            return f"<col_{col}>"
        else:
            return f"</col_{col}>"

    @staticmethod
    def get_page_token(page: int):
        """Function to get page tokens."""
        return f"<page_{page}>"

    @staticmethod
    def get_location_token(val: float, rnorm: int = 100):
        """Function to get location tokens."""
        val_ = round(rnorm * val)

        if val_ < 0:
            return "<loc_0>"

        if val_ > rnorm:
            return f"<loc_{rnorm}>"

        return f"<loc_{val_}>"
