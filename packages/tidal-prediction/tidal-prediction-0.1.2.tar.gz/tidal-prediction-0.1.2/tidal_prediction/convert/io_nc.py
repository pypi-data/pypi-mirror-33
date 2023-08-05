"""
Module containing NetCDF methods used for the tidal prediction.
"""
# Standard library imports
import logging

# External imports
import netCDF4
import numpy as np


def create(filename):
    """Initialize output file."""
    dataset = netCDF4.Dataset(filename, "w", format="NETCDF4")
    dataset.set_auto_maskandscale(True)

    # Set Conventions attribute
    dataset.setncattr('Conventions', 'CF-1.7')

    return dataset
