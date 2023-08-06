# Built-ins

# Third-party
import numpy as np
from pytest import raises

# This package
from cpc.geogrids.definition import list_builtin_geogrids, Geogrid, GeogridError
from cpc.geogrids.manipulation import interpolate, fill_outside_mask_borders, smooth


def test_interpolation():
    """Test that interpolation can be done between all grids"""
    # Create fake data for every grid
    fake_data = {}
    for gridname in list_builtin_geogrids():
        grid = Geogrid(gridname)
        fake_data[gridname] = np.random.rand(grid.num_y, grid.num_x).astype('float16')
    # Loop over every possible combination of grids
    for gridname1 in list_builtin_geogrids():
        for gridname2 in list_builtin_geogrids():
            # Create 2 Grid objects
            grid1 = Geogrid(gridname1)
            grid2 = Geogrid(gridname2)
            interpolate(fake_data[gridname1], grid1, grid2)
    # Make sure a 1-d input results in a 1-d output
    grid1 = Geogrid(list_builtin_geogrids()[0])
    grid2 = Geogrid(list_builtin_geogrids()[1])
    data1 = np.random.rand(grid1.num_y * grid1.num_x)
    data2 = interpolate(data1, grid1, grid2)
    assert data1.ndim == data2.ndim
    # Make sure a 2-d input results in a 2-d output
    grid1 = Geogrid(list_builtin_geogrids()[0])
    grid2 = Geogrid(list_builtin_geogrids()[1])
    data1 = np.random.rand(grid1.num_y, grid1.num_x)
    data2 = interpolate(data1, grid1, grid2)
    assert data1.ndim == data2.ndim


def test_fill_outside_borders():
    """Test the function that fills data outside the borders"""
    # Make sure when passing in a MaskedArray, a MaskedArray is returned
    test_array = np.ma.masked_array(np.random.rand(2, 2))
    returned_array = fill_outside_mask_borders(test_array)
    mask = returned_array.mask
    # Make sure when passing in a non-MaskedArray, a non-MaskedArray is returned
    test_array = np.random.rand(2, 2)
    returned_array = fill_outside_mask_borders(test_array)
    with raises(AttributeError):
        returned_array.mask
    # Make sure it raises a ValueError for 1-d data
    test_array = np.random.rand(5)
    with raises(ValueError):
        fill_outside_mask_borders(test_array)
    # Make sure an all-NaN array comes out as an all-NaN array
    test_array = np.empty((5, 5)) * np.nan
    output_array = fill_outside_mask_borders(test_array)
    assert np.all(np.isnan(output_array))


def test_smooth():
    """Test the function that smooths an array of spatial data"""
    # Make sure when passing in a MaskedArray, a MaskedArray is returned
    test_array = np.ma.masked_array(np.random.rand(2, 2))
    returned_array = fill_outside_mask_borders(test_array)
    mask = returned_array.mask
    # Make sure when passing in a non-MaskedArray, a non-MaskedArray is returned
    test_array = np.random.rand(2, 2)
    returned_array = fill_outside_mask_borders(test_array)
    with raises(AttributeError):
        returned_array.mask
    # Make sure a GridError is raised if the grid doesn't match the data
    test_grid = Geogrid(list_builtin_geogrids()[-1])
    test_array = np.random.rand(5, 5)
    with raises(GeogridError):
        smooth(test_array, test_grid)
    # Make sure the dimensions of the data don't change when smoothed
    test_grid = Geogrid(list_builtin_geogrids()[-1])
    test_array = np.random.rand(test_grid.num_y, test_grid.num_x)
    smoothed_array = smooth(test_array, test_grid)
    assert test_array.shape == smoothed_array.shape
