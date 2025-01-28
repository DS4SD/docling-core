"""Models for the base data types."""

import warnings
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
        warnings.warn(
            "scaled is deprecated: use `scale_to_size` instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        return self.scale_to_size(size=Size(width=scale, height=scale))

    def normalized(self, page_size: Size) -> "BoundingBox":
        """normalized.

        :param page_size: Size:

        """
        warnings.warn(
            "normalized is deprecated: use `normalize_to_size` instead",
            DeprecationWarning,
            stacklevel=2,
        )
        return self.normalize_to_size(size=page_size)

    def normalize_to_size(self, size: Size) -> "BoundingBox":
        """normalize_to_size.

        :param page_size: Size:

        """
        return BoundingBox(
            l=self.l / size.width,
            r=self.r / size.width,
            t=self.t / size.height,
            b=self.b / size.height,
            coord_origin=self.coord_origin,
        )

    def scale_to_size(self, size: Size) -> "BoundingBox":
        """scale_to_size.

        :param page_size: Size:

        """
        return BoundingBox(
            l=self.l * size.width,
            r=self.r * size.width,
            t=self.t * size.height,
            b=self.b * size.height,
            coord_origin=self.coord_origin,
        )

    def expand_to_size(self, size: Size) -> "BoundingBox":
        """expand_to_size."""
        if self.coord_origin == CoordOrigin.TOPLEFT:
            return BoundingBox(
                l=self.l - self.width * size.width,
                r=self.r + self.width * size.width,
                t=self.t - self.height * size.height,
                b=self.b + self.height * size.height,
                coord_origin=self.coord_origin,
            )
        elif self.coord_origin == CoordOrigin.BOTTOMLEFT:
            return BoundingBox(
                l=self.l - self.width * size.width,
                r=self.r + self.width * size.width,
                t=self.t + self.height * size.height,
                b=self.b - self.height * size.height,
                coord_origin=self.coord_origin,
            )

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
        return abs(self.r - self.l) * abs(self.b - self.t)

    def intersection_area_with(self, other: "BoundingBox") -> float:
        """intersection_area_with.

        :param other: "BoundingBox":

        """
        if (
            self.coord_origin == CoordOrigin.BOTTOMLEFT
            and other.coord_origin == CoordOrigin.BOTTOMLEFT
        ):

            # Calculate intersection coordinates
            left = max(self.l, other.l)
            right = min(self.r, other.r)

            bottom = max(self.b, other.b)
            top = min(self.t, other.t)

            # Calculate intersection dimensions
            width = right - left
            height = top - bottom

            # If the bounding boxes do not overlap, width or height will be negative
            if width <= 0 or height <= 0:
                return 0.0

            return width * height
        elif (
            self.coord_origin == CoordOrigin.TOPLEFT
            and other.coord_origin == CoordOrigin.TOPLEFT
        ):

            # Calculate intersection coordinates
            left = max(self.l, other.l)
            right = min(self.r, other.r)

            bottom = min(self.b, other.b)
            top = max(self.t, other.t)

            # Calculate intersection dimensions
            width = right - left
            height = bottom - top

            # If the bounding boxes do not overlap, width or height will be negative
            if width <= 0 or height <= 0:
                return 0.0

            return width * height
        else:
            raise ValueError("BoundingBox is not BOTTOMLEFT")

        return False

    def intersection_over_union(
        self, other: "BoundingBox", eps: float = 1.0e-6
    ) -> float:
        """intersection_over_union."""
        intersection_area = self.intersection_area_with(other)

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

    def overlaps(self, other: "BoundingBox") -> bool:
        """overlaps."""
        return self.overlaps_horizontally(other=other) and self.overlaps_vertically(
            other=other
        )

    def overlaps_horizontally(self, other: "BoundingBox") -> bool:
        """overlaps_x."""
        return (
            (self.l <= other.l and other.l < self.r)
            or (self.l <= other.r and other.r < self.r)
            or (other.l <= self.l and self.l < other.r)
            or (other.l <= self.r and self.r < other.r)
        )

    def overlaps_vertically(self, other: "BoundingBox") -> bool:
        """overlaps_y."""
        if (
            self.coord_origin == CoordOrigin.BOTTOMLEFT
            and other.coord_origin == CoordOrigin.BOTTOMLEFT
        ):
            return (
                (self.b <= other.b and other.b < self.t)
                or (self.b <= other.t and other.t < self.t)
                or (other.b <= self.b and self.b < other.t)
                or (other.b <= self.t and self.t < other.t)
            )
        else:
            raise ValueError("BoundingBox is not BOTTOMLEFT")

        return False

    def overlaps_vertically_with_iou(self, other: "BoundingBox", iou: float) -> bool:
        """overlaps_y_with_iou."""
        if (
            self.coord_origin == CoordOrigin.BOTTOMLEFT
            and other.coord_origin == CoordOrigin.BOTTOMLEFT
        ):

            if self.overlaps_vertically(other=other):

                u0 = min(self.b, other.b)
                u1 = max(self.t, other.t)

                i0 = max(self.b, other.b)
                i1 = min(self.t, other.t)

                iou_ = float(i1 - i0) / float(u1 - u0)
                return (iou_) > iou

            return False
        else:
            raise ValueError("BoundingBox is not BOTTOMLEFT")

        return False

    def is_left_of(self, other: "BoundingBox") -> bool:
        """is_left_of."""
        return self.r < other.r

    def is_strictly_left_of(self, other: "BoundingBox", eps: float = 0.001) -> bool:
        """is_strictly_left_of."""
        return (self.r + eps) < other.l

    def is_above_of(self, other: "BoundingBox") -> bool:
        """is_above."""
        if (
            self.coord_origin == CoordOrigin.BOTTOMLEFT
            and other.coord_origin == CoordOrigin.BOTTOMLEFT
        ):
            return self.t > other.t
        else:
            raise ValueError("BoundingBox is not BOTTOMLEFT")

        return False

    def is_strictly_above_of(self, other: "BoundingBox", eps: float = 0.001) -> bool:
        """is_strictly_above."""
        if (
            self.coord_origin == CoordOrigin.BOTTOMLEFT
            and other.coord_origin == CoordOrigin.BOTTOMLEFT
        ):
            return (self.b + eps) > other.t
        else:
            raise ValueError("BoundingBox is not BOTTOMLEFT")

        return False

    def is_horizontally_connected(
        self, elem_i: "BoundingBox", elem_j: "BoundingBox"
    ) -> bool:
        """is_horizontally_connected."""
        if (
            self.coord_origin == CoordOrigin.BOTTOMLEFT
            and elem_i.coord_origin == CoordOrigin.BOTTOMLEFT
            and elem_j.coord_origin == CoordOrigin.BOTTOMLEFT
        ):

            min_ij: float = min(elem_i.b, elem_j.b)
            max_ij: float = max(elem_i.t, elem_j.t)

            if self.b < max_ij and min_ij < self.t:  # overlap_y
                return False

            if self.l < elem_i.r and elem_j.l < self.r:
                return True

            return False
        else:
            raise ValueError("BoundingBox is not BOTTOMLEFT")

        return False
