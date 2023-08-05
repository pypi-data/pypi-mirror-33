"""
Module containing NetCDF methods used for the tidal prediction.
"""
# Standard library imports
import logging

# External imports
import netCDF4
import numpy as np
"""
def read_bathymetry(filename):
    # Reads bathymetry file.
    dataset = netCDF4.Dataset(filename, 'r')
    print(dataset)
    pass
"""


def create_outfile(filename, outputs, lat, lon):
    """Initialize output file."""
    dataset = netCDF4.Dataset(filename, "w", format="NETCDF4_CLASSIC")

    dataset.setncattr('Conventions', 'CF-1.7')

    dataset.set_auto_maskandscale(True)

    # Define dimensions
    dataset.createDimension('time', None)
    dataset.createDimension('lat', len(lat))
    dataset.createDimension('lon', len(lon))

    # Define dimensional variables
    nctm = dataset.createVariable('time', np.float64, ('time'))
    nclat = dataset.createVariable('lat', np.float32, ('lat'))
    nclon = dataset.createVariable('lon', np.float32, ('lon'))
    nclon[:] = lon
    nclat[:] = lat

    # Set attributes for dimensional variables
    nctm.setncattr('standard_name', 'time')
    nctm.setncattr('long_name', 'time')
    nclat.setncattr('standard_name', 'latitude')
    nclat.setncattr('long_name', 'latitude')
    nclat.setncattr('units', 'degrees_north')
    nclon.setncattr('standard_name', 'longitude')
    nclon.setncattr('long_name', 'longitude')
    nclon.setncattr('units', 'degrees_east')

    fill_value = netCDF4.default_fillvals['i2']  # -32767

    # Define u and v current variables
    if 'u' in outputs:
        ncu = dataset.createVariable(
            'u', 'i2', ('time', 'lat', 'lon'), fill_value=fill_value)
        ncu.setncattr('standard_name', 'eastward_sea_water_velocity')
        ncu.setncattr('long_name', 'Eastward velocity')
        ncu.setncattr('units', 'm s-1')
        ncu.setncattr('add_offset', 0.0)
        ncu.setncattr('scale_factor', 0.001)

    if 'v' in outputs:
        ncv = dataset.createVariable(
            'v', 'i2', ('time', 'lat', 'lon'), fill_value=fill_value)
        ncv.setncattr('standard_name', 'northward_sea_water_velocity')
        ncv.setncattr('long_name', 'Northward velocity')
        ncv.setncattr('units', 'm s-1')
        ncv.setncattr('add_offset', 0.0)
        ncv.setncattr('scale_factor', 0.001)

    # Define U and V transport variables
    if 'U' in outputs:
        ncu = dataset.createVariable(
            'U', 'i2', ('time', 'lat', 'lon'), fill_value=fill_value)
        ncu.setncattr('standard_name', 'ocean_volume_x_transport')
        ncu.setncattr('long_name', 'Eastward volume transport')
        ncu.setncattr('units', 'm2 s-1')
        ncu.setncattr('add_offset', 0.0)
        ncu.setncattr('scale_factor', 0.1)

    if 'V' in outputs:
        ncv = dataset.createVariable(
            'V', 'i2', ('time', 'lat', 'lon'), fill_value=fill_value)
        ncv.setncattr('standard_name', 'ocean_volume_y_transport')
        ncv.setncattr('long_name', 'Northward volume transport')
        ncv.setncattr('units', 'm2 s-1')
        ncv.setncattr('add_offset', 0.0)
        ncv.setncattr('scale_factor', 0.1)

    # Define elevation variable
    if 'z' in outputs:
        ncz = dataset.createVariable(
            'z', 'i2', ('time', 'lat', 'lon'), fill_value=fill_value)
        ncz.setncattr('standard_name', 'sea_surface_elevation')
        ncz.setncattr('long_name', 'Sea surface elevation')
        ncz.setncattr('units', 'm')
        ncz.setncattr('add_offset', 0.0)
        ncz.setncattr('scale_factor', 0.001)

    # Define depth
    add_offset = 5000.0
    scale_factor = 0.25  # Values are from 0 to ~10000
    ncdepth = dataset.createVariable(
        'depth', 'i2', ('lat', 'lon'), fill_value=fill_value)
    ncdepth.setncattr('standard_name', 'sea_floor_depth')
    ncdepth.setncattr('long_name', 'Sea floor depth')
    ncdepth.setncattr('units', 'm')
    ncdepth.setncattr('add_offset', add_offset)
    ncdepth.setncattr('scale_factor', scale_factor)

    return dataset
