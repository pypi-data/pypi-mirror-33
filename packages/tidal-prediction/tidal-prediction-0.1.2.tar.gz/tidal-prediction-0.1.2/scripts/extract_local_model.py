#!/usr/bin/env python3
"""
Interpolates the tpxo8-atlas compact NetCDF files (elevations, transports and 
bathymetry) and outputs the model in NetCDF format to a user specified regular
grid. The output is written to an unstaggered grid.

The input files contain a global model in 1/6 degree resolution and local
models in 1/30 degree resolution.
"""

# Standard library imports
import argparse
import logging
import os

# External imports
from configobj import ConfigObj
import netCDF4
import numpy as np

# Local imports
from tidal_prediction.convert import io_nc


def addcyclic(arrin,lonsin):
    """
    ``arrout, lonsout = addcyclic(arrin, lonsin)``
    adds cyclic (wraparound) point in longitude to ``arrin`` and ``lonsin``,
    assumes longitude is the right-most dimension of ``arrin``.
    """
    nlons = arrin.shape[-1]
    newshape = list(arrin.shape)
    newshape[-1] += 1
    if np.ma.isMA(arrin):
        arrout  = np.ma.zeros(newshape,arrin.dtype)
    else:
        arrout  = np.zeros(newshape,arrin.dtype)
    arrout[...,0:nlons] = arrin[:]
    arrout[...,nlons] = arrin[...,0]
    if np.ma.isMA(lonsin):
        lonsout = np.ma.zeros(nlons+1,lonsin.dtype)
    else:
        lonsout = np.zeros(nlons+1,lonsin.dtype)
    lonsout[0:nlons] = lonsin[:]
    lonsout[nlons]  = lonsin[-1] + lonsin[1]-lonsin[0]
    return arrout,lonsout


