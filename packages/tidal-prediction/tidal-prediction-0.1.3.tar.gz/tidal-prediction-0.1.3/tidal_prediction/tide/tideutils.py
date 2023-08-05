"""
Various tidal calculation utility methods. We always use UTC
decimal MJD for time.

This file has been ported from the original Fortran code written
by Gary Egbert and Lana Erofeeva.
"""
# Standard library imports
import datetime
import math

# External imports
from astropy.time import Time
#import bohrium
import numpy as np

# Local imports
from . import tideconstit


def astrol(mjd):
    """\
    Computes the basic astronomical mean longitudes s, h, p, N.
    Note N is not N', i.e. N is decreasing with time.
    These formulae are for the period 1990 - 2010, and were derived
    by David Cartwright (personal comm., Nov. 1990).
    mjd is UTC in decimal MJD.
    All longitudes returned in degrees.
    """
    circle = 360.0
    t = mjd - 51544.4993

    # Mean longitude of moon
    s = 218.3164 + 13.17639648 * t
    s = s % circle
    if s < 0.0:
        s += circle

    # Mean longitude of sun
    h = 280.4661 + 0.98564736 * t
    h = h % circle
    if h < 0.0:
        h += circle

    # Mean longitude of lunar perigee
    p = 83.3535 + 0.11140353 * t
    p = p % circle
    if p < 0.0:
        p += circle

    # Mean longitude of ascending lunar node
    N = 125.0445 - 0.05295377 * t
    N = N % circle
    if N < 0.0:
        N += circle

    return s, h, p, N


class Astro5:
    """\
    Computes the 5 basic astronomical mean longitudes  s, h, p, N, p'.

    Note N is not N', i.e. N is decreasing with time.

    TIME is UTC in decimal Modified Julian Day (MJD).
    All longitudes returned in degrees.

    R. D. Ray, NASA/GSFC   August 2003

    Most of the formulae for mean longitudes are extracted from 
    Jean Meeus, Astronomical Algorithms, 2nd ed., 1998.  
    Page numbers below refer to this book.

    Note: This routine uses TIME in UT and does not distinguish between
    the subtle differences of UTC, UT1, etc.  This is more than adequate
    for the calculation of these arguments, especially in tidal studies.
    """

    def __init__(self):
        self.tjlast = -1.0

    def __call__(self, mjd):
        circle = 360.0
        # Convert to Julian Day and to Ephemeris Time
        tjd = mjd + 2400000.5
        if abs(tjd - self.tjlast) > 100.0:
            deltat = Deltat()
            self.del_ = deltat(tjd) / 86400.0
            self.tjlast = tjd
        tjd = tjd + self.del_

        # Compute time argument in centuries relative to J2000
        T = (tjd - 2451545.) / 36525.

        # Mean longitude of moon (p.338)
        s = (((-1.53388e-8*T + 1.855835e-6)*T - 1.5786e-3)*T + \
                  481267.88123421)*T + 218.3164477
        s = s % circle

        # Mean elongation of moon (p.338)
        D = (((-8.8445e-9*T + 1.83195e-6)*T - 1.8819e-3)*T + \
                445267.1114034)*T + 297.8501921

        # Mean longitude of sun
        h = s - D
        h = h % circle

        # Mean longitude of lunar perigee (p.343)
        p = ((-1.249172e-5*T - 1.032e-2)*T + 4069.0137287)*T + \
                  83.3532465
        p = p % circle

        # Mean longitude of ascending lunar node (p.144)
        N = ((2.22222e-6*T + 2.0708e-3)*T - 1934.136261)*T + \
                  125.04452
        N = N % circle

        # Mean longitude of solar perigee (Simon et al., 1994)
        pm = 282.94 + 1.7192 * T
        pm = pm % circle

        return s, h, p, N, pm


