'''
Module to manage special histograms, like adaptive binned 1D and 2D histograms.
'''

__author__ = ['Miguel Ramos Pernas']
__email__  = ['miguel.ramos.pernas@cern.ch']


# Custom
from hep_spt.histograms import errorbar_hist, process_range
from hep_spt.stats import poisson_fu

# Python
import numpy as np
import bisect, itertools
import matplotlib.pyplot as plt
import warnings
from matplotlib.patches import Rectangle


__all__ = ['AdBin', 'adbin_hist2d_rectangles',
           'adbin_hist1d', 'adbin_hist1d_edges',
           'adbin_hist'
           ]


class AdBin(object):

    def __init__( self, arr, range = None, weights = None ):
        '''
        Represent a n-dimensional adaptive bin. This class is meant so serve
        as interface between the user and matplotlib to plot adaptive
        binned histograms.

        :param arr: array of data.
        :type arr: numpy.ndarray
        :param range: range of the histogram in each dimension. As \
        [(xmin, ymin), (xmax, ymax)].
        :type range: None or numpy.ndarray(float, float).
        :param weights: possible weights.
        :type weights: numpy.ndarray
        '''
        arr, (vmin, vmax), weights = _proc_hist_input(arr, range, weights)

        self.array   = arr
        self.weights = weights
        self.vmin    = np.array(vmin, dtype = float)
        self.vmax    = np.array(vmax, dtype = float)

    def contains( self, arr ):
        '''
        Return whether the values in the input array are inside this bin or \
        not.

        :param arr: input data.
        :type arr: numpy.ndarray
        :returns: Whether the values in the input array are inside this bin or \
        not.
        :rtype: bool or numpy.ndarray(bool)
        '''
        return np.logical_and(arr >= self.vmin, arr < self.vmax).all(axis = 1)

    def dens( self, arr, weights = None ):
        '''
        Return the density of this bin.

        :param arr: array of data to process.
        :type arr: numpy.ndarray
        :param weights: possible weights.
        :type weights: numpy.ndarray
        :returns: Density of this bin.
        :rtype: float
        '''
        return self.sw(arr, weights)/float(self.size())

    def divide( self, ndiv = 2 ):
        '''
        Divide this bin in two, using the median in each dimension. The
        dimension used to make the division is taken as that which generates
        the smallest bin.

        :param ndiv: number of divisions to create. For large values, this \
        algorithm will ask for having a low sum of weights for the first \
        bin, which will translate in having a long thin bin.
        :type ndiv: int
        :returns: Two new bins, supposed to contain half the sum of weights of \
        the parent.
        :rtype: AdBin, AdBin
        :raises RuntimeError: If called after the data pointers have been freed.

        .. warning:: This method can not be called after
           :meth:`AdBin.free_memory`, since it destroys the arrays of data and
           weights.

        .. seealso:: :meth:`AdBin.free_memory`
        '''
        assert ndiv > 1

        if self.array is None:
            raise RuntimeError('Attempt to call AdBin.divide on a bin whose '\
                               'pointers have been freed')

        srt   = self.array.argsort(axis = 0)
        sarr  = np.array([self.array.T[i][s] for i, s in enumerate(srt.T)]).T
        swgts = self.weights[srt]
        csw   = swgts.cumsum(axis = 0)

        # Normalize using the total sum of weights: csw[-1][0]
        co = csw[-1][0]/float(ndiv)

        p = np.array([bisect.bisect_left(c, co) for c in csw.T])

        bounds = np.array([np.nextafter(sarr[p,i], np.infty)
                           for i, p in enumerate(p)])

        mask_left  = (self.array < bounds)
        mask_right = (self.array >= bounds)

        def _msz( arr, i ):
            '''
            Calculate the minimum size of the input array, for the
            given index and considering the two global masks
            "mask_left" and "mask_right".
            '''
            size = lambda arr: arr.max() - arr.min()

            sarr = arr[:,i]
            sz   = float(size(sarr))

            if sz == 0:
                return np.infty

            sl = size(sarr[mask_left[:,i]])/sz
            sr = size(sarr[mask_right[:,i]])/sz

            return min(sl, sr)

        frags = np.array([_msz(self.array, i) for i in np.arange(self.array.shape[1])])

        # The sample is cut following the criteria that leads to the
        # smallest bin possible.

        min_dim = frags.argmin()

        if min_dim == np.infty:
            # This is a very special case. If we reach this point, some points
            # have the same values in all dimensions, so the division is not
            # possible.
            warnings.warn('All possible divisions have size equal to zero; not dividing',
                          RuntimeWarning)
            return [self]

        il = mask_left[:,min_dim]
        ir = mask_right[:,min_dim]

        left   = self.array[il]
        right  = self.array[ir]
        wleft  = self.weights[il]
        wright = self.weights[ir]

        d = bounds[min_dim]

        lbd = np.array([self.vmin, self.vmax])
        lbd[1][min_dim] = d
        bl = AdBin(left, lbd, wleft)

        rbd = np.array([self.vmin, self.vmax])
        rbd[0][min_dim] = d
        br = AdBin(right, rbd, wright)

        # If the number of divisions is greater than 2, perform again the same
        # operation in the bin on the right
        all_bins = [bl]
        if ndiv > 2:
            all_bins += br.divide(ndiv - 1)
        else:
            all_bins.append(br)

        return all_bins

    def free_memory( self ):
        '''
        Remove the pointers to the arrays of data and weights.

        .. warning:: The method :meth:`AdBin.divide` will become unavailable
           after this.
        '''
        self.array   = None
        self.weights = None

    def size( self ):
        '''
        Return the size of the bin.

        :returns: Size of this bin calculated as the product of \
        the individual sizes in each dimension.
        :rtype: float
        '''
        return float(np.prod(self.vmax - self.vmin))

    def sw( self, arr, weights = None ):
        '''
        Compute and return the sum of weights.

        :param arr: array of data to process.
        :type arr: numpy.ndarray
        :param weights: possible weights.
        :type weights: numpy.ndarray
        :returns: Sum of weights for this bin.
        :rtype: float
        '''
        true = self.contains(arr)

        if weights is not None:
            sw = weights[true].sum()
        else:
            sw = np.count_nonzero(true)

        return float(sw)

    def sw_u( self, arr, weights = None ):
        '''
        Calculate and return the uncertainty on the sum of weights.

        :param arr: array of data to process.
        :type arr: numpy.ndarray
        :param weights: possible weights.
        :type weights: numpy.ndarray
        :returns: Uncertainty of the sum of weights in the bin. If "weights" is \
        provided, this magnitude is equal to the square root of the sum of \
        weights in the bin. Otherwise poissonian errors are considered.
        :rtype: float
        '''
        true = self.contains(arr)

        if weights is not None:
            uncert = np.sqrt((weights*weights)[true].sum())
        else:
            sw = np.count_nonzero(true)

            uncert = poisson_fu(sw)

        return float(uncert)