def interp(datain,xin,yin,xout,yout,checkbounds=False,masked=False,order=1):
    """
    Interpolate data (``datain``) on a rectilinear grid (with x = ``xin``
    y = ``yin``) to a grid with x = ``xout``, y= ``yout``.

    .. tabularcolumns:: |l|L|

    ==============   ====================================================
    Arguments        Description
    ==============   ====================================================
    datain           a rank-2 array with 1st dimension corresponding to
                     y, 2nd dimension x.
    xin, yin         rank-1 arrays containing x and y of
                     datain grid in increasing order.
    xout, yout       rank-2 arrays containing x and y of desired output grid.
    ==============   ====================================================

    .. tabularcolumns:: |l|L|

    ==============   ====================================================
    Keywords         Description
    ==============   ====================================================
    checkbounds      If True, values of xout and yout are checked to see
                     that they lie within the range specified by xin
                     and xin.
                     If False, and xout,yout are outside xin,yin,
                     interpolated values will be clipped to values on
                     boundary of input grid (xin,yin)
                     Default is False.
    masked           If True, points outside the range of xin and yin
                     are masked (in a masked array).
                     If masked is set to a number, then
                     points outside the range of xin and yin will be
                     set to that number. Default False.
    order            0 for nearest-neighbor interpolation, 1 for
                     bilinear interpolation (default 1).
    ==============   ====================================================

    .. note::
     If datain is a masked array and order=1 (bilinear interpolation) is
     used, elements of dataout will be masked if any of the four surrounding
     points in datain are masked.  To avoid this, do the interpolation in two
     passes, first with order=1 (producing dataout1), then with order=0
     (producing dataout2).  Then replace all the masked values in dataout1
     with the corresponding elements in dataout2 (using numpy.where).
     This effectively uses nearest neighbor interpolation if any of the
     four surrounding points in datain are masked, and bilinear interpolation
     otherwise.

    Returns ``dataout``, the interpolated data on the grid ``xout, yout``.
    """
    # xin and yin must be monotonically increasing.
    if xin[-1]-xin[0] < 0 or yin[-1]-yin[0] < 0:
        raise ValueError('xin and yin must be increasing!')
    if xout.shape != yout.shape:
        raise ValueError('xout and yout must have same shape!')
    # check that xout,yout are
    # within region defined by xin,yin.
    if checkbounds:
        if xout.min() < xin.min() or \
           xout.max() > xin.max() or \
           yout.min() < yin.min() or \
           yout.max() > yin.max():
            raise ValueError('yout or xout outside range of yin or xin')
    # compute grid coordinates of output grid.
    delx = xin[1:]-xin[0:-1]
    dely = yin[1:]-yin[0:-1]
    if max(delx)-min(delx) < 1.e-4 and max(dely)-min(dely) < 1.e-4:
        # regular input grid.
        xcoords = (len(xin)-1)*(xout-xin[0])/(xin[-1]-xin[0])
        ycoords = (len(yin)-1)*(yout-yin[0])/(yin[-1]-yin[0])
    else:
        # irregular (but still rectilinear) input grid.
        xoutflat = xout.flatten(); youtflat = yout.flatten()
        ix = (np.searchsorted(xin,xoutflat)-1).tolist()
        iy = (np.searchsorted(yin,youtflat)-1).tolist()
        xoutflat = xoutflat.tolist(); xin = xin.tolist()
        youtflat = youtflat.tolist(); yin = yin.tolist()
        xcoords = []; ycoords = []
        for n,i in enumerate(ix):
            if i < 0:
                xcoords.append(-1) # outside of range on xin (lower end)
            elif i >= len(xin)-1:
                xcoords.append(len(xin)) # outside range on upper end.
            else:
                xcoords.append(float(i)+(xoutflat[n]-xin[i])/(xin[i+1]-xin[i]))
        for m,j in enumerate(iy):
            if j < 0:
                ycoords.append(-1) # outside of range of yin (on lower end)
            elif j >= len(yin)-1:
                ycoords.append(len(yin)) # outside range on upper end
            else:
                ycoords.append(float(j)+(youtflat[m]-yin[j])/(yin[j+1]-yin[j]))
        xcoords = np.reshape(xcoords,xout.shape)
        ycoords = np.reshape(ycoords,yout.shape)
    # data outside range xin,yin will be clipped to
    # values on boundary.
    if masked:
        xmask = np.logical_or(np.less(xcoords,0),np.greater(xcoords,len(xin)-1))
        ymask = np.logical_or(np.less(ycoords,0),np.greater(ycoords,len(yin)-1))
        xymask = np.logical_or(xmask,ymask)
    xcoords = np.clip(xcoords,0,len(xin)-1)
    ycoords = np.clip(ycoords,0,len(yin)-1)
    # interpolate to output grid using bilinear interpolation.
    if order == 1:
        xi = xcoords.astype(np.int32)
        yi = ycoords.astype(np.int32)
        xip1 = xi+1
        yip1 = yi+1
        xip1 = np.clip(xip1,0,len(xin)-1)
        yip1 = np.clip(yip1,0,len(yin)-1)
        delx = xcoords-xi.astype(np.float32)
        dely = ycoords-yi.astype(np.float32)
        dataout = (1.-delx)*(1.-dely)*datain[yi,xi] + \
                  delx*dely*datain[yip1,xip1] + \
                  (1.-delx)*dely*datain[yip1,xi] + \
                  delx*(1.-dely)*datain[yi,xip1]
    elif order == 0:
        xcoordsi = np.around(xcoords).astype(np.int32)
        ycoordsi = np.around(ycoords).astype(np.int32)
        dataout = datain[ycoordsi,xcoordsi]
    else:
        raise ValueError('order keyword must be 0 or 1')
    if masked and isinstance(masked,bool):
        dataout = np.ma.masked_array(dataout)
        newmask = np.ma.mask_or(np.ma.getmask(dataout), xymask)
        dataout = np.ma.masked_array(dataout,mask=newmask)
    elif masked and is_scalar(masked):
        dataout = np.where(xymask,masked,dataout)
    return dataout