def polint(xa, ya, n, x):
    """\
    given arrays xa and ya of length n and a value x, this routine returns a 
    value y and an error estimate dy. if p(x) is the polynomial of degree n-1
    such that ya = p(xa) ya then the returned value is y = p(x) 

    input:
    xa(0:n-1) = array of x values
    ya(0:n-1) = array of y values
    n       = order of interpolant, 2=linear, 3=quadratic ...
    x       = x value where interpolation is desired

    output:
    y       = interpolated y value
    dy      = error esimate
    """
    nmax = 10

    # Find the index ns of the closest table entry; initialize the c and d tables
    ns = 0
    dif = abs(x - xa[0])
    c = np.empty((nmax), dtype=np.float64)
    d = np.empty((nmax), dtype=np.float64)
    for i in range(n):
        dift = abs(x - xa[i])
        if dift < dif:
            ns = i
            dif = dift
        c[i] = ya[i]
        d[i] = ya[i]

    # First guess for y
    y = ya[ns]

    # For each column of the table, loop over the c's and d's and update them
    ns = ns - 1
    for m in range(1, n):
        for i in range(n - m):
            ho = xa[i] - x
            hp = xa[i + m] - x
            w = c[i + 1] - d[i]
            den = ho - hp
            assert den != 0.0, '2 xa entries are the same in polint'
            den = w / den
            d[i] = hp * den
            c[i] = ho * den

        # After each column is completed, decide which correction c or d, to add
        # to the accumulating value of y, that is, which path to take in the table
        # by forking up or down. ns is updated as we go to keep track of where we
        # are. the last dy added is the error indicator.
        if 2 * ns < n - m:
            dy = c[ns + 1]
        else:
            dy = d[ns]
            ns = ns - 1
        y = y + dy
    return y, dy