def adbin_as_rectangle( adb, **kwargs ):
    '''
    Extract the bounds of a 2-dimensional :class:`AdBin` object so it
    can be processed by a :class:`matplotlib.patches.Rectangle` and properly
    fill the area inside it.

    :param adb: input adaptive bin. It must be 2-dimensional.
    :type adb: AdBin
    :param kwargs: extra arguments to :class:`matplotlib.patches.Rectangle`.
    :type kwargs: dict
    :returns: Rectangle to be drawn with matplotlib.
    :rtype: matplotlib.patches.Rectangle
    '''
    xmin, ymin = adb.vmin
    xmax, ymax = adb.vmax

    width  = xmax - xmin
    height = ymax - ymin

    return Rectangle((xmin, ymin), width, height, **kwargs)


def adbin_hist1d( arr, nbins = 100, range = None, weights = None, is_sorted = False, **kwargs ):
    '''
    Create an adaptive binned histogram in one dimension.

    :param arr: array of data.
    :type arr: numpy.ndarray
    :param nbins: number of bins. Must be greater than the length of the \
    input array.
    :type nbins: int
    :param range: range of the histogram.
    :type range: None or tuple(float, float)
    :param weights: optional array of weights.
    :type weights: numpy.ndarray
    :param is_sorted: whether the input sample is already sorted or not.
    :type is_sorted: bool
    :param kwargs: any other argument to be passed to \
    :func:`plotting.errorbar_hist`.
    :type kwargs: dict
    :returns: Values, edges, the distance between the center and the bounds \
    of the bins in X and Y errors. The shape of the errors in Y depends on \
    the uncertainty type passed to :func:`errorbar_hist` in "kwargs".
    :rtype: numpy.ndarray, numpy.ndarray, numpy.ndarray, numpy.ndarray

    .. seealso:: :func:`adbin_hist1d_edges`, :func:`adbin_hist`
    '''
    arr, range, weights = _proc_hist_input_1d(arr, range, weights)

    # Sort the data
    if not is_sorted:
        srt     = arr.argsort()
        arr     = arr[srt]
        weights = weights[srt]

    # Solving the problem from the left and from the right reduces
    # the bias in the last edges
    le = adbin_hist1d_edges(arr, nbins, range, weights, is_sorted=True)
    re = adbin_hist1d_edges(arr[::-1], nbins, range, weights[::-1], is_sorted=True)[::-1]

    edges = (re + le)/2.

    edges[0], edges[-1] = range

    return errorbar_hist(arr, edges, range, weights, **kwargs)