def init_outfile(dataset, constituents, lon, lat):
    """\
    Initialize output file.
    """

    # Names for latitudes and longitudes
    lat_name = 'lat'
    lon_name = 'lon'

    # Define dimensions for group
    dataset.createDimension(lat_name, len(lat))
    dataset.createDimension(lon_name, len(lon))

    # Define dimensional variables
    nclat = dataset.createVariable(lat_name, np.float32, (lat_name),
                                   zlib=True, complevel=1)
    nclon = dataset.createVariable(lon_name, np.float32, (lon_name),
                                   zlib=True, complevel=1)

    # Set attributes for dimensional variables
    nclat.setncattr('long_name', 'latitude')
    nclat.setncattr('units', 'degrees_north')
    nclon.setncattr('long_name', 'longitude')
    nclon.setncattr('units', 'degrees_east')

    # Fill in values for dimensional variables
    nclon[:] = lon
    nclat[:] = lat

    # Constituents
    con_name = 'constituents'
    dataset.createDimension(con_name, len(constituents))
    nccon = dataset.createVariable(con_name, str, (con_name))
    for i in range(len(constituents)):
        nccon[i] = constituents[i]
    nccon.setncattr('long_name', 'constituent names')

    # We encode the variables as 16-bit integers 
    out_type = 'i2'
    fill_value = netCDF4.default_fillvals[out_type]  # 'i2': -32767

    # Elevation constituents
    scale_factor = 0.00025 # Values are up to +/- ~10
    hre_name = 'hRe'
    him_name = 'hIm'
    nc_hre = dataset.createVariable(hre_name, out_type, (con_name, lat_name,
                                    lon_name), fill_value=fill_value,
                                    zlib=True, complevel=1)
    nc_hre.setncattr('long_name', 'Tidal elevation complex amplitude, Real part')
    nc_hre.setncattr('units', 'm')
    nc_hre.setncattr('field',
      'Re(z), scalar, amp=abs(hRe+i*hIm);GMT phase=atan2(-hIm,hRe)/pi*180;')
    nc_hre.setncattr('add_offset', 0.0)
    nc_hre.setncattr('scale_factor', scale_factor)

    nc_him = dataset.createVariable(him_name, out_type, (con_name, lat_name,
                                    lon_name), fill_value=fill_value,
                                    zlib=True, complevel=1)
    nc_him.setncattr('long_name', 'Tidal elevation complex amplitude, Real part')
    nc_him.setncattr('units', 'm')
    nc_him.setncattr('field', 'Im(z), scalar')
    nc_him.setncattr('add_offset', 0.0)
    nc_him.setncattr('scale_factor', scale_factor)

    # Depth
    depth_name = 'hz'
    scale_factor = 0.25 # Values are from 0 to ~10000
    ncdepth = dataset.createVariable(depth_name, out_type, (lat_name,
                                     lon_name), fill_value=fill_value,
                                     zlib=True, complevel=1)
    ncdepth.setncattr('standard_name', 'depth')
    ncdepth.setncattr('long_name', 'Bathymetry')
    ncdepth.setncattr('units', 'm')
    ncdepth.setncattr('add_offset', 5000.0)
    ncdepth.setncattr('scale_factor', scale_factor)

    # Transport constituents
    scale_factor = 0.075 # Values are up to +/- ~2000

    ure_name = 'uRe'
    uim_name = 'uIm'
    vre_name = 'vRe'
    vim_name = 'vIm'

    nc_ure = dataset.createVariable(ure_name, out_type, (con_name, lat_name, lon_name),
                                    fill_value=fill_value, zlib=True, complevel=1)
    nc_ure.setncattr('long_name', 'Tidal WE transport complex amplitude, Real part')
    nc_ure.setncattr('units', 'm^2/sec')
    nc_ure.setncattr('field',
      'Re(u), scalar, amp=abs(uRe+i*uIm);GMT phase=atan2(-uIm,uRe)/pi*180;')
    nc_ure.setncattr('add_offset', 0.0)
    nc_ure.setncattr('scale_factor', scale_factor)

    nc_uim = dataset.createVariable(uim_name, out_type, (con_name, lat_name, lon_name),
                                    fill_value=fill_value, zlib=True, complevel=1)
    nc_uim.setncattr('long_name', 'Tidal WE transport complex amplitude, Imag part')
    nc_uim.setncattr('units', 'm^2/sec')
    nc_uim.setncattr('field',
      'Im(u), scalar, amp=abs(uRe+i*uIm);GMT phase=atan2(-uIm,uRe)/pi*180;')
    nc_uim.setncattr('add_offset', 0.0)
    nc_uim.setncattr('scale_factor', scale_factor)

    nc_vre = dataset.createVariable(vre_name, out_type, (con_name, lat_name, lon_name),
                                    fill_value=fill_value, zlib=True, complevel=1)
    nc_vre.setncattr('long_name', 'Tidal SN transport complex amplitude, Real part')
    nc_vre.setncattr('units', 'm^2/sec')
    nc_vre.setncattr('field',
      'Re(v), scalar, amp=abs(vRe+i*vIm);GMT phase=atan2(-vIm,vRe)/pi*180;')
    nc_vre.setncattr('add_offset', 0.0)
    nc_vre.setncattr('scale_factor', scale_factor)

    nc_vim = dataset.createVariable(vim_name, out_type, (con_name, lat_name, lon_name),
                                    fill_value=fill_value, zlib=True, complevel=1)
    nc_vim.setncattr('long_name', 'Tidal SN transport complex amplitude, Imag part')
    nc_vim.setncattr('units', 'm^2/sec')
    nc_vim.setncattr('field',
      'Im(v), scalar, amp=abs(vRe+i*vIm);GMT phase=atan2(-vIm,vRe)/pi*180;')
    nc_vim.setncattr('add_offset', 0.0)
    nc_vim.setncattr('scale_factor', scale_factor)