class Deltat:
    """\
    This routine computes the difference between 
    universal time and dynamical time.

    tjd  = UT julian day number

    Returns
    deltat = ET - UT in seconds

    Original author: F X Timmes, University of Chicago

    Slightly revised by R Ray, GSFC, Aug 2003.  Also updated table.
    Updated periodically the tables.  -RDR
    """

    # Parameter mp determines the order of the interpolatant
    # when interpolating in the table. mp=2=linear mp=3=quadratic and so on.
    # don't be too greedy about the order of the interpolant since
    # for many years the data is flat, and trying to fit anything other
    # that a line will produce unwanted oscillations. thus i choose mp=2.
    mp = 2

    # These tables of observed and extrapolated data are
    # are from the us naval observatory ftp://maia.usno.navy.mil/ser7/
    # years 1620 to 1710
    # years 1711 to 1799
    # years 1800 to 1890
    # years 1890 to 1979
    # years 1980 to 2015
    # Values up to and including 2011 are OK; 2012 and after
    # are are extrapolated.
    # 2012 to 2015-01-01 from file deltat.data
    # Dates after 2015-01-01 to be linearly extrapolated by
    # (dt_2015-dt_2010)/dy/5
    tabstart = 1620
    tabend = 2015
    tabsize = tabend - tabstart + 1
    dt = [
        124.00, 119.00, 115.00, 110.00, 106.00, 102.00, 98.00, 95.00, 91.00,
        88.00, 85.00, 82.00, 79.00, 77.00, 74.00, 72.00, 70.00, 67.00, 65.00,
        63.00, 62.00, 60.00, 58.00, 57.00, 55.00, 54.00, 53.00, 51.00, 50.00,
        49.00, 48.00, 47.00, 46.00, 45.00, 44.00, 43.00, 42.00, 41.00, 40.00,
        38.00, 37.00, 36.00, 35.00, 34.00, 33.00, 32.00, 31.00, 30.00, 28.00,
        27.00, 26.00, 25.00, 24.00, 23.00, 22.00, 21.00, 20.00, 19.00, 18.00,
        17.00, 16.00, 15.00, 14.00, 14.00, 13.00, 12.00, 12.00, 11.00, 11.00,
        10.00, 10.00, 10.00, 9.00, 9.00, 9.00, 9.00, 9.00, 9.00, 9.00, 9.00,
        9.00, 9.00, 9.00, 9.00, 9.00, 9.00, 9.00, 9.00, 10.00, 10.00, 10.00,
        10.00, 10.00, 10.00, 10.00, 10.00, 10.00, 11.00, 11.00, 11.00, 11.00,
        11.00, 11.00, 11.00, 11.00, 11.00, 11.00, 11.00, 11.00, 11.00, 11.00,
        11.00, 11.00, 11.00, 12.00, 12.00, 12.00, 12.00, 12.00, 12.00, 12.00,
        12.00, 12.00, 12.00, 13.00, 13.00, 13.00, 13.00, 13.00, 13.00, 13.00,
        14.00, 14.00, 14.00, 14.00, 14.00, 14.00, 14.00, 15.00, 15.00, 15.00,
        15.00, 15.00, 15.00, 15.00, 16.00, 16.00, 16.00, 16.00, 16.00, 16.00,
        16.00, 16.00, 16.00, 16.00, 17.00, 17.00, 17.00, 17.00, 17.00, 17.00,
        17.00, 17.00, 17.00, 17.00, 17.00, 17.00, 17.00, 17.00, 17.00, 17.00,
        17.00, 16.00, 16.00, 16.00, 16.00, 15.00, 15.00, 14.00, 14.00, 13.70,
        13.40, 13.10, 12.90, 12.70, 12.60, 12.50, 12.50, 12.50, 12.50, 12.50,
        12.50, 12.50, 12.50, 12.50, 12.50, 12.50, 12.40, 12.30, 12.20, 12.00,
        11.70, 11.40, 11.10, 10.60, 10.20, 9.60, 9.10, 8.60, 8.00, 7.50, 7.00,
        6.60, 6.30, 6.00, 5.80, 5.70, 5.60, 5.60, 5.60, 5.70, 5.80, 5.90, 6.10,
        6.20, 6.30, 6.50, 6.60, 6.80, 6.90, 7.10, 7.20, 7.30, 7.40, 7.50, 7.60,
        7.70, 7.70, 7.80, 7.80, 7.88, 7.82, 7.54, 6.97, 6.40, 6.02, 5.41, 4.10,
        2.92, 1.82, 1.61, 0.10, -1.02, -1.28, -2.69, -3.24, -3.64, -4.54,
        -4.71, -5.11, -5.40, -5.42, -5.20, -5.46, -5.46, -5.79, -5.63, -5.64,
        -5.80, -5.66, -5.87, -6.01, -6.19, -6.64, -6.44, -6.47, -6.09, -5.76,
        -4.66, -3.74, -2.72, -1.54, -0.2, 1.24, 2.64, 3.86, 5.37, 6.14, 7.75,
        9.13, 10.46, 11.53, 13.36, 14.65, 16.01, 17.20, 18.24, 19.06, 20.25,
        20.95, 21.16, 22.25, 22.41, 23.03, 23.49, 23.62, 23.86, 24.49, 24.34,
        24.08, 24.02, 24.00, 23.87, 23.95, 23.86, 23.93, 23.73, 23.92, 23.96,
        24.02, 24.33, 24.83, 25.30, 25.70, 26.24, 26.77, 27.28, 27.78, 28.25,
        28.71, 29.15, 29.57, 29.97, 30.36, 30.72, 31.07, 31.35, 31.68, 32.18,
        32.68, 33.15, 33.59, 34.00, 34.47, 35.03, 35.73, 36.54, 37.43, 38.29,
        39.20, 40.18, 41.17, 42.23, 43.37, 44.49, 45.48, 46.46, 47.52, 48.53,
        49.59, 50.54, 51.38, 52.17, 52.96, 53.79, 54.34, 54.87, 55.32, 55.82,
        56.30, 56.86, 57.57, 58.31, 59.12, 59.98, 60.78, 61.63, 62.29, 62.97,
        63.47, 63.83, 64.09, 64.30, 64.47, 64.57, 64.69, 64.85, 65.15, 65.46,
        65.78, 66.07, 66.32, 66.60, 66.91, 67.28, 67.64
    ]

    # If this is the first time the method is called, initialize
    # put the julian date at the first of the year in the array
    # years so that we can interpolate/extrapolate directly on
    # the given ut julian date
    years = np.empty((tabsize), dtype=np.float64)
    for i in range(tabsize):
        j = (tabstart - 1) + i
        years[i] = Time(
            datetime.datetime(j, 1, 1, 0, 0, 0),
            format='datetime',
            scale='ut1').jd1

    def __call__(self, tjd):
        # Convert the given ut julian date to a ut calendar date
        t = Time(tjd, format='jd')
        td = t.to_datetime()
        iy = td.year

        # If we are outside the table on the low end
        # use the stephenson and morrison expression 948 to 1600,
        # and the borkowski formula for earlier years

        if iy < self.tabstart:
            if iy >= 948:
                b = 0.01 * float(iy - 2000)
                secdif = b * (b * 23.58 + 100.3) + 101.6
            else:
                b = 0.01 * float(iy - 2000) + 3.75
                secdif = 35.0 * b * b + 40.0
        elif iy > self.tabend:
            # If we are outside the table on the high end
            # use a linear extrapolation into the future
            b = float(iy - self.tabend)
            secdif = self.dt[self.tabsize - 1] + b * 0.2 * (
                self.dt[self.tabsize - 1] - self.dt[self.tabsize - 6])
        else:
            # Otherwise we are in the table
            # get the table location and interpolate
            iat = iy - self.tabstart
            iat = int(
                max(0, min(iat - self.mp / 2 + 1, self.tabsize - self.mp)))
            secdif, dy = polint(self.years[iat:iat + self.mp],
                                self.dt[iat:iat + self.mp], self.mp, tjd)

        # The astronomical almanac table is corrected by adding the expression
        #       -0.000091 (ndot + 26)(year-1955)^2  seconds
        # to entries prior to 1955 (page K8), where ndot is the secular tidal
        # term in the mean motion of the moon. entries after 1955 are referred
        # to atomic time standards and are not affected by errors in lunar
        # or planetary theory.  a value of ndot = -25.8 arcsec per century squared
        # is the value used in jpl's de403 ephemeris, the earlier de200 ephemeris
        # used the value -23.8946. note for years below the table (less than 1620)
        # the time difference is not adjusted for small improvements in the
        # current estimate of ndot because the formulas were derived from
        # studies of ancient eclipses and other historical information, whose
        # interpretation depends only partly on ndot.
        # here we make the ndot correction.
        if iy < 1955:
            b = float(iy - 1955)
            secdif = secdif - 0.000091 * (-25.8 + 26.0) * b * b

        # Add the difference to the ut julian date to get the dynamical julian date
        # tjde = tjd + secdif/86400.0

        return secdif


