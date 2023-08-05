"""
Tidal model main module. This module is responsible for setting up and
executing the tidal model.
"""

# Standard library imports
import datetime
import logging
#import multiprocessing
import pprint

# External imports
from astropy.time import Time
#import bohrium
import netCDF4
import numpy as np

# Local imports
from . import nc
from . import tideutils


class Model:
    """Tidal model class."""

    def __init__(self, outfile, cfg):
        """Setup of tidal model."""
        pp = pprint.PrettyPrinter(indent=2, compact=True)
        logging.info('Setting up model with config:\n%s' % pp.pformat(cfg))

        # Read bathymetry and grid
        infile = cfg['input_file']
        logging.info('Reading input file %s' % infile)
        self.infile = netCDF4.Dataset(infile, 'r')

        # Extract grid information
        self.lat = self.infile.variables['lat'][:]
        self.nlat = len(self.lat)
        self.lon = self.infile.variables['lon'][:]
        self.nlon = len(self.lon)

        # Find number of points
        self.ndat = self.nlat * self.nlon

        # Constituents
        self.constids = cfg['constituents']
        logging.info('Using these constituents: %s' % self.constids)

        # How many processes to run
        self.numprocs = cfg['numprocs']

        # Create pool
        #self.pool = multiprocessing.Pool(nprocs=self.numprocs)

        # Approximate chunk size to be processed at a time
        self.nchunk = cfg['chunksize']

        # Interpolate minor constituents from major constituents
        self.interpolate_minor = cfg['interpolate_minor']
        if self.interpolate_minor:
            logging.info('Interpolating minor constituents')

        # What output do we want
        self.outputs = cfg['outputs']

        # Assume that u/U and v/V are enabled together
        if 'u' in self.outputs:
            assert 'v' in self.outputs
        if 'U' in self.outputs:
            assert 'V' in self.outputs
        if 'v' in self.outputs:
            assert 'u' in self.outputs
        if 'V' in self.outputs:
            assert 'U' in self.outputs

        # Initialize output NetCDF file
        logging.info('Creating output file %s' % outfile)
        self.outfile = nc.create_outfile(outfile, self.outputs, self.lat,
                                         self.lon)

        # We process this many latitude rows at a time
        self.nlat_chunk = int(self.nchunk / self.nlon)

        # Write depths to NetCDF file in chunks
        logging.info('Writing depth to output file %s' % outfile)
        for j in range(0, self.nlat, self.nlat_chunk):
            # Calculate end index
            jj = min(j + self.nlat_chunk, self.nlat)

            # Create slice object for lat direction for this chunk
            jslice = slice(j, jj)

            self.outfile.variables['depth'][jslice,:] = \
                  self.infile.variables['hz'][jslice,:]

    def run(self, start, stop, step):
        """Run tidal model from start to stop with a given step (seconds)."""
        logging.info('Running from %s to %s with step %ss' % \
                     (start, stop, step))

        # Calculate timesteps
        trange = int((stop - start).total_seconds())
        nsteps = int(trange / step) + 1
        timesteps = []
        for i in range(nsteps):
            timestep = start + datetime.timedelta(seconds=i * step)
            timesteps.append(timestep)

        # Set time units attribute in output file to the first timestep
        outfile = self.outfile
        nctm = outfile.variables['time']
        tunits = start.strftime('%Y-%m-%d %H:%M:%S')
        nctm.setncattr('units', "hours since %s" % tunits)
        nctm.setncattr('calendar', 'standard')

        # Number of constituents
        ncon = len(self.constids)

        # Lats and lons
        lat = self.lat
        lon = self.lon
        nlat = self.nlat
        nlon = self.nlon
        nlat_chunk = self.nlat_chunk

        # Prepare various time dependent parameters and write timesteps to
        # NetCDF file
        mjd_list = []
        A_list = []
        fc_list = []
        fs_list = []
        for itime, timestep in enumerate(timesteps):
            # Write timestep in hours to NetCDF file
            outfile.variables['time'][itime] = itime * step / 3600.0

            # Calculate Mean Julian Day from timestep
            atime = Time(timestep, format='datetime', scale='ut1')
            mjd = atime.mjd
            mjd_list.append(mjd)
            logging.info('Writing timestep information %s (MJD=%s)' % \
                         (timestep, mjd))

            logging.info('Calculating prediction coefficient matrices at '
                         '%s (MJD=%s)' % (timestep, mjd))
            A = tideutils.nodal_A(mjd, self.constids)
            A_list.append(A)

            logging.info('Calculating corrections for minor constituents at '
                         '%s (MJD=%s)' % (timestep, mjd))
            fc, fs = tideutils.fac_minor(mjd)
            fc_list.append(fc)
            fs_list.append(fs)

        # The processing is split up into chunks
        # to limit memory consumption and prepare for future parallellization
        for j in range(0, nlat, nlat_chunk):
            # Calculate end index
            jj = min(j + nlat_chunk, nlat)

            logging.info('Calculating tidal prediction for latitude index '
                         'range %s to %s of %s' % (j, jj, nlat))

            # Create slice object for lat direction for this chunk
            jslice = slice(j, jj)

            # Read in bathymetry
            #depths = self.infile.variables['hz'][jslice,:]
            depths = np.ma.array(read_real_chunk(self.infile, 'hz', jslice))

            # Calculate inverse depth for current calculations
            if 'u' in self.outputs or 'v' in self.outputs:
                depths_inv = 1.0 / depths

            # Read in elevations.
            if 'z' in self.outputs:
                # Read in elevation constituents from NetCDF file
                h = np.ma.empty((ncon, jj - j, nlon), dtype=np.complex)
                for k, constid in enumerate(self.constids):
                    # Read in elevation values and convert from mm to m
                    h[k] = read_complex_chunk(self.infile, ['hRe', 'hIm'],
                                              jslice, k)
                ptideH = tideutils.Ptide(h, self.constids,
                                         self.interpolate_minor)

            # Loop over timesteps. For performance reasons it is beneficial to
            # process each parameter in a separate loop (contiguous disk writes)
            if 'z' in self.outputs:
                for itime in range(len(timesteps)):
                    # Calculate elevation
                    hout = ptideH(fc_list[itime], fs_list[itime],
                                  A_list[itime])
                    write_chunk(outfile, 'z', itime, jslice, hout)

            if 'u' in self.outputs or 'U' in self.outputs:
                # Read in u-transport constituents from NetCDF file
                U = np.ma.empty((ncon, jj - j, nlon), dtype=np.complex)
                for k in range(ncon):
                    # Read in u-transport values (m**2/s)
                    U[k] = read_complex_chunk(self.infile, ['uRe', 'uIm'],
                                              jslice, k)

            if 'v' in self.outputs or 'V' in self.outputs:
                # Read in v-transport constituents from NetCDF file
                V = np.ma.empty((ncon, jj - j, nlon), dtype=np.complex)
                for k in range(ncon):
                    # Read in v-transport values (m**2/s)
                    V[k] = read_complex_chunk(self.infile, ['vRe', 'vIm'],
                                              jslice, k)

            # Limit suspicious constituents before running model
            if 'u' in self.outputs or 'U' in self.outputs:
                #U, V = limit_suspicious_constituents(U, V, depths)
                ptideU = tideutils.Ptide(U, self.constids,
                                         self.interpolate_minor)
                ptideV = tideutils.Ptide(V, self.constids,
                                         self.interpolate_minor)

            if 'u' in self.outputs or 'U' in self.outputs:
                for itime in range(len(timesteps)):
                    # Calculate velocity and transport
                    Uout = ptideU(fc_list[itime], fs_list[itime],
                                  A_list[itime])
                    if 'U' in self.outputs:
                        write_chunk(outfile, 'U', itime, jslice, Uout)
                    if 'u' in self.outputs:
                        uout = Uout * depths_inv
                        write_chunk(outfile, 'u', itime, jslice, uout)

            if 'v' in self.outputs or 'V' in self.outputs:
                for itime in range(len(timesteps)):
                    # Calculate velocity and transport
                    Vout = ptideV(fc_list[itime], fs_list[itime],
                                  A_list[itime])
                    if 'V' in self.outputs:
                        write_chunk(outfile, 'V', itime, jslice, Vout)
                    if 'v' in self.outputs:
                        vout = Vout * depths_inv
                        write_chunk(outfile, 'v', itime, jslice, vout)

        # Close NetCDF output file
        outfile.close()