def adbin_hist1d_edges( arr, nbins = 100, range = None, weights = None, is_sorted = False ):
    '''
    Create adaptive binned edges to make a histogram from the given data.

    :param arr: array of data.
    :type arr: numpy.ndarray
    :param nbins: number of bins. Must be greater than the length of the \
    input array.
    :type nbins: int
    :param range: range of the histogram.
    :type range: None or tuple(float, float)
    :param weights: optional array of weights.
    :type weights: numpy.ndarray
    :param is_sorted: whether the input sample is already sorted or not.
    :type is_sorted: bool
    :returns: Edges of the histogram, with size (nbins + 1).
    :rtype: numpy.ndarray
    :raises ValueError: If the number of bins specified is greater than the \
    length of the input array.

    .. note:: The number of bins must be smaller than the length of the input array.

    .. seealso:: :func:`adbin_hist1d`
    '''
    if nbins > len(arr):
        raise ValueError(
            'Number of bins can not be greater than the length of the input array')

    arr, (vmin, vmax), weights = _proc_hist_input_1d(arr, range, weights)

    # Sort the data
    if not is_sorted:
        srt     = arr.argsort()
        arr     = arr[srt]
        weights = weights[srt]

    edges = np.zeros(nbins + 1)

    for i in np.arange(nbins - 1):

        csum = weights.cumsum()
        reqs = csum[-1]/float(nbins - i)

        p = bisect.bisect_left(csum, reqs)
        if p == len(csum):
            p = -1

        s = csum[p]

        if s != reqs:
            # If the sum differs, then decide whether to use the
            # current index based on the relative difference.
            if p != 0 and np.random.uniform() < (s - reqs)/reqs:
                p -= 1

        edges[i + 1]  = (arr[p] + arr[p + 1])/2.

        arr = arr[p + 1:]
        weights = weights[p + 1:]

    edges[0]  = vmin
    edges[-1] = vmax

    return edges


def adbin_hist2d_rectangles( bins, smp,
                             range = None, weights = None,
                             cmap = None, fill = 'sw',
                             color = True,
                             **kwargs ):
    '''
    Create a list of rectangles from a list of bins.
    It uses the input data in "arr" to calculate the associated quantity,
    which is specified in "fill".

    :param bins: input bins.
    :type bins: list(AdBin)
    :param smp: input sample. It must have shape (n, 2).
    :type smp: numpy.ndarray
    :param range: range of the histogram in each dimension. As \
    [(xmin, ymin), (xmax, ymax)].
    :type range: None or tuple(np.ndarray, np.ndarray)
    :param weights: input weights.
    :type weights: list(value-type)
    :param cmap: optional color map. If "None", the default from \
    matplotlib.pyplot is used.
    :type cmap: matplotlib.colors.Colormap
    :param fill: method to use for filling ('sw' or 'dens').
    :type fill: str
    :param color: whether the output rectangles are filled with a color or not.
    :type color: bool
    :param kwargs: any other argument to the constructor of \
    :class:`matplotlib.patches.Rectangle`.
    :type kwargs: dict
    :returns: Rectangles and contents.
    :rtype: numpy.ndarray, numpy.ndarray
    '''
    if fill not in ('sw', 'dens'):
        raise ValueError('Unknown fill option "{}", choose '\
                         'between ("sw", "dens")'.format(fill))

    recs = [adbin_as_rectangle(b, **kwargs) for b in bins]

    arr, range, weights = _proc_hist_input(smp, range, weights)

    # Get the contents associated to each bin
    func = getattr(AdBin, fill)
    contents = np.array(list(map(lambda b: func(b, arr, weights), bins)))

    if color:

        cmap = cmap or plt.get_cmap()

        vmin = contents.min()
        vmax = contents.max()

        sz = float(vmax - vmin)

        # We need to normalize the color map. The normalization
        # depends if the input number is an integer (0, length of
        # the color map) or a float (0., 1.).
        for r, c in zip(recs, contents):
            if sz != 0:
                r.set_facecolor(cmap((c - vmin)/sz))
            else:
                r.set_facecolor('none')
    else:
        for r in recs:
            r.set_facecolor((1, 1, 1))

    return recs, contents