def fac_minor(mjd):
    """\
    Returns correction factors for 18 minor constituents based on input
    time.
    """
    rad = math.pi / 180.0
    PP = 282.8

    hour = (mjd - int(mjd)) * 24.0
    t1 = 15.0 * hour
    t2 = 30.0 * hour

    S, H, P, omega = astrol(mjd)

    arg = np.empty((18), dtype=np.float64)
    arg[0] = t1 - 4. * S + H + 2. * P - 90.  # 2Q1
    arg[1] = t1 - 4. * S + 3. * H - 90.  # sigma1
    arg[2] = t1 - 3. * S + 3. * H - P - 90.  # rho1
    arg[3] = t1 - S + H - P + 90.  # M1
    arg[4] = t1 - S + H + P + 90.  # M1
    arg[5] = t1 - S + 3. * H - P + 90.  # chi1
    arg[6] = t1 - 2. * H + PP - 90.  # pi1
    arg[7] = t1 + 3. * H + 90.  # phi1
    arg[8] = t1 + S - H + P + 90.  # theta1
    arg[9] = t1 + S + H - P + 90.  # J1
    arg[10] = t1 + 2. * S + H + 90.  # OO1
    arg[11] = t2 - 4. * S + 2. * H + 2. * P  # 2N2
    arg[12] = t2 - 4. * S + 4. * H  # mu2
    arg[13] = t2 - 3. * S + 4. * H - P  # nu2
    arg[14] = t2 - S + P + 180.  # lambda2
    arg[15] = t2 - S + 2. * H - P + 180.  # L2
    arg[16] = t2 - S + 2. * H + P  # L2
    arg[17] = t2 - H + PP  # t2

    # Determine nodal corrections f and u
    sinn = math.sin(omega * rad)
    cosn = math.cos(omega * rad)
    sin2n = math.sin(2. * omega * rad)
    cos2n = math.cos(2. * omega * rad)
    f = np.ones((18), dtype=np.float64)
    f[0] = math.sqrt((1.0 + 0.189*cosn - 0.0058*cos2n)**2 + \
                 (0.189*sinn - 0.0058*sin2n)**2)
    f[1] = f[0]
    f[2] = f[0]
    f[3] = math.sqrt((1.0 + 0.185 * cosn)**2 + (0.185 * sinn)**2)
    f[4] = math.sqrt((1.0 + 0.201 * cosn)**2 + (0.201 * sinn)**2)
    f[5] = math.sqrt((1.0 + 0.221 * cosn)**2 + (0.221 * sinn)**2)
    f[9] = math.sqrt((1.0 + 0.198 * cosn)**2 + (0.198 * sinn)**2)
    f[10] = math.sqrt((1.0 + 0.640*cosn + 0.134*cos2n)**2 + \
                 (0.640*sinn + 0.134*sin2n)**2 )
    f[11] = math.sqrt((1.0 - 0.0373 * cosn)**2 + (0.0373 * sinn)**2)
    f[12] = f[11]
    f[13] = f[11]
    f[15] = f[11]
    f[16] = math.sqrt((1.0 + 0.441 * cosn)**2 + (0.441 * sinn)**2)

    u = np.zeros((18), dtype=np.float64)
    u[0] = math.atan2(0.189*sinn - 0.0058*sin2n, \
                 1.0 + 0.189*cosn - 0.0058*sin2n)/rad
    u[1] = u[0]
    u[2] = u[0]
    u[3] = math.atan2(0.185 * sinn, 1.0 + 0.185 * cosn) / rad
    u[4] = math.atan2(-0.201 * sinn, 1.0 + 0.201 * cosn) / rad
    u[5] = math.atan2(-0.221 * sinn, 1.0 + 0.221 * cosn) / rad
    u[9] = math.atan2(-0.198 * sinn, 1.0 + 0.198 * cosn) / rad
    u[10] = math.atan2(-0.640*sinn - 0.134*sin2n, \
                  1.0 + 0.640*cosn + 0.134*cos2n)/rad
    u[11] = math.atan2(-0.0373 * sinn, 1.0 - 0.0373 * cosn) / rad
    u[12] = u[11]
    u[13] = u[11]
    u[15] = u[11]
    u[16] = math.atan2(-0.441 * sinn, 1.0 + 0.441 * cosn) / rad

    fc = f * np.cos((arg + u) * rad)
    fs = f * np.sin((arg + u) * rad)

    return fc, fs


