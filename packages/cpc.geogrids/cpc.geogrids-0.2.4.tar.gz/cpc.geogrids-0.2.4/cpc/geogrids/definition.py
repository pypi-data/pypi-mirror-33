"""
Defines a GeoGrid object. Grid objects store certain properties of a gridded dataset (lat/lon grid
corners, resolution, etc.), and can simplify defining a grid when calling utilities such as
interpolation routines, plotting, etc.
"""


# Built-ins
import reprlib

# Third-party
import numpy as np

# This package
from cpc.geogrids.exceptions import GeogridError


# Create reprlib
r = reprlib.Repr()
r.maxlist = 4  # max elements displayed for lists
r.maxstring = 50  # max characters displayed for strings

# Create dict of all built-in GeoGrids
builtin_geogrids = {
    '1deg-global': {
        'll_corner': (-90, 0),
        'ur_corner': (90, 359),
        'res': 1,
        'type': 'latlon'
    },
    '2deg-global': {
        'll_corner': (-90, 0),
        'ur_corner': (90, 358),
        'res': 2,
        'type': 'latlon'
    },
    '2.5deg-global': {
        'll_corner': (-90, 0),
        'ur_corner': (90, 357.5),
        'res': 2.5,
        'type': 'latlon'
    },
    '2deg-conus': {
        'll_corner': (20, 230),
        'ur_corner': (56, 300),
        'res': 2,
        'type': 'latlon'
    },
    '1/6th-deg-global': {
        'll_corner': (-89.9167, 0.0833),
        'ur_corner': (89.9167, 359.9167),
        'res': 1/6,
        'type': 'latlon'
    },
    '0.5deg-global-edge-aligned': {
        'll_corner': (-89.75, 0.25),
        'ur_corner': (89.75, 359.75),
        'res': 0.5,
        'type': 'latlon'
    },
    '0.5deg-global-center-aligned': {
        'll_corner': (-90, 0),
        'ur_corner': (90, 359.5),
        'res': 0.5,
        'type': 'latlon'
    },
}


def list_builtin_geogrids():
    return list(builtin_geogrids.keys())