def read_real_chunk(ncfile, ncvar, jslice):
    return ncfile.variables[ncvar][jslice, :]


def read_complex_chunk(ncfile, ncvars, jslice, k):
    value = np.ma.array(
        ncfile.variables[ncvars[0]][k, jslice, :], dtype=np.complex)
    value += ncfile.variables[ncvars[1]][k, jslice, :] * 1.0j
    return value


def write_chunk(ncfile, ncvar, itime, jslice, hout):
    # Write elevations to NetCDF file
    ncfile.variables[ncvar][itime, jslice, :] = hout


def limit_suspicious_constituents(U, V, depths, maxnorm=4.0):
    """\
   Finds the summed norm of the complex transport constituents
   and divides it by the depth to find the summed current speed.
   
   The transport constituents are then capped at a current speed
   of 1 m/s.
   """
    # Find norm at each grid point
    #norm = 0.25*(np.ma.sqrt(np.ma.sqrt(U.real**2).sum(axis=0)**2 + \
    #                        np.ma.sqrt(U.imag**2).sum(axis=0)**2) + \
    #             np.ma.sqrt(np.ma.sqrt(V.real**2).sum(axis=0)**2 + \
    #                        np.ma.sqrt(V.imag**2).sum(axis=0)**2))
    #print((U.real**2 + U.imag**2 + V.real**2 + V.imag**2).shape)
    norm = 0.25 * np.ma.sqrt(
        (U.real**2 + U.imag**2 + V.real**2 + V.imag**2).sum(axis=0))

    # Assert that masks of norm and depths are identical
    assert np.array_equal(np.ma.getmaskarray(norm),
            np.ma.getmaskarray(depths)), \
            'Depth input and transport constituent input must have same masks'

    # Normalize with depth
    norm = norm / depths

    # 1.0/norm but we only set the values where we use them
    norm_inv = np.ma.empty(norm.shape)

    # Suspicious values where norm >= maxnorm. Normalize these values
    inorm = np.ma.where(norm >= maxnorm)

    if len(inorm[0]) > 0:
        points = [(x[0], x[1], depths[x[0], x[1]])
                  for x in zip(inorm[0], inorm[1])]
        logging.info('Limiting transports at (j, i, z): %s' % points)
        logging.info('Maximum norm before limiter: %s' % norm.max())
    nconstit = U.shape[0]
    UVtmp = np.ma.empty(U.shape[1:], dtype=U.dtype)
    norm_inv[inorm] = 1.0 / norm[inorm]
    for i in range(nconstit):
        UVtmp = np.ma.array(U[i], copy=True)
        UVtmp[inorm] = UVtmp[inorm] * norm_inv[inorm]
        U[i, :] = UVtmp[:]
        UVtmp = np.ma.array(V[i], copy=True)
        UVtmp[inorm] = UVtmp[inorm] * norm_inv[inorm]
        V[i, :] = UVtmp[:]

    if len(inorm[0]) > 0:
        norm = 0.25 * np.ma.sqrt(
            (U.real**2 + U.imag**2 + V.real**2 + V.imag**2).sum(axis=0))
        norm = norm / depths
        logging.info('Maximum norm after limiter: %s' % norm.max())

    return U, V