def fu_nodal(omega, p, constituent):
    """\
    Computes tidal nodal (& perigee) corrections "f" and "u" 
    for n tidal constituents,
    given the mean longitudes p and omega.

    Input:
       omega - mean longitude of lunar node, in degrees.
       p     - mean longitude of lunar perigee.
       consituent - array of constituent names
    Output:
       f  - modulation factor for given tide(s).
       u  - phase correction for given tide, in degrees.

    Note: omega = -N' (the 5th Doodson variable), decreasing in time.
    This is not a very efficient routine, but it needn't be
    called very often, so is ok.

    R Ray  21 August 2003
    Revised 9/15/08.
    Revised 3/28/11 - fixed Mt, MSt.
    Python version 2017-08/25 - Jesper Baasch-Larsen
    """
    # Constants
    rad = math.pi / 180.0
    two = 2.0
    three = 3.0

    # Length of arrays {f,u,constituent}
    n = len(constituent)

    # Initialize output arrays
    f = np.empty((n), dtype=np.float64)
    u = np.empty((n), dtype=np.float64)

    # Various trig functions of astronomical longitudes
    sinn = math.sin(omega * rad)
    cosn = math.cos(omega * rad)
    sin2n = math.sin(two * omega * rad)
    cos2n = math.cos(two * omega * rad)
    sin3n = math.sin(three * omega * rad)
    sinp = math.sin(p * rad)
    cosp = math.cos(p * rad)
    sin2p = math.sin(two * p * rad)
    cos2p = math.cos(two * p * rad)
    sinpn = math.sin((p - omega) * rad)
    cospn = math.cos((p - omega) * rad)

    # Compute standard nodal corrections f and u
    for i in range(n):
        c = constituent[i]
        if c in ['mm', 'msm']:
            term1 = -.0534 * sin2p - .0219 * math.sin((two * p - omega) * rad)
            term2 = 1.0 - .1308*cosn - .0534*cos2p \
                    - .0219*math.cos((two*p-omega)*rad)
        elif c in ['mf', 'msq', 'msp', 'mq']:
            term1 = -0.04324 * sin2p - 0.41465 * sinn - 0.03873 * sin2n
            term2 = 1.0 + 0.04324 * cos2p + 0.41465 * cosn + 0.03873 * cos2n
        elif c in ['msf']:
            # This is linear tide, not compound.
            term1 = 0.137 * sinn
            term2 = 1.0
        elif c in ['mt']:
            term1 = -0.018 * sin2p - 0.4145 * sinn - 0.040 * sin2n
            term2 = 1.0 + 0.018 * cos2p + 0.4145 * cosn + 0.040 * cos2n
        elif c in ['mst']:
            term1 = -0.380 * sin2p - 0.413 * sinn - 0.037 * sin2n
            term2 = 1.0 + 0.380 * cos2p + 0.413 * cosn + 0.037 * cos2n
        elif c in ['o1', 'so3']:
            term1 = 0.1886 * sinn - 0.0058 * sin2n - 0.0065 * sin2p
            term2 = 1.0 + 0.1886 * cosn - 0.0058 * cos2n - 0.0065 * cos2p
        elif c in ['2q1', 'q1', 'rho1', 'sig1']:
            term1 = 0.1886 * sinn
            term2 = 1.0 + 0.1886 * cosn
        elif c in ['tau1']:
            term1 = 0.219 * sinn
            term2 = 1.0 - 0.219 * cosn
        elif c in ['m1']:
            # This assumes m1 argument includes p.
            term1 = -0.2294*sinn - 0.3594*sin2p \
                    - 0.0664*math.sin((two*p-omega)*rad)
            term2 = 1.0 + 0.1722*cosn + 0.3594*cos2p \
                    + 0.0664*math.cos((two*p-omega)*rad)
        elif c in ['chi1']:
            term1 = -0.221 * sinn
            term2 = 1.0 + 0.221 * cosn
        elif c in ['p1']:
            term1 = -0.0112 * sinn
            term2 = 1.0 - 0.0112 * cosn
        elif c in ['k1', 'sk3']:
            term1 = -0.1554 * sinn + 0.0031 * sin2n
            term2 = 1.0 + 0.1158 * cosn - 0.0028 * cos2n
        elif c in ['j1', 'the1']:
            term1 = -0.227 * sinn
            term2 = 1.0 + 0.169 * cosn
        elif c in ['oo1']:
            term1 = -0.640 * sinn - 0.134 * sin2n - 0.150 * sin2p
            term2 = 1.0 + 0.640 * cosn + 0.134 * cos2n + 0.150 * cos2p
        elif c in ['m2','2n2','mu2','n2','nu2','lam2','2sm2', \
                   'ms4','eps2']:
            term1 = -0.03731 * sinn + 0.00052 * sin2n
            term2 = 1.0 - 0.03731 * cosn + 0.00052 * cos2n
        elif c in ['l2']:
            term1 = -0.250*sin2p - 0.110*math.sin((two*p-omega)*rad) \
                    - 0.037*sinn
            term2 = 1.0 - 0.250*cos2p - 0.110*math.cos((two*p-omega)*rad) \
                    - 0.037*cosn
        elif c in ['k2']:
            term1 = -0.3108 * sinn - 0.0324 * sin2n
            term2 = 1.0 + 0.2853 * cosn + 0.0324 * cos2n
        elif c in ['eta2']:
            term1 = -0.436 * sinn
            term2 = 1.0 + 0.436 * cosn
        elif c in ['m3', 'o3', 'f3']:
            # Linear 3rd-deg terms
            term1 = -0.056 * sinn
            term2 = 1.0 - 0.056 * cosn
        elif c in ['j3']:
            term1 = -0.43 * sinn
            term2 = 1.0 + 0.43 * cosn
        else:
            term1 = 0.0
            term2 = 1.0

        f[i] = math.sqrt(term1**2 + term2**2)
        u[i] = math.atan(term1 / term2) / rad

        # Following tides are all compound & use recursion
        if c in ['m4', 'mn4', 'mns2']:
            ctmp = ['m2']
            ftmp, utmp = fu_nodal(omega, p, ctmp)
            f[i] = ftmp[0]**2
            u[i] = 2.0 * utmp[0]
        elif c in ['mk3']:
            ctmp = ['m2', 'k1']
            ftmp, utmp = fu_nodal(omega, p, ctmp)
            f[i] = ftmp[0] * ftmp[1]
            u[i] = utmp[0] + utmp[1]
        elif c in ['mk4']:
            ctmp = ['m2', 'k2']
            ftmp, utmp = fu_nodal(omega, p, ctmp)
            f[i] = ftmp[0] * ftmp[1]
            u[i] = utmp[0] + utmp[1]
        elif c in ['m6']:
            ctmp = ['m2']
            ftmp, utmp = fu_nodal(omega, p, ctmp)
            f[i] = ftmp[0]**3
            u[i] = 3.0 * utmp[0]
        elif c in ['m8']:
            ctmp = ['m2']
            ftmp, utmp = fu_nodal(omega, p, ctmp)
            f[i] = ftmp[0]**4
            u[i] = 4.0 * utmp[0]
        elif c in ['mfDW']:
            # Special test of old Doodson-Warburg formula
            f[i] = 1.043 + 0.414 * cosn
            u[i] = -23.7 * sinn + 2.7 * sin2n - 0.4 * sin3n

    return f, u