class Geogrid:
    """
    Geogrid object storing attributes of a geo grid.

    A Geogrid object can either be created by providing the name of the grid, or by providing the
    other attributes listed below

    #### Attributes

    - name - *str* - name of the grid
    - ll_corner - *tuple of floats* - lower-left corner of the grid, formatted as (lat, lon)
    - ur_corner - *tuple of floats* - upper-right corner of the grid, formatted as (lat, lon)
    - res = *float* - resolution of the grid (in km if `type="even"`, in degrees if `type="latlon"`)
    - type - *str* - grid type. Possible values are 'latlon' (Latlon grid), 'equal' (Equally-spaced square grid)
    """

    def __init__(self, name=None, ll_corner=None, ur_corner=None, res=None, type='latlon'):

        # ------------------------------------------------------------------------------------------
        # Document attributes
        #
        self.name = None
        '''Grid name'''
        self.ll_corner = ll_corner
        '''Lower-left corner of grid (lon, lat)'''
        self.ur_corner = ur_corner
        '''Upper-right corner of grid (lon, lat)'''
        self.res = res
        '''Grid resolution'''
        self.type = type
        '''Grid type (currently only latlon is supported)'''

        # ------------------------------------------------------------------------------------------
        # Create the Geogrid
        #
        # Built-in
        if name in builtin_geogrids:
            self.name = name
            self.ll_corner = builtin_geogrids[name]['ll_corner']
            self.ur_corner = builtin_geogrids[name]['ur_corner']
            self.res = builtin_geogrids[name]['res']
            self.type = builtin_geogrids[name]['type']
        # Custom
        else:
            # User didn't provide everything necessary to create a custom Geogrid
            if not all([self.ll_corner, self.ur_corner, self.res]):
                raise GeogridError('You must either supply the name of a built-in Grid, or an '
                                   'll_corner, ur_corner, and res to create a custom Grid')
            # Create a custom Geogrid
            else:
                self.name = 'custom'
                self.ll_corner = ll_corner
                self.ur_corner = ur_corner
                self.res = res
                self.type = type

        # ------------------------------------------------------------------------------------------
        # Calculate additional attributes
        #
        self.num_y = int(((self.ur_corner[0] - self.ll_corner[0]) / self.res) + 1)
        '''Number of points in the y-direction'''
        self.num_x = int(((self.ur_corner[1] - self.ll_corner[1]) / self.res) + 1)
        '''Number of points in the x-direction'''
        self.lats = np.arange(self.ll_corner[0], self.ur_corner[0] + 0.00000001, self.res).tolist()
        '''List of latitude values at which grid points are found'''
        self.lons = np.arange(self.ll_corner[1], self.ur_corner[1] + 0.00000001, self.res).tolist()
        '''List of longitude values at which grid points are found'''

    def __repr__(self):
        details = ''
        for key, val in sorted(vars(self).items()):
            details += eval(r.repr('- {}: {}\n'.format(key, val)))
        return 'Geogrid:\n{}'.format(details)

    def data_fits(self, data):
        """
        Determines if the specified data fits this Geogrid

        #### Parameters

        - data - *array_like* - data to verify

        #### Returns

        - *boolean* - whether the data fits this Geogrid

        #### Exceptions

        - *GeogridError* - raised if data is not a valid NumPy array

        #### Examples

            >>> import numpy as np
            >>> from cpc.geogrids import Geogrid
            >>> grid = Geogrid('1deg-global')
            >>> data = np.random.random((grid.num_y, grid.num_x))
            >>> data.shape
            (181, 360)
            >>> grid.data_fits(data)
            True
            >>> data = np.random.random((grid.num_y + 1, grid.num_x + 1))
            >>> data.shape
            (182, 361)
            >>> grid.data_fits(data)
            False
        """
        # Make sure there are num_y x num_x points
        try:
            if self.num_y * self.num_x != data.size:
                return False
            else:
                return True
        except AttributeError:
            raise GeogridError('Data not a valid NumPy array')

    def latlon_to_1d_index(self, latlons):
        """
        Returns the 1-dimensional index of the grid point, from this Geogrid, that is located at
        the specified lat/lon position

        For example, you may have a 1-dimensional data array on a `1deg-global` Geogrid, and you
        want to know the index corresponding to 50 deg lat, -80 deg lon.

        #### Parameters

        - latlons - *tuple of floats* or *list of tuples of floats* - lat/lon of grid point(s)

        #### Returns

        - *int* or *None* - array index containing the given gridpoint(s) index(es), or -1 if no gridpoint matches the
        given lat/lon value

        #### Examples

        Get the index of a 1deg-global grid at 50 deg lat, -80 deg lon

            >>> from cpc.geogrids import Geogrid
            >>> grid = Geogrid('1deg-global')
            >>> grid.latlon_to_1d_index((50, -80))
            [50820]

        Get the index of 1deg-global grid at several lat/lon points

            >>> from cpc.geogrids import Geogrid
            >>> grid = Geogrid('1deg-global')
            >>> grid.latlon_to_1d_index([(0, 0), (20, 40), (50, -80)])
            [90, 7350, 50820]
        """
        if type(latlons) is not list:
            latlons = [latlons]
        matches = []
        for latlon in latlons:
            lat, lon = latlon
            lon = 360 + lon if lon < 0 else lon
            lats, lons = np.meshgrid(self.lats, self.lons)
            lats = lats.reshape((self.num_y * self.num_x))
            lons = lons.reshape((self.num_y * self.num_x))
            try:
                matches.append(np.argwhere((lats == lat) & (lons == lon))[0][0])
            except IndexError:
                matches.append(-1)
        return matches

# Support applications referring to the legacy name for GeoGrids (Grids)
Grid = Geogrid
GridError = GeogridError

if __name__ == '__main__':
    from cpc.geogrids import Geogrid
    print(Geogrid('0.5deg-global-center-aligned'))