def cdogrid_read(filename):
    """Return dictionary from cdo grid description"""
    # Does file exist
    if not os.path.isfile(filename):
        sys.exit('ERROR cannot locate cdo grid description')
    # Return grid description 
    cdogrid = np.genfromtxt(filename, delimiter='=', dtype=str)
    griddes = {}
    for i in range(cdogrid.shape[0]):
        griddes[str.strip(cdogrid[i,0])] = str.strip(cdogrid[i,1])

    return griddes


def cdogrid_longitude(griddes):
    """\
    Creates longitude variable from a griddes dictionary.
    Returns None if longitude not present.
    """
    x = None
    if griddes['xfirst'] and griddes['xsize'] and griddes['xinc']:
        x_beg = float(griddes['xfirst'])
        x_inc = float(griddes['xinc'])
        x_num = int(griddes['xsize'])
        x = np.arange(x_beg, x_beg+x_inc*x_num, x_inc)
    return x


def cdogrid_latitude(griddes):
    """\
    Creates latitude variable from a griddes dictionary.
    Returns None if latitude not present.
    """
    y = None
    if griddes['yfirst'] and griddes['ysize'] and griddes['yinc']:
        y_beg = float(griddes['yfirst'])
        y_inc = float(griddes['yinc'])
        y_num = int(griddes['ysize'])
        y = np.arange(y_beg, y_beg+y_inc*y_num, y_inc)
    return y


#@profile
def grow(vals, ia, ib, ni, wi, niter=1, locked_mask=None):
    # define initial mask
    m = vals.mask

    # loop over growth iterations
    for i in range(niter):
        n = np.where(ni[i], True, False)

        # set masked values to 0
        vals = np.where(m, 0, vals)
        if locked_mask is not None: # enforce locked mask
            vals = np.ma.masked_where(locked_mask, vals)

        # add mean value from neighbors in growth zone
        vals[n] +=(vals[ib[n,0], ia[n,0]] + vals[ib[n,1], ia[n,0]] + vals[ib[n,2], ia[n,0]]
                +  vals[ib[n,0], ia[n,1]] + vals[ib[n,1], ia[n,1]] + vals[ib[n,2], ia[n,1]]
                +  vals[ib[n,0], ia[n,2]] + vals[ib[n,1], ia[n,2]] + vals[ib[n,2], ia[n,2]]) * wi[i,n]

        # update mask
        m = np.where(n, False, m)

    vals = np.ma.masked_where(m, vals)

    return vals


#@profile
def grow_weights(mask, niter=1):

    nlat = mask.shape[0]
    nlon = mask.shape[1]
    ni = np.zeros((niter,nlat,nlon))
    wi = np.zeros((niter,nlat,nlon))

    # create arrays of indices
    ia,ib = np.meshgrid(np.arange(0,nlon,1), np.arange(0,nlat,1))

    ia = np.dstack((ia - 1, ia, ia + 1))
    ib = np.dstack((ib - 1, ib, ib + 1))
    ia = np.where(ia < 0, 0, ia)
    ib = np.where(ib < 0, 0, ib)
    ia = np.where(ia > nlon-1, nlon-1, ia)
    ib = np.where(ib > nlat-1, nlat-1, ib)

    for i in range(niter):
        # initialize work arrays
        valw = np.where(mask, 0.0, 1.0)
        valn = np.zeros( (nlat, nlon) )

        # calculate weight
        wi[i] = ( valw[ib[:,:,0], ia[:,:,0]] + valw[ib[:,:,1], ia[:,:,0]] + valw[ib[:,:,2], ia[:,:,0]]
                + valw[ib[:,:,0], ia[:,:,1]] + valw[ib[:,:,1], ia[:,:,1]] + valw[ib[:,:,2], ia[:,:,1]]
                + valw[ib[:,:,0], ia[:,:,2]] + valw[ib[:,:,1], ia[:,:,2]] + valw[ib[:,:,2], ia[:,:,2]] )

        n = np.where(wi[i] < 1, False, True)
        ni[i] = np.where(n, mask, False)

        # update mask
        mask = ~n

    wi = np.where(wi<1.0, 0.001, wi)
    wi = 1.0/wi

    return ia, ib, ni, wi