def nodal(mjd):
    astro5 = Astro5()
    s, h, p, omega, pprime = astro5(mjd)
    pf, pu = fu_nodal(omega, p, tideconstit.constid)

    rad = math.pi / 180.0
    pu = pu * rad
    return pf, pu


def nodal_A(mjd, constids):
    """\
    At a specific time, calculate nodal factors for constituents at
    all points
 
    Based on subroutine ptide() by Lana Erofeeva, June 2004
    """
    const_idx = []
    for constid in constids:
        const_idx.append(tideconstit.constid.index(constid))

    pf, pu = nodal(mjd)

    A = make_A(mjd, pf, pu, const_idx)
    return A


def make_A(mjd, pf, pu, const_idx):
    """\
    Computes A matrix elements for one data point.
    """
    omega_d = tideconstit.omega_d
    phase_mkB = tideconstit.phase_mkB

    # To use phase shifts from constit.h time should be in seconds
    # relatively Jan 1 1992 (48622mjd)
    rebase = 48622.0
    seconds_per_day = 86400.0
    tm = (mjd - rebase) * seconds_per_day

    ncon = len(const_idx)
    A = np.empty((ncon), dtype=np.complex)
    for j in range(ncon):
        i = const_idx[j]
        if i == -1:
            continue
        A[j] = pf[i]*math.cos(omega_d[i]*tm + phase_mkB[i]+pu[i]) + \
               (pf[i]*math.sin(omega_d[i]*tm + phase_mkB[i]+pu[i]))*1.0j
    return A


