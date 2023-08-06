"""
Contains methods for interpolating data between GeoGrids.
"""

# Built-ins
import warnings

# Third-party
import numpy as np
from scipy.ndimage.filters import gaussian_filter
import mpl_toolkits.basemap
from cpc.stats import find_nearest_index

# This package
from cpc.geogrids.exceptions import GeogridError


def interpolate(orig_data, orig_grid, new_grid):
    """
    Interpolates data from one Geogrid to another.

    ### Parameters

    - orig_data - *array_like* - array of original data
    - orig_grid - *Geogrid* - original Geogrid
    - new_grid - *Geogrid* - new Geogrid

    ### Returns

    - new_data - *array_like* - a data array on the desired Geogrid.

    ### Examples

    Interpolate gridded temperature obs from 2 degrees (CONUS) to 1 degree global

        #!/usr/bin/env python
        >>> # Import packages
        >>> import numpy as np
        >>> from cpc.geogrids.definition import Geogrid
        >>> from cpc.geogrids.manipulation import interpolate
        >>> # Create original and new GeoGrids
        >>> orig_grid = Geogrid('1deg-global')
        >>> new_grid = Geogrid('2deg-global')
        >>> # Generate random data on the original Geogrid
        >>> A = np.random.rand(orig_grid.num_y, orig_grid.num_x)
        >>> # Interpolate data to the new Geogrid
        >>> B = interpolate(A, orig_grid, new_grid)
        >>> # Print shapes of data before and after
        >>> print(A.shape)
        (181, 360)
        >>> print(B.shape)
        (91, 180)
    """

    # If orig and new grids are the same, we're done
    if orig_grid.name == new_grid.name:
        return orig_data

    # If data is 1-dimensional, reshape to 2 dimensions
    reshape_back_to_1 = False
    if orig_data.ndim == 1:
        reshape_back_to_1 = True
        orig_data = np.reshape(orig_data, (orig_grid.num_y, orig_grid.num_x))

    # Generate arrays of longitude and latitude values for the original grid
    num_lats, num_lons = (orig_grid.num_y, orig_grid.num_x)
    orig_start_lat, orig_start_lon = orig_grid.ll_corner
    orig_lons = np.arange(orig_start_lon, orig_start_lon + (num_lons * orig_grid.res),
                          orig_grid.res, np.float32)
    orig_lats = np.arange(orig_start_lat, orig_start_lat + (num_lats * orig_grid.res),
                          orig_grid.res, np.float32)

    # Generate mesh of longitude and latitude values for the new grid
    new_lons, new_lats = np.meshgrid(new_grid.lons, new_grid.lats)

    # Use the interp() function from mpl_toolkits.basemap to interpolate the grid to the new
    # lat/lon values.
    new_data = mpl_toolkits.basemap.interp(orig_data, orig_lons, orig_lats, new_lons, new_lats,
                                           order=1, masked=True)
    # Extract the data portion of the MaskedArray
    new_data = new_data.filled(np.nan)

    # If the original data was 1-dimensional, return to 1 dimension
    if reshape_back_to_1:
        new_data = np.reshape(new_data, (new_grid.num_y * new_grid.num_x))

    # May be faster, but so far doesn't work with missing data (ex. oceans)
    # f = interpolate.RectBivariateSpline(lats[:,1], lons[1,:], np.ma.masked_invalid(data),
    #                                     kx=1, ky=1)
    # data_new = f(lats_new[:,1], lons_new[1,:])

    return new_data


