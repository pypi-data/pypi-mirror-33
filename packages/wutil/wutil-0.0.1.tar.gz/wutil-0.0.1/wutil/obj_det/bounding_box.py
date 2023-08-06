import json
from shapely.geometry import Polygon


class Point(object):
    """ Point class.  """

    def __init__(self, x, y):
        """ Create :class:`Point`. """
        self.x = x
        self.y = y

    def __repr__(self):
        return 'x: {}, y: {}'.format(self.x, self.y)

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y


class BoundingBox(object):
    """ Represents a 4-point bounding box with category and annotation.

    Default constructor assumes rectangular form.
    """

    def __init__(self, x, y, w, h, category, annotation=None, confidence=1.0):
        self.tl = Point(x, y)
        self.tr = Point(x + w, y)
        self.br = Point(x + w, y + h)
        self.bl = Point(x, y + h)
        self.category = category
        self.annotation = annotation
        self.confidence = confidence

    def __repr__(self):
        return 'x: {}, y: {}, w: {}, h: {}, cent_x: {}, cent_y: {}, category: {}, confidence: {}'.format(self.tl.x, self.tl.y,
                                                                                                         self.w, self.h,
                                                                                                         self.tl.x + self.w / 2,
                                                                                                         self.tl.y + self.h / 2,
                                                                                                         self.category,
                                                                                                         self.confidence)

    @property
    def w(self) -> int:
        """
        Returns
        -------
        int
            Bounding box width.

        """
        return self.br.x - self.tl.x

    @property
    def h(self):
        """
        Returns
        -------
        int
            Bounding box height.

        """
        return self.br.y - self.tl.y

    def scaled(self, w_scale, h_scale):
        """
        Returns
        -------
        bb : :class:`BoundingBox`
            new scaled bounding box.

        """
        return BoundingBox(self.tl.x * w_scale, self.tl.y * h_scale, self.w * w_scale, self.h * h_scale, self.category)

    def shifted(self, w_shift, h_shift):
        """
        Returns
        -------
        bb : :class:`BoundingBox`
            new shifted bounding box.

        """
        return BoundingBox(self.tl.x + w_shift, self.tl.y + h_shift, self.w, self.h, self.category)

    @property
    def int_coords(self):
        """
        Returns
        -------
        (x1, y1), (x2, y2)
            coords suitable for PIL image region selection

        """
        return (int(round(self.tl.x)), int(round(self.tl.y))), (int(round(self.br.x)), int(round(self.br.y)))

    @property
    def flat_int_coords(self):
        """
        Returns
        -------
        (x1, y1), (x2, y2)
            flat int coords suitable for image region selection

        """
        tl, br = self.int_coords
        return tl[0], tl[1], br[0], br[1]

    @property
    def center(self):
        """
        Returns
        -------
        p : :class:`Point`
            center point.

        """
        return Point(self.tl.x + self.w / 2, self.tl.y + self.h / 2)

    @property
    def poly(self):
        """
        Returns
        -------
        shapely.Polygon
            polygon constructed from :class:`BoundingBox`.

        """
        return Polygon([[self.tl.x, self.tl.y], [self.tr.x, self.tr.y], [self.br.x, self.br.y], [self.bl.x, self.bl.y]])

    @staticmethod
    def from_coords(x1, y1, x2, y2, category, annotation=None, confidence=1.0):
        """ Create :class:`BoundingBox` from corner coordinates.

        Returns
        -------
        bb : :class:`BoundingBox`
            new BoundingBox

        """
        w = x2 - x1
        h = y2 - y1
        return BoundingBox(x1, y1, w, h, category, annotation, confidence)


class BoundingBoxEncoder(json.JSONEncoder):
    """ Json encoder with BoundingBox support. """

    def default(self, obj):
        if isinstance(obj, BoundingBox):
            return {'x': obj.tl.x, 'y': obj.tl.y, 'w': obj.w, 'h': obj.h, 'category': obj.category}
        else:
            return super().default(obj)


def read_bb4_labels(bb_path, label_mapping):
    """ Parse bb4 annotation file.

    Returns
    -------
    boxes : list of :class:`BoundingBox`
    im_w : int
    im_h : int

    """
    boxes = []
    im_w, im_h = 0, 0
    with open(bb_path) as bboxes_file:
        lines = bboxes_file.readlines()
        if lines:  # bbox file can be empty
            num_boxes, im_w, im_h = map(int, lines[0].strip().split(';'))
            for bbox_line_idx in range(1, num_boxes + 1):
                split_bbox_line = lines[bbox_line_idx].strip().split(';')

                if len(split_bbox_line) == 10:
                    tl_x, tl_y, tr_x, tr_y, br_x, br_y, bl_x, bl_y, category, annotation = split_bbox_line
                else:
                    tl_x, tl_y, tr_x, tr_y, br_x, br_y, bl_x, bl_y, category = split_bbox_line
                    annotation = ''
                tl_x, tl_y, tr_x, tr_y, br_x, br_y, bl_x, bl_y = map(int, [tl_x, tl_y, tr_x, tr_y, br_x, br_y, bl_x, bl_y])
                category = label_mapping.get(category, category)

                x_max = max([tl_x, tr_x, br_x, bl_x])
                x_min = min([tl_x, tr_x, br_x, bl_x])
                y_max = max([tl_y, tr_y, br_y, bl_y])
                y_min = min([tl_y, tr_y, br_y, bl_y])

                boxes.append(BoundingBox(x_min, y_min, x_max - x_min, y_max - y_min, category, annotation))
    return boxes, im_w, im_h

def read_bb_labels(bb_path):
    """ Parse bb annotation file.

    Returns
    -------
    boxes : list of :class:`BoundingBox`
    im_w : int
    im_h : int

    """
    with open(bb_path) as bboxes_file:
        boxes = []
        im_w, im_h = 0, 0
        lines = bboxes_file.readlines()
        if lines:  # bbox file can be empty
            num_boxes, im_w, im_h = map(int, lines[0].strip().split(' '))
            for bbox_line_idx in range(1, num_boxes + 1):
                split_bbox_line = lines[bbox_line_idx].strip().split(' ', 4)

                x, y, w, h, category = split_bbox_line
                x, y, w, h = map(int, [x, y, w, h])
                boxes.append(BoundingBox(x, y, w, h, category))
        return boxes, im_w, im_h
