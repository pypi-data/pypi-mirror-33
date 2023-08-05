# Python Tidal Prediction Model 

The Python Tidal Prediction Model is a reimplementation of the
[OSU Tidal Prediction Software (OTPS)](http://volkov.oce.orst.edu/tides/otps.html)
by Gary D. Egbert and Lana Erofeeva. The reimplementation has 
been developed with two main goals in mind:

1. Efficient for producing gridded predictions.

2. Predictable and configurable memory usage no matter output grid size.

## Installation

You will need Python 3 to install this software (Python 2 is not supported).
Before installing this software you will also need to install some Python
modules. These are:

```
AstroPy
ConfigObj
netcdf4python
NumPy
```

On Ubuntu these can be installed using the package manager:

```
apt-get install python3-astropy \
                python3-configobj \
                python3-netcdf4 \
                python3-numpy
```

You can also install them using pip3:

```
pip3 install AstroPy ConfigObj netCDF4 NumPy SciPy
```

If you encounter an error when installing SciPy you can try:

```
pip install scipy
```

which has been reported to solve the problem.

Hereafter you clone or download (and unpack) this repository and change
directory to it. You can then install it using:

```
python3 setup.py install
```

This will install the package globally. Please add "--help" to the command
to see how to install it in a separate directory if you only want to test
the package or prefer a different installation directory.

### Development

It is possible to setup the package for development by running:

```
python3 setup.py develop
```

This will install the package but with links to the files in the current
directory.

You can also set it up to run in this directory instead of using the above
command. If you use a bash-like shell you will then need to run:

```
export PYTHONPATH=$(pwd)
```

or if you use csh or similar:

```
setenv PYTHONPATH "`pwd`"
```

to make the required Python modules available. In the usage section you will
have to prepend the commands with "./scripts" or add this directory to your
PATH if you followed this approach.

## Usage

The tidal prediction is based on input files containing the complex elevation
and transport constituents for the M2, S2, N2, K2, O1, P1, Q1, M4, MS4, MN4,
MM and MF tidal constituents from the [OSU Tidal Data Inversion](http://volkov.oce.orst.edu/tides/)
by Gary D. Egbert and Lana Erofeeva.

The first thing you should do is to download these files (several gigabytes):

```
mkdir NCDATA
cd NCDATA
wget -c 'ftp://ftp.oce.orst.edu/dist/tides/TPXO8_atlas_30_v1_nc/*.nc'
```

### Output Grid

Next we need to setup a grid on which to produce the prediction.
Currently only unstaggered regular grids are supported. The grid is defined
using the grid description format used by Climate Data Operators (CDO). An
example file for a global grid is shown here:

```
gridtype = lonlat
xsize = 60
ysize = 30
xfirst = -177
xinc = 6
yfirst = −87
yinc = 6
```

Tip: If you already have a NetCDF file with the desired grid and CDO installed,
then you can run:

```
cdo griddes <netcdf_file>
```

to produce a grid description. Please remember that we currently only support
regular grids.

The next step is to interpolate the tidal constituents in the input files
downloaded previously to this grid. This is done by running the script:

```
extract_local_model.py examples/extract_mercator.cfg
```

You can find a documented [example configuration file](examples/extract_mercator.cfg).
You will most likely only have change some settings in the
"output" section in the file.

This script will only have to be run once for a given grid but it may
take some time to do this. It will output a NetCDF file with the
interpolated constituents. This file must then be used as input for the
tidal prediction described in the next section.

### Tidal Prediction

We are now ready to make a tidal prediction. The first step is to setup
the configuration file for the tidal prediction. To do this please see
the inline documentation in the [example file](examples/tides_mercator.cfg)
provided in this directory.

When this is done we can run the prediction. The tidal prediction script has the
following usage:

```
predict_tide.py --help
usage: predict_tide.py [-h] cfgfile outfile start stop step

positional arguments:
  cfgfile     Configuration file name
  outfile     Output NetCDF file
  start       Start time (%Y%m%d[%H%M%S])
  stop        Stop time (%Y%m%d[%H%M%S])
  step        Timestep (seconds)

optional arguments:
  -h, --help  show this help message and exit
```

The script will output a single NetCDF file with the tidal prediction.

## License

The license can be found in the [LICENSE](LICENSE) file. Furthermore the
extract_local_model.py includes two methods from the Matplotlib Basemap
package. The license for these methods can be found in
[LICENSE.BASEMAP](LICENSE.BASEMAP). The original Fortran
software is licensed under [LICENSE.OTPS.pdf](LICENSE.OTPS.pdf).
