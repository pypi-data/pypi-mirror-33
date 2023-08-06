# -*- coding: utf-8 -*-

from .lookups import Lookup
from .utils import fetch_url
from .core import GsxObject, GsxError

REASON_CODES = (
    ('A', 'Part not needed'),
    ('B', 'Duplicated part'),
    ('C', 'Added wrong part'),
    ('D', 'Tried to cancel order'),
    ('E', 'Customer refused order'),
)

IMAGE_URL = "https://km.support.apple.com.edgekey.net/kb/imageService.jsp?image=%s"


class Part(GsxObject):
    """A service part.

    >>> Part('922-7913').lookup().stockPrice
    6.16
    """
    def lookup(self):
        lookup = Lookup(**self._data)
        return lookup.parts()

    def fetch_image(self):
        """
        Tries the fetch the product image for this service part
        """
        if self.partNumber is None:
            raise GsxError("Cannot fetch part image without part number")

        image = "%s_350_350.gif" % self.partNumber

        try:
            return fetch_url(IMAGE_URL % image)
        except Exception as e:
            raise GsxError("Failed to fetch part image: %s" % e)


if __name__ == '__main__':
    import sys
    import doctest
    import logging
    from .core import connect
    logging.basicConfig(level=logging.DEBUG)
    connect(*sys.argv[1:])
    doctest.testmod()
