"""Models for the base data types."""

import copy
from enum import Enum
from typing import Tuple

from pydantic import BaseModel


class ImageRefMode(str, Enum):
    """ImageRefMode."""

    PLACEHOLDER = "placeholder"  # just a place-holder
    EMBEDDED = "embedded"  # embed the image as a base64
    REFERENCED = "referenced"  # reference the image via uri


class CoordOrigin(str, Enum):
    """CoordOrigin."""

    TOPLEFT = "TOPLEFT"
    BOTTOMLEFT = "BOTTOMLEFT"


class Size(BaseModel):
    """Size."""

    width: float = 0.0
    height: float = 0.0

    def as_tuple(self):
        """as_tuple."""
        return (self.width, self.height)


class BoundingBox(BaseModel):
    """BoundingBox."""

    l: float  # left
    t: float  # top
    r: float  # right
    b: float  # bottom

    coord_origin: CoordOrigin = CoordOrigin.TOPLEFT

    @property
    def width(self):
        """width."""
        return self.r - self.l

    @property
    def height(self):
        """height."""
        return abs(self.t - self.b)

    def scaled(self, scale: float) -> "BoundingBox":
        """scaled.

        :param scale: float:

        """
        return self.scale_to_size(page_size=Size(width=scale, height=scale))

    def normalized(self, page_size: Size) -> "BoundingBox":
        """normalized.

        :param page_size: Size:

        """
        return self.normalize_to_size(page_size=page_size)

    def normalize_to_size(self, page_size: Size) -> "BoundingBox":
        """normalize_to_size.

        :param page_size: Size:

        """
        out_bbox = copy.deepcopy(self)
        out_bbox.l /= page_size.width
        out_bbox.r /= page_size.width
        out_bbox.t /= page_size.height
        out_bbox.b /= page_size.height

        return out_bbox

    def scale_to_size(self, page_size: Size) -> "BoundingBox":
        """scale_to_size.

        :param page_size: Size:

        """
        out_bbox = copy.deepcopy(self)
        out_bbox.l *= page_size.width
        out_bbox.r *= page_size.width
        out_bbox.t *= page_size.height
        out_bbox.b *= page_size.height

        return out_bbox

    def as_tuple(self) -> Tuple[float, float, float, float]:
        """as_tuple."""
        if self.coord_origin == CoordOrigin.TOPLEFT:
            return (self.l, self.t, self.r, self.b)
        elif self.coord_origin == CoordOrigin.BOTTOMLEFT:
            return (self.l, self.b, self.r, self.t)

    @classmethod
    def from_tuple(cls, coord: Tuple[float, ...], origin: CoordOrigin):
        """from_tuple.

        :param coord: Tuple[float:
        :param ...]:
        :param origin: CoordOrigin:

        """
        if origin == CoordOrigin.TOPLEFT:
            l, t, r, b = coord[0], coord[1], coord[2], coord[3]
            if r < l:
                l, r = r, l
            if b < t:
                b, t = t, b

            return BoundingBox(l=l, t=t, r=r, b=b, coord_origin=origin)
        elif origin == CoordOrigin.BOTTOMLEFT:
            l, b, r, t = coord[0], coord[1], coord[2], coord[3]
            if r < l:
                l, r = r, l
            if b > t:
                b, t = t, b

            return BoundingBox(l=l, t=t, r=r, b=b, coord_origin=origin)

    def area(self) -> float:
        """area."""
        area = (self.r - self.l) * (self.b - self.t)
        if self.coord_origin == CoordOrigin.BOTTOMLEFT:
            area = -area
        return area

    def intersection_area_with(self, other: "BoundingBox", page_height: float) -> float:
        """intersection_area_with.

        :param other: "BoundingBox":

        """
        self_bl = self.to_bottom_left_origin(page_height=page_height)
        other_bl = other.to_bottom_left_origin(page_height=page_height)

        # Calculate intersection coordinates
        left = max(self_bl.l, other_bl.l)
        top = max(self_bl.t, other_bl.t)
        right = min(self_bl.r, other_bl.r)
        bottom = min(self_bl.b, other_bl.b)

        # Calculate intersection dimensions
        width = right - left
        height = bottom - top

        # If the bounding boxes do not overlap, width or height will be negative
        if width <= 0 or height <= 0:
            return 0.0

        return width * height

    def intersection_over_union(
        self, other: "BoundingBox", page_height: float, eps: float = 1.0e-6
    ) -> float:
        """intersection_over_union."""
        intersection_area = self.intersection_area_with(other, page_height=page_height)

        union_area = (
            abs(self.l - self.r) * abs(self.t - self.b)
            + abs(other.l - other.r) * abs(other.t - other.b)
            - intersection_area
        )

        return intersection_area / (union_area + eps)

    def to_bottom_left_origin(self, page_height: float) -> "BoundingBox":
        """to_bottom_left_origin.

        :param page_height:

        """
        if self.coord_origin == CoordOrigin.BOTTOMLEFT:
            return self.model_copy()
        elif self.coord_origin == CoordOrigin.TOPLEFT:
            return BoundingBox(
                l=self.l,
                r=self.r,
                t=page_height - self.t,
                b=page_height - self.b,
                coord_origin=CoordOrigin.BOTTOMLEFT,
            )

    def to_top_left_origin(self, page_height: float) -> "BoundingBox":
        """to_top_left_origin.

        :param page_height:

        """
        if self.coord_origin == CoordOrigin.TOPLEFT:
            return self.model_copy()
        elif self.coord_origin == CoordOrigin.BOTTOMLEFT:
            return BoundingBox(
                l=self.l,
                r=self.r,
                t=page_height - self.t,  # self.b
                b=page_height - self.b,  # self.t
                coord_origin=CoordOrigin.TOPLEFT,
            )

    def overlaps(self, other: "BoundingBox", page_height: float) -> bool:
        """overlaps."""
        return self.overlaps_horizontally(other=other) and self.overlaps_vertically(
            other=other, page_height=page_height
        )

    def overlaps_horizontally(self, other: "BoundingBox") -> bool:
        """overlaps_x."""
        return (
            (self.l <= other.l and other.l < self.r)
            or (self.l <= other.r and other.r < self.r)
            or (other.l <= self.l and self.l < other.r)
            or (other.l <= self.r and self.r < other.r)
        )

    def overlaps_vertically(self, other: "BoundingBox", page_height: float) -> bool:
        """overlaps_y."""
        self_bl = self.to_bottom_left_origin(page_height=page_height)
        other_bl = other.to_bottom_left_origin(page_height=page_height)

        return (
            (self_bl.b <= other_bl.b and other_bl.b < self_bl.t)
            or (self_bl.b <= other_bl.t and other_bl.t < self_bl.t)
            or (other_bl.b <= self_bl.b and self_bl.b < other_bl.t)
            or (other_bl.b <= self_bl.t and self_bl.t < other_bl.t)
        )

    def overlaps_vertically_with_iou(
        self, other: "BoundingBox", iou: float, page_height: float
    ) -> bool:
        """overlaps_y_with_iou."""
        self_bl = self.to_bottom_left_origin(page_height=page_height)
        other_bl = other.to_bottom_left_origin(page_height=page_height)

        if self_bl.overlaps_vertically(other=other_bl, page_height=page_height):

            u0 = min(self_bl.b, other_bl.b)
            u1 = max(self_bl.t, other_bl.t)

            i0 = max(self_bl.b, other_bl.b)
            i1 = min(self_bl.t, other_bl.t)

            iou_ = float(i1 - i0) / float(u1 - u0)
            return (iou_) > iou

        return False

    def is_left_of(self, other: "BoundingBox") -> bool:
        """is_left_of."""
        return self.r < other.r

    def is_strictly_left_of(self, other: "BoundingBox", eps: float = 0.001) -> bool:
        """is_strictly_left_of."""
        return (self.r + eps) < other.l

    def is_above_of(self, other: "BoundingBox", page_height: float) -> bool:
        """is_above."""
        self_bl = self.to_bottom_left_origin(page_height=page_height)
        other_bl = other.to_bottom_left_origin(page_height=page_height)

        return self_bl.t > other_bl.t

    def is_strictly_above_of(
        self, other: "BoundingBox", page_height: float, eps: float = 0.001
    ) -> bool:
        """is_strictly_above."""
        self_bl = self.to_bottom_left_origin(page_height=page_height)
        other_bl = other.to_bottom_left_origin(page_height=page_height)

        return (self_bl.b + eps) > other_bl.t

    def is_horizontally_connected(
        self, elem_i: "BoundingBox", elem_j: "BoundingBox", page_height: float
    ) -> bool:
        """is_horizontally_connected."""
        self_bl = self.to_bottom_left_origin(page_height=page_height)

        elem_i_bl = elem_i.to_bottom_left_origin(page_height=page_height)
        elem_j_bl = elem_j.to_bottom_left_origin(page_height=page_height)

        min_ij: float = min(elem_i_bl.b, elem_j_bl.b)
        max_ij: float = max(elem_i_bl.t, elem_j_bl.t)

        if self_bl.b < max_ij and min_ij < self_bl.t:  # overlap_y
            return False

        if self_bl.l < elem_i_bl.r and elem_j_bl.l < self_bl.r:
            return True

        return False
