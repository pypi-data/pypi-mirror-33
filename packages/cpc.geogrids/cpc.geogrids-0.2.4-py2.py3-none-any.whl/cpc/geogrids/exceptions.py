"""
Defines all Exceptions used by the GeoGrids package
"""


class GeogridError(Exception):
    def __init__(self, *args, **kwargs):
        Exception.__init__(self, *args, **kwargs)