def height(A, P):
    """Returns height from model array of complex constituents."""
    assert len(A.shape) == 1
    assert len(P.shape) == 3

    if A.shape[0] == 0:
        return 0.0
    """
    sum_ = 0.0
    # height[i] = sum_of_real(A[i]*P[i])
    for i in range(len(A)):
        sum_ = sum_ + P[i].real*A[i].real - P[i].imag*A[i].imag
    """

    # Array implementation
    """
    sum_ = np.zeros((P.shape[1]), dtype=np.float64)
    for i in range(len(sum_)):
        tmp1 = P[:,i].real*A.real - P[:,i].imag*A.imag
        sum_[i] = tmp1.sum()
    """

    # Full array implementation
    # Reshape to allow broadcasting
    Ar = np.reshape(A, (A.shape[0], 1, 1))
    #sum_ = np.zeros((P.shape[1], P.shape[2]), dtype=np.float64)
    tmp1 = P.real * Ar.real - P.imag * Ar.imag
    sum_ = tmp1.sum(axis=0)

    return sum_


class Ptide:
    """\
    At a specific time, predict tide, given constituents at a point.
    """

    def __init__(self, hc, constids, interp_minor):
        self.hc = hc
        self.constids = constids
        self.interp_minor = interp_minor

        if interp_minor:
            self.minorH = MinorH(hc, constids)

    def __call__(self, fc, fs, A):
        # Calculate predicted value
        zpred = height(A, self.hc)

        if self.interp_minor:
            # Add minor constituents
            zpred = zpred + self.minorH(fc, fs)

        return zpred