def adbin_hist( arr, nbins = 100, range = None, weights = None, ndiv = 2, free_memory = True ):
    '''
    Create an adaptive binned histogram in N dimensions.
    The number of dimensions is determined by the shape of the input array.
    An array with shape (n, 2), will create a 2-dimensional adaptive binned
    histogram.

    :param arr: array of data with the variables as columns.
    :type arr: numpy.ndarray
    :param range: range of the histogram in each dimension. For example, \
    [(xmin, ymin), (xmax, ymax)] in the 2-dimensional case.
    :type range: None or numpy.ndarray((float, float, ...), (float, float, ...)).
    :param nbins: number of bins. In this algorithm, divisions will be made \
    till the real number of bins is equal or greater than "nbins". If this \
    number is a power of "ndiv", then the real number of bins will match \
    "nbins".
    :type nbins: int
    :param weights: optional array of weights.
    :type weights: numpy.ndarray
    :param ndiv: see :meth:`AdBin.divide`.
    :type ndiv: int
    :param free_memory: whether to free the pointers pointing to the arrays of \
    data and weights in the bins.
    :type free_memory: bool
    :returns: Adaptive bins of the histogram, with size (nbins + 1).
    :rtype: list(AdBin)

    .. note:: This function will automatically delete the arrays of data and
       weights copied in the adaptive bins by calling `AdBin.free_memory`. To
       prevent it set "free_memory" to False. In such case, the user is
       responsible of deleting the data in each bin by calling the
       aforementioned function, if necessary.

    .. seealso:: :func:`adbin_hist1d`, :meth:`AdBin.divide`,
       :meth:`AdBin.free_memory`
    '''
    if nbins > len(arr):
        raise ValueError(
            'Number of bins can not be greater than the length of the input array')

    bins = [AdBin(arr, range, weights)]
    while len(bins) < nbins:
        bins = list(itertools.chain.from_iterable(a.divide(ndiv) for a in bins))

    if free_memory:
        map(AdBin.free_memory, bins)

    return bins


def _proc_hist_input_1d( arr, range = None, weights = None ):
    '''
    Process some of the input arguments of the functions to
    manage 1D histograms.

    :param arr: array of data.
    :type arr: numpy.ndarray
    :param range: range of the histogram.
    :type range: None or tuple(float, float)
    :param weights: optional array of weights.
    :type weights: numpy.ndarray
    :returns: Processed array of data, weights, and the minimum \
    and maximum values.
    :rtype: numpy.ndarray, tuple(float, float), numpy.ndarray
    '''
    vmin, vmax = process_range(arr, range)

    cond = np.logical_and(arr >= vmin, arr < vmax)

    arr = arr[cond]

    if weights is not None:
        weights = weights[cond]
    else:
        weights = np.ones(len(arr))

    return arr, (vmin, vmax), weights


def _proc_hist_input( arr, range = None, weights = None ):
    '''
    Process some of the input arguments of the functions to
    manage ND histograms.

    :param arr: array of data.
    :type arr: numpy.ndarray
    :param range: range of the histogram in each dimension. For example, \
    [(xmin, ymin), (xmax, ymax)] in the 2-dimensional case.
    :type range: None or numpy.ndarray((float, float, ...), (float, float, ...)).
    :param weights: optional array of weights.
    :type weights: numpy.ndarray
    :returns: Processed array of data, weights, and the minimum \
    and maximum values for each dimension.
    :rtype: numpy.ndarray, tuple(np.ndarray, np.ndarray), numpy.ndarray
    '''
    vmin, vmax = process_range(arr, range)

    cond = np.logical_and(arr >= vmin, arr < vmax).all(axis = 1)

    arr = arr[cond]

    if weights is not None:
        weights = weights[cond]
    else:
        weights = np.ones(len(arr))

    return arr, (vmin, vmax), weights
