#!/usr/bin/env python3
"""
Script for predicting tides on a global grid
"""
# Standard library imports
import argparse
import datetime
import logging
import os
import sys

# External imports
from configobj import ConfigObj

# Local imports
from tidal_prediction.tide import tidemodel

def main():
    """Run tidal model."""
    #usage='usage: %prog [options] cfgfile start stop'
    parser = argparse.ArgumentParser()
    parser.add_argument('cfgfile', help='Configuration file name')
    parser.add_argument('outfile', help='Output NetCDF file')
    parser.add_argument('start', help='Start time (%%Y%%m%%d[%%H%%M%%S])')
    parser.add_argument('stop', help='Stop time (%%Y%%m%%d[%%H%%M%%S])')
    parser.add_argument('step', help='Timestep (seconds)')
    args = parser.parse_args()

    outfile = args.outfile
    cfgfile = args.cfgfile
    try:
        start = datetime.datetime.strptime(args.start, '%Y%m%d%H%M%S')
    except ValueError:
        start = datetime.datetime.strptime(args.start, '%Y%m%d')
    try:
        stop = datetime.datetime.strptime(args.stop, '%Y%m%d%H%M%S')
    except ValueError:
        stop = datetime.datetime.strptime(args.stop, '%Y%m%d')
    step = int(args.step)

    # Log to stdout
    logging.basicConfig(level=logging.INFO,
                       format='%(asctime)s %(levelname)s %(message)s',
                       datefmt='%Y-%m-%dT%H:%M:%S')

    # Check if configuration file exists
    if not os.path.exists(cfgfile):
        raise IOError('File not found: %s' % cfgfile)

    # Read in configuration
    cfg = ConfigObj(cfgfile, unrepr=True, interpolation=True)

    # Run model
    model = tidemodel.Model(outfile, cfg)
    model.run(start, stop, step)

if __name__ == '__main__':
    main()