def interp_chunk(data_in, lon_in, lat_in, lon_out, lat_out, chunksize):
    """Chunked interpolation generator from input grid to output grid."""
    # We process this many latitude rows at a time
    nlat_out = len(lat_out)
    nlon_out = len(lon_out)
    nlat_chunk = int(chunksize / nlon_out)

    # Process input grid one latitude chunk at a time
    for j in range(0, nlat_out, nlat_chunk):
        # Calculate end index for this chunk
        jj = min(j + nlat_chunk, nlat_out)

        # Create slice object for lat direction for this chunk
        jslice = slice(j, jj)
        #logging.info('Processing slice %s' % jslice)
        lat_out_s = lat_out[jslice]

        # Quick exit if lon_out/lat_out does not overlap lon_in/lat_in
        if lon_out[0] > lon_in[-1] or lon_out[-1] < lon_in[0] or \
           lat_out_s[0] > lat_in[-1] or lat_out_s[-1] < lat_in[0]:
            arr_shape = (len(lat_out_s), len(lon_out))
            #print('Quick exit', arr_shape)
            yield jslice, np.ma.masked_values(np.zeros(arr_shape), 0.0)

        lon_chunk, lat_chunk = np.meshgrid(lon_out, lat_out_s)

        # Interpolate global grid to output grid.
        # We use a simple bi-linear interpolation for this.
        data_out = interp(data_in, lon_in, lat_in, lon_chunk,
                lat_chunk, checkbounds=False, masked=True, order=1)
        yield jslice, data_out


def read_ncvars_h(dataset, varh_name):
    lon_z = dataset.variables['lon_z'][:]
    lat_z = dataset.variables['lat_z'][:]
    h = dataset.variables[varh_name][:]
    
    # Shift longitudes and h
    lon_z = np.concatenate((lon_z[-1::] - 360.0, lon_z[:-1]))
    h = np.concatenate((h[:,-1::], h[:,:-1]), axis=1)

    # Reorder h axes from (lon, lat) to (lat, lon)
    h = np.swapaxes(h, 0, 1)

    # Add cyclic longitude point for interpolation
    h, lon_z = addcyclic(h, lon_z)

    return lon_z, lat_z, h


def read_ncvars_u(dataset, varu_name):
    lon_u = dataset.variables['lon_u'][:]
    lat_u = dataset.variables['lat_u'][:]
    u = dataset.variables[varu_name][:]
    
    # Shift longitudes and h
    lon_u = np.concatenate((lon_u[-1::] - 360.0, lon_u[:-1]))
    u = np.concatenate((u[:,-1::], u[:,:-1]), axis=1)

    # Reorder h axes from (lon, lat) to (lat, lon)
    u = np.swapaxes(u, 0, 1)

    # Add two cyclic longitude points for interpolation
    # (the field needs to span 0-360 degrees longitude)
    u, lon_u = addcyclic(u, lon_u)
    u, lon_u = addcyclic(u, lon_u)

    return lon_u, lat_u, u


def read_ncvars_v(dataset, varv_name):
    lon_v = dataset.variables['lon_v'][:]
    lat_v = dataset.variables['lat_v'][:]
    v = dataset.variables[varv_name][:]
    
    # Shift longitudes and v
    lon_v = np.concatenate((lon_v[-1::] - 360.0, lon_v[:-1]))
    v = np.concatenate((v[:,-1::], v[:,:-1]), axis=1)

    # Reorder h axes from (lon, lat) to (lat, lon)
    v = np.swapaxes(v, 0, 1)

    # Add cyclic longitude point for interpolation
    v, lon_v = addcyclic(v, lon_v)

    # Copy northernmost latitude row to allow interpolation up to 90N
    # This will of introduce a small error in the interpolation
    # for points less than ~2 km from the North Pole
    lat_last = lat_v[-1::] + (lat_v[-1] - lat_v[-2])
    lat_v = np.concatenate((lat_v, lat_last))
    v = np.concatenate((v, v[-1::,:]), axis=0)

    return lon_v, lat_v, v


