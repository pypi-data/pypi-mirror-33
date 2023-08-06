'''
Provide some useful functions to plot with matplotlib.
'''

__author__ = ['Miguel Ramos Pernas']
__email__  = ['miguel.ramos.pernas@cern.ch']


# Local
from hep_spt import __project_path__
from hep_spt.histograms import cfe

# Python
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np
import math
import os
import warnings
from cycler import cycler

__all__ = [
    'available_styles',
    'corr_hist2d',
    'opt_fig_div',
    'path_to_styles',
    'samples_cycler',
    'set_style',
    'text_in_rectangles'
    ]

# Path to the directory containing the styles
__path_to_styles__ = os.path.join(__project_path__, 'mpl')


def available_styles():
    '''
    Get a list with the names of the available styles.

    :returns: List with the names of the available styles within this package.
    :rtype: list(str)
    '''
    available_styles = list(map(lambda s: s[:s.find('.mplstyle')],
                                os.listdir(__path_to_styles__)))
    return available_styles


def corr_hist2d( matrix, titles, frmt = '{:.2f}', vmin = None, vmax = None, cax = None ):
    '''
    Plot a correlation matrix in the given axes.

    :param matrix: correlation matrix.
    :type matrix: numpy.ndarray
    :param titles: name of the variables being represented.
    :type titles: list(str)
    :param frmt: format to display the correlation value in each bin. By \
    default it is assumed that the values go between :math:`[0, 1]`, so \
    three significant figures are considered. If "frmt" is None, then \
    no text is displayed in the bins.
    :type frmt: str
    :param vmin: minimum value to represent in the histogram.
    :type vmin: float
    :param vmax: maximum value to represent in the histogram.
    :type vmax: float
    :param cax: axes where to draw. If None, then the current axes are taken.
    :type cax: matplotlib.axes.Axes
    '''
    cax = cax or plt.gca()

    edges = np.linspace(0, len(titles), len(titles) + 1)

    centers = cfe(edges)

    x, y = np.meshgrid(centers, centers)

    x = x.reshape(x.size)
    y = y.reshape(y.size)
    c = matrix.reshape(matrix.size)

    vmin = vmin or c.min()
    vmax = vmax or c.max()

    cax.hist2d(x, y, (edges, edges), weights=c, vmin=vmin, vmax=vmax)

    # Modify the ticks to display the variable names
    for i, a in enumerate((cax.xaxis, cax.yaxis)):

        a.set_major_formatter(ticker.NullFormatter())
        a.set_minor_formatter(ticker.FixedFormatter(titles))

        a.set_major_locator(ticker.FixedLocator(edges))
        a.set_minor_locator(ticker.FixedLocator(centers))

        for tick in a.get_minor_ticks():
            tick.tick1line.set_markersize(0)
            tick.tick2line.set_markersize(0)
            tick.label1.set_rotation(45)

            if i == 0:
                tick.label1.set_ha('right')
            else:
                tick.label1.set_va('top')

    # Annotate the value of the correlation
    if frmt is not None:
        for ix, iy, ic in zip(x, y, c):
            cax.annotate(frmt.format(ic), xy=(ix, iy), ha='center', va='center')

    # Draw the grid
    cax.grid()


def opt_fig_div( naxes ):
    '''
    Get the optimal figure division for a given number of axes, where
    all the axes have the same dimensions.
    For non-perfect square numbers, this algorithm preferes to increase
    the number of columns instead of the number of rows.

    :param naxes: number of axes to plot in the figure.
    :type naxes: int
    :returns: Number of rows and columns of axes to draw.
    :rtype: int, int
    '''
    nstsq = int(round(math.sqrt(naxes)))

    if nstsq**2 > naxes:
        nx = nstsq
        ny = nstsq
    else:
        nx = nstsq
        ny = nstsq
        while nx*ny < naxes:
            ny += 1

    return nx, ny


def path_to_styles():
    '''
    Retrieve the path to the directory containing the styles.

    :returns: Path to the directory containing the styles.
    :rtype: str
    '''
    return __path_to_styles__


def samples_cycler( smps, *args, **kwargs ):
    '''
    Generate a :class:`cycler.Cycler` object were the labels are defined by
    "smps", and the other parameters are left to the user.
    This function is useful when one wants to plot several samples with
    different matplotlib styles.
    This function allows to create a :class:`cycler.Cycler` object
    to loop over the given samples and associated formats, where the "label"
    key is filled with the values from "smps".

    :param smps: list of names for the samples.
    :type smps: list(str)
    :param args: position argument to :func:`cycler.cycler`.
    :type args: tuple
    :param kwargs: keyword arguments to :func:`cycler.cycler`.
    :type kwargs: dict
    :returns: Object with the styles for each sample and a defined "label" key.
    :rtype: :class:`cycler.Cycler`
    '''
    cyc = cycler(*args, **kwargs)

    ns = len(smps)
    nc = len(cyc)

    if ns > nc:

        warnings.warn('Not enough plotting styles in cycler, '\
                      'some samples might have the same style.',
                      RuntimeWarning)

        l = (ns // nc) + bool(ns % nc)

        re_cyc = (l*cyc)[:ns]
    else:
        re_cyc = cyc[:ns]

    return re_cyc + cycler(label=smps)


def set_style( *args ):
    '''
    Set the style for matplotlib to one within this project. Available styles
    are:

    * singleplot: designed to create a single figure.
    * multiplot: to make subplots. Labels and titles are smaller than in \
    "singleplot", although lines and markers maintain their sizes.

    By default the "singleplot" style is set.

    :param args: styles to load.
    :type args: tuple
    '''
    args = list(args)
    if len(args) == 0:
        # The default style is always set
        args = ['default', 'singleplot']
    elif 'default' not in args:
        args.insert(0, 'default')

    avsty = available_styles()

    sty_args = []
    for s in args:
        if s not in avsty:
            warnings.warn('Unknown style "{}", will not be loaded'.format(style))
        else:
            sty_args.append(os.path.join(__path_to_styles__, '{}.mplstyle'.format(s)))

    plt.style.use(sty_args)


def text_in_rectangles( recs, txt, cax = None, **kwargs ):
    '''
    Write text inside :class:`matplotlib.patches.Rectangle` instances.

    :param recs: set of rectangles to work with.
    :type recs: list(matplotlib.patches.Rectangle)
    :param txt: text to fill in each rectangle.
    :type txt: list(str)
    :param cax: axes where the rectangles are being drawn. If None, then the \
    current axes are taken.
    :type cax: matplotlib.axes.Axes
    :param kwargs: any other argument to matplotlib.axes.Axes.annotate.
    :type kwargs: dict
    '''
    cax = cax or plt.gca()

    for r, t in zip(recs, txt):
        x, y = r.get_xy()

        cx = x + r.get_width()/2.
        cy = y + r.get_height()/2.

        cax.annotate(t, (cx, cy), **kwargs)