def fill_outside_mask_borders(data, passes=1):
    """
    Fill the grid points outside of the mask borders of a dataset (eg. over the ocean for
    land-only datasets) with the value from the nearest non-missing neighbor

    ### Parameters

    - data - *numpy array* - data to fill missing
    - passes - *int* - number of passes (for each pass, 1 extra layer of grid points will be
    filled)

    ### Returns

    - *numpy array* - a filled array

    ### Examples

    Create a 5x5 array of data, mask out the outer values, and fill

        >>> # Import packages
        >>> from cpc.geogrids.manipulation import fill_outside_mask_borders
        >>> import numpy as np
        >>> # Generate random data with missing values along the border
        >>> A = np.random.randint(1, 9, (5, 5)).astype('float16')
        >>> A[0] = A[-1] = A[:,0] = A[:,-1] = np.nan
        >>> A  # doctest: +SKIP
        array([[ nan,  nan,  nan,  nan,  nan],
               [ nan,   4.,   4.,   3.,  nan],
               [ nan,   6.,   7.,   3.,  nan],
               [ nan,   3.,   8.,   8.,  nan],
               [ nan,  nan,  nan,  nan,  nan]], dtype=float16)
        >>> # Fill the missing outside values with the nearest neighbor values
        >>> A = fill_outside_mask_borders(A)
        >>> A  # doctest: +SKIP
        array([[ 4.,  4.,  4.,  3.,  3.],
               [ 4.,  4.,  4.,  3.,  3.],
               [ 6.,  6.,  7.,  3.,  3.],
               [ 3.,  3.,  8.,  8.,  8.],
               [ 3.,  3.,  8.,  8.,  8.]], dtype=float16)
    """
    # Data must be 2-dimensional
    if data.ndim != 2:
        raise ValueError('data must be 2-dimensional')
    # If all values are NaNs, raise a warning
    if np.all(np.isnan(data)):
        warnings.warn('All values of data are NaN, returning original array')
        return data
    # If data is already a masked array, then make sure to return a masked array. If not,
    # return just the data portion
    try:
        data.mask
        is_masked = True
    except AttributeError as e:
        data = np.ma.masked_invalid(data)
        is_masked = False
    for _ in range(passes):
        for shift in (-1, 1):
            for axis in (0, 1):
                data_shifted = np.roll(data, shift=shift, axis=axis)
                idx = ~data_shifted.mask * data.mask
                data[idx] = data_shifted[idx]
    if is_masked:
        return data
    else:
        return data.data


def smooth(data, grid, factor=0.5):
    """
    Smooth an array of spatial data using a gaussian filter

    ### Parameters

    - data - *array_like* - array of spatial data
    - grid - *Geogrid* - Geogrid corresponding to data
    - factor - *float, optional* - sigma value for the gaussian filter

    ### Returns

    - *array_like* - array of smoothed spatial data

    ### Examples

    """
    # Make sure data matches grid
    if not grid.data_fits(data):
        raise GeogridError('data provided does not fit the Geogrid provided')
    # ----------------------------------------------------------------------------------------------
    # Smooth the data
    #
    # Get the mask of the current data array
    mask = np.ma.masked_invalid(data).mask
    # Fill all missing values with their nearest neighbor's value so that the following Gaussian
    # filter does not eat away the data set at the borders.
    data = fill_outside_mask_borders(data, passes=max([grid.num_y, grid.num_x]))
    # Apply a Gaussian filter to smooth the data
    data = gaussian_filter(data, factor, order=0, mode='nearest')
    # Reapply the mask from the initial data array
    return np.where(mask, np.NaN, data)


def grid_to_stn(gridded_data, grid, stn_lats, stn_lons):
    """Interpolates values from a grid to stations in a station list.

    Parameters
    ----------

    - gridded_data (array_like)
        - Array of gridded data
    - grid (Grid)
        - `data_utils.gridded.grid.Grid` that the gridded data is on
    - stn_lats (list)
        - List of station lats
    - stn_lons (list)
        - List of station lons

    Returns
    -------

    - list
        - List of values representing the value of the gridded data interpolated to the station
          locations

    Examples
    --------

    """
    # Make sure stn_lats and stn_lons are same length
    if len(stn_lats) != len(stn_lons):
        raise GeogridError('stn_lats and stn_lons must have the same length')
    # Reshape gridded data to 2 dimensions if necessary
    if gridded_data.ndim == 1:
        gridded_data = np.reshape(gridded_data, (grid.num_y, grid.num_x))
    # Create empty list to store station vals
    stn_val = []
    # Loop over all stations
    for i in range(len(stn_lats)):
        # Find closest grid point to station
        x_index = find_nearest_index(grid.lons, stn_lons[i])
        y_index = find_nearest_index(grid.lats, stn_lats[i])
        # Assign station val
        stn_val.append(gridded_data[y_index, x_index])

    return stn_val