def read_bathy(cfgin, varname):
    # Read input bathymetries at z nodes
    h_in = {}
    for key in cfgin:
        dataset_in = netCDF4.Dataset(cfgin[key]['bathymetry_file'], "r")

        if varname == 'hz':
            # Read depth at z nodes
            lon, lat, h = read_ncvars_h(dataset_in, varname)
        elif varname == 'hu':
            # Read depth at u nodes
            lon, lat, h = read_ncvars_u(dataset_in, varname) 
        elif varname == 'hv':
            # Read depth at v nodes
            lon, lat, h = read_ncvars_v(dataset_in, varname) 
        else:
            raise SystemExit(1)

        # Convert 0 values to masked values before interpolation
        h = np.ma.masked_values(h, 0.0)
    
        h_in[key] = {
            'lon': lon,
            'lat': lat,
            'h': h
        }
    return h_in


#@profile
def process(dataset_out, hz_out, lat_out, lon_out, constituents_out, cfgin, var_names,
            h_in, nchunk, niter, scale, filetype, reader):
    # TODO: This method needs to be refactored into smaller bits
    for i in range(len(constituents_out)):
        constituent_out = constituents_out[i]
        #logging.info('Interpolating tidal constituent %s' % constituent_out)
        for name in cfgin:
            cfgdata = cfgin[name]
            if constituent_out in cfgdata['constituents']:
                file_in = cfgdata[filetype].replace(
                       '{constituent}', constituent_out)
                dataset_in = netCDF4.Dataset(file_in, "r")
                logging.info('Interpolating %s for constituent %s from %s' % \
                        (var_names, constituent_out, file_in))

                for var_name in var_names:
                    logging.debug('Interpolating parameter %s' % var_name)

                    # Interpolate to output grid
                    h_out = dataset_out.variables[var_name]
                
                    # Read input variables
                    lon_z, lat_z, h = reader(dataset_in, var_name)

                    # Mask out land values based on bathymetry input
                    h = np.ma.masked_where(np.ma.getmask(h_in[name]['h']), h)

                    # Interpolate to output grid
                    generator = interp_chunk(h, lon_z, lat_z, lon_out, lat_out,
                            nchunk)
                    for g in generator:
                        jslice, data = g
                        data = scale*data
                        h_out[i,jslice,:] = data

                    # Grow data
                    logging.debug('Extrapolating parameter %s' % (var_name))
                    nlat_out = len(lat_out)
                    nlon_out = len(lon_out)
                    nlat_chunk = int(nchunk / nlon_out)
                    nrem = 0
                    # Process input grid one latitude chunk at a time
                    for j in range(0, nlat_out, nlat_chunk):
                        # Calculate end index for this chunk
                        jj = min(j + nlat_chunk, nlat_out)

                        # Create slice object for lat direction for this chunk
                        jslice = slice(j, jj)

                        # We will however use a halo equal to the number of
                        # iterations on the input data
                        j_in = max(j - niter[name], 0)
                        jj_in = min(jj + niter[name], nlat_out)
                        jslice_in = slice(j_in, jj_in)

                        # Get data including halo
                        data = h_out[i,jslice_in,:]

                        # Convert to masked array if necessary
                        if type(data) != np.ma.core.MaskedArray:
                            data = np.ma.core.MaskedArray(data, np.zeros(
                                    data.shape, dtype = bool))
                        
                        ia, ib, ni, wi = grow_weights(data.mask,
                                niter=niter[name])
                        data = grow(data, ia, ib, ni, wi, niter=niter[name],
                                locked_mask=None)

                        # Apply output bathymetry mask (land-sea mask)
                        mask = hz_out[jslice_in,:]
                        data = np.ma.masked_where(np.ma.getmask(mask), data)

                        # Set remaining values to zero
                        mask_hz = np.ma.getmaskarray(mask)
                        mask_data = np.ma.getmaskarray(data)
                        mask_remaining = np.logical_xor(mask_data, mask_hz)
                        data = np.ma.where(mask_remaining, 0.0, data)
                        nrem += np.sum(mask_remaining)

                        # Check that masks are equal
                        assert np.array_equal(np.ma.getmaskarray(mask),
                                np.ma.getmaskarray(data)), \
                                'Internal error for %s' % name

                        # Write data (excluding halo)
                        jslice_out = slice(j-j_in, jj-j_in)
                        h_out[i,jslice,:] = data[jslice_out,:]
                    
                    # Report if there are points that are not interpolated
                    # or extrapolated.
                    if nrem > 0:
                        logging.info('Setting %s values to 0.0 ' \
                                '(consider increasing niter)' % nrem)

                break