class MinorH:
    """\
    Return correction for the 16 minor constituents at a single timestep
    Given coefficients for the timestep calculated by subroutine fac_minor()
    Based on subroutine infer_minor() by Lana Erofeeva, June 2004:
    Based on Richard Ray code perth2

    z = HC for GIVEN consituents
    constids = GIVEN constituents
    """

    def __init__(self, z, constids):
        nc, ny, nx = z.shape
        ncon = len(constids)
        constids8 = ['q1', 'o1', 'p1', 'k1', 'n2', 'm2', 's2', 'k2']
        # Re-order to correspond to constids8
        z8 = np.zeros((8, ny, nx), dtype=np.complex)
        ni = 0
        for i in range(8):
            for j in range(ncon):
                if constids[j] == constids8[i]:
                    z8[i] = z[j]
                    if i not in [2, 8]:
                        ni += 1

        if ni <= 6:
            raise ValueError('Not enough constituents for inference')

        self.zmin = np.empty((18, ny, nx), dtype=np.complex)
        self.zmin[0] = 0.263 * z8[0] - 0.0252 * z8[1]  # 2Q1
        self.zmin[1] = 0.297 * z8[0] - 0.0264 * z8[1]  # sigma1
        self.zmin[2] = 0.164 * z8[0] + 0.0048 * z8[1]  # rho1 +
        self.zmin[3] = 0.0140 * z8[1] + 0.0101 * z8[3]  # M1
        self.zmin[4] = 0.0389 * z8[1] + 0.0282 * z8[3]  # M1
        self.zmin[5] = 0.0064 * z8[1] + 0.0060 * z8[3]  # chi1
        self.zmin[6] = 0.0030 * z8[1] + 0.0171 * z8[3]  # pi1
        self.zmin[7] = -0.0015 * z8[1] + 0.0152 * z8[3]  # phi1
        self.zmin[8] = -0.0065 * z8[1] + 0.0155 * z8[3]  # theta1
        self.zmin[9] = -0.0389 * z8[1] + 0.0836 * z8[3]  # J1 +
        self.zmin[10] = -0.0431 * z8[1] + 0.0613 * z8[3]  # OO1 +
        self.zmin[11] = 0.264 * z8[4] - 0.0253 * z8[5]  # 2N2 +
        self.zmin[12] = 0.298 * z8[4] - 0.0264 * z8[5]  # mu2 +
        self.zmin[13] = 0.165 * z8[4] + 0.00487 * z8[5]  # nu2 +
        self.zmin[14] = 0.0040 * z8[5] + 0.0074 * z8[6]  # lambda2
        self.zmin[15] = 0.0131 * z8[5] + 0.0326 * z8[6]  # L2 +
        self.zmin[16] = 0.0033 * z8[5] + 0.0082 * z8[6]  # L2 +
        self.zmin[17] = 0.0585 * z8[6]  # t2 +

    def __call__(self, fc, fs):
        # sum over all tides
        fcs = fc.reshape(18, 1, 1)
        fss = fc.reshape(18, 1, 1)
        dh = self.zmin.real * fcs - self.zmin.imag * fss
        dh = dh.sum(axis=0)

        return dh