#@profile
def main():
    """\
    Interpolates the tpxo8-atlas compact NetCDF files (elevations, transports
    and bathymetry) and outputs the model in NetCDF format to a user specified
    regular grid. The output is written to an unstaggered grid.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('cfgfile', help='Configuration file name')
    args = parser.parse_args()

    cfgfile = args.cfgfile

    # Log to stdout
    logging.basicConfig(level=logging.INFO,
                       format='%(asctime)s %(levelname)s %(message)s',
                       datefmt='%Y-%m-%dT%H:%M:%S')

    # Check if configuration file exists
    if not os.path.exists(cfgfile):
        raise IOError('File not found: %s' % cfgfile)

    # Read in configuration
    cfg = ConfigObj(cfgfile, unrepr=True, interpolation=True)

    # Read output grid
    cfgout = cfg['output']
    grid_file = cfgout['grid_description_file']
    griddes = cdogrid_read(grid_file)
    lon_out = cdogrid_longitude(griddes)
    lat_out = cdogrid_latitude(griddes)
    nlat_out = len(lat_out)
    nlon_out = len(lon_out)

    # Initialize output NetCDF file
    dataset_out = io_nc.create(cfgout['output_file'])

    constituents_out = cfgout['constituents']
    logging.info('Interpolating constituents: %s' % constituents_out)
    init_outfile(dataset_out, constituents_out, lon_out, lat_out)

    # How much to grow fields for each input dataset
    niter = cfgout['niter']

    # Approximate chunk size to be processed at a time
    nchunk = cfg['computations']['chunksize']

    cfgin = cfg['input']

    # Read input bathymetries at z nodes
    hz_in = read_bathy(cfgin, 'hz')

    # Interpolate bathymetry
    bathy_out = cfgout['bathymetry']

    # Read input bathymetry file
    logging.info('Interpolating bathymetry from %s' % cfgin[bathy_out]['bathymetry_file'])

    # Interpolate to output grid
    hz_out = dataset_out.variables['hz']

    # Interpolate bathymetry to output grid
    hz_in_out = hz_in[bathy_out]
    generator = interp_chunk(hz_in_out['h'], hz_in_out['lon'],
            hz_in_out['lat'], lon_out, lat_out, nchunk)

    # Use a generator for the actual interpolation
    for g in generator:
        jslice, data = g
        hz_out[jslice,:] = data

    # Convert data from mm to m
    scale = 0.001

    # Which section in configuration file to read
    filetype = 'elevations_file'

    # Use this function to read input variables
    reader = read_ncvars_h

    # Interpolate sea level constituents
    process(dataset_out, hz_out, lat_out, lon_out, constituents_out, cfgin,
            ['hRe', 'hIm'], hz_in, nchunk, niter, scale, filetype, reader)

    # Which section in configuration file to read
    filetype = 'transports_file'

    # Convert data from cm**2/s to m**2/s
    scale = 0.0001

    # Read input bathymetries at u nodes
    hu_in = read_bathy(cfgin, 'hu')

    # Use this function to read input variables
    reader = read_ncvars_u

    # Interpolate U-transport constituents
    process(dataset_out, hz_out, lat_out, lon_out, constituents_out, cfgin,
            ['uRe', 'uIm'], hu_in, nchunk, niter, scale, filetype, reader)

    # Read input bathymetries at v nodes
    hv_in = read_bathy(cfgin, 'hv')

    # Use this function to read input variables
    reader = read_ncvars_v

    # Interpolate V-transport constituents
    process(dataset_out, hz_out, lat_out, lon_out, constituents_out, cfgin,
            ['vRe', 'vIm'], hv_in, nchunk, niter, scale, filetype, reader)

    dataset_out.close()

if __name__ == '__main__':
    main()
