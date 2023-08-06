'''
Functions to work with histograms.
'''

__author__ = ['Miguel Ramos Pernas']
__email__  = ['miguel.ramos.pernas@cern.ch']

# Local
from hep_spt.stats import stat_values, poisson_fu, poisson_llu, sw2_u

# Python
import numpy as np

__all__ = [
    'cfe',
    'errorbar_hist',
    'profile',
    'pull',
    'residual',
]


def cfe( edges ):
    '''
    Calculate the centers of a set of bins given their edges.

    :param edges: edges of a histogram.
    :type edges: numpy.ndarray
    :returns: Centers of the histogram.
    :rtype: numpy.ndarray
    '''
    return (edges[1:] + edges[:-1])/2.


def errorbar_hist( arr, bins = 20, range = None, weights = None, norm = False, norm_type = 'range', uncert = None ):
    '''
    Calculate the values needed to create an error bar histogram.
    Different errors can be considered (see below).

    :param arr: input array of data to process.
    :param bins: see :func:`numpy.histogram`.
    :type bins: int or sequence of scalars or str
    :param range: range to process in the input array.
    :type range: None or tuple(float, float)
    :param weights: possible weights for the histogram.
    :type weights: None or numpy.ndarray(value-type)
    :param norm: if True, normalize the histogram. If it is set to a number, \
    the histogram is normalized and multiplied by that number.
    :type norm: bool, int or float
    :param norm_type: the normalization type to apply. To be chosen between \
    'range' and 'all'. In the first case (default), only the points lying \
    inside the histogram range are considered in the normalization. In the \
    later, all the points are considered. In this case, the sum of the \
    values returned by this function will not sum the value provided in "norm".
    :type norm_type: str
    :param uncert: type of uncertainty to consider. If None, the square root \
    of the sum of squared weights is considered. The possibilities \
    are: \
    - "freq": frequentist uncertainties. \
    - "dll": uncertainty based on the difference on the logarithm of \
    likelihood. \
    - "sw2": sum of square of weights. In case of non-weighted data, the \
    uncertainties will be equal to the square root of the entries in the bin.
    :type uncert: str or None
    :returns: Values, edges, the spacing between bins in X the Y errors. \
    In the non-weighted case, errors in Y are returned as two arrays, with the \
    lower and upper uncertainties.
    :rtype: numpy.ndarray, numpy.ndarray, numpy.ndarray, numpy.ndarray
    :raises ValueError: if the uncertainty type is not among the possibilities.
    :raises ValueError: if the normalization type is neither 'range' nor 'all'.
    :raises TypeError: if the uncertainty is "freq" or "dll" and "weights" is \
    not of integer type.

    .. seealso:: :func:`hep_spt.stats.poisson_fu`, :func:`hep_spt.stats.poisson_llu`
    '''
    if uncert not in (None, 'freq', 'dll', 'sw2'):
        raise ValueError('Unknown uncertainty type "{}"'.format(uncert))

    # By default use square root of the sum of squared weights
    uncert = uncert or 'sw2'

    values, edges = np.histogram(arr, bins, range, weights=weights)

    if uncert == 'freq':
        ey = poisson_fu(values)
    elif uncert == 'dll':
        ey = poisson_llu(values)
    else:
        ey = sw2_u(arr, bins, range, weights)

    # For compatibility with matplotlib.pyplot.errorbar
    ey = ey.T

    ex = (edges[1:] - edges[:-1])/2.

    if norm:

        if norm_type == 'range':

            # Normalizing in the visible region
            s = float(values.sum())/norm

        elif norm_type == 'all':

            # Normalizing to all the points
            if weights is None:
                s = float(len(arr))/norm
            else:
                s = float(weights.sum())/norm

        else:
            raise ValueError('Unknown normalization type "{}"'.format(norm_type))

        values = values/s
        ey = ey/s

    return values, edges, ex, ey


def process_range( arr, range = None ):
    '''
    Process the given range, determining the minimum and maximum
    values for a 1D histogram.

    :param arr: array of data.
    :type arr: numpy.ndarray
    :param range: range of the histogram. It must contain tuple(min, max), \
    where "min" and "max" can be either floats (1D case) or collections \
    (ND case).
    :type range: None or tuple
    :returns: Minimum and maximum values.
    :rtype: float, float
    '''
    if range is None:
        amax = arr.max(axis=0)
        vmin = arr.min(axis=0)
        vmax = np.nextafter(amax, np.infty)
    else:
        vmin, vmax = range

    return vmin, vmax


def profile( x, y, bins = 20, range = None, weights = None, std_type = 'mean' ):
    '''
    Calculate the profile from a 2D data sample.
    It corresponds to the mean of the values in "y" for each bin in "x".

    :param x: values to consider for the binning.
    :type x: numpy.ndarray(value-type)
    :param y: values to calculate the mean with.
    :type y: numpy.ndarray(value-type)
    :param bins: see :func:`numpy.histogram`.
    :type bins: int or sequence of scalars or str
    :param range: range to process in the input array.
    :type range: None or tuple(float, float)
    :param weights: possible array of weights for the profile.
    :type weights: None or numpy.ndarray(value-type)
    :param std_type: type of standard deviation to be returned. The default \
    ('mean') makes this function return the standard deviation of the mean. \
    If set to 'sample', it will return the standard deviation of the sample \
    instead. The definitions can be seen in :func:`stat_values`.
    :type std_type: str
    :returns: Profile in "y" and standard deviation.
    :rtype: numpy.ndarray, numpy.ndarray
    :raises ValueError: If an unknown standard deviation type is provided.
    '''
    vmin, vmax = process_range(x, range)

    _, edges = np.histogram(x, bins, range=(vmin, vmax))

    dig = np.digitize(x, edges)

    ln = len(edges)

    prof, std = np.empty((ln - 1,)), np.empty((ln - 1,))
    for i in np.arange(1, ln):

        cond = (dig == i)

        if weights is not None:
            vals = stat_values(y[cond], weights[cond])
        else:
            vals = stat_values(y[cond])

        prof[i - 1] = vals.mean

        if std_type == 'mean':
            std[i - 1] = vals.std_mean
        elif std_type == 'sample':
            std[i - 1] = vals.std
        else:
            raise ValueError('Unknown standard deviation type "{}"'.format(std_type))

    return prof, std


def pull( vals, err, ref, ref_err = None ):
    '''
    Get the pull with the associated errors for a given set of values and a
    reference. Considering, :math:`v` as the experimental value and :math:`r`
    as the rerference, the definition of this quantity is :math:`(v - r)/\sigma`
    in case symmetric errors are provided. In the case of asymmetric errors the
    definition is:

    .. math::
       \\text{pull}
       =
       \Biggl \lbrace
       {
       \\frac{v - r}{\sigma_{low}} \\text{ if } v - r \geq 0
       \\atop
       \\frac{v - r}{\sigma_{up}}  \\text{ otherwise }
       }

    In the latter case, the errors are computed in such a way that the closer to
    the reference is equal to 1 and the other is scaled accordingly, so if
    :math:`v - r > 0`, then :math:`\sigma^{pull}_{low} = 1` and
    :math:`\sigma^{pull}_{up} = \sigma_{up}/\sigma_{low}`.

    If uncertainties are also provided for the reference, then the
    definition is the same but considering the sum of squares rule:

    .. math::
       (\sigma'^{v}_{low})^2 = (\sigma^{v}_{low})^2 + (\sigma^{r}_{up})^2

    .. math::
       (\sigma'^{v}_{up})^2 = (\sigma^{v}_{up})^2 + (\sigma^{r}_{low})^2

    :param vals: values to compare with.
    :type vals: numpy.ndarray
    :param err: array of errors. Both symmetric and asymmetric errors \
    can be provided. In the latter case, they must be provided as a \
    (2, n) array.
    :type err: numpy.ndarray
    :param ref: reference to follow.
    :type ref: numpy.ndarray
    :param ref_err: possible errors for the reference.
    :type ref_err: numpy.ndarray
    :returns: Pull of the values with respect to the reference and \
    associated errors. In case asymmetric errors have been provided, \
    the returning array has shape (2, n).
    :rtype: numpy.ndarray, numpy.ndarray
    :raises TypeError: if any of the error arrays does not have shape (2, n) or (n,).

    .. seealso:: :func:`residual`
    '''
    pull, err = residual(vals, err, ref, ref_err)

    perr = np.ones_like(err)

    if len(err.shape) == 1:
        # Symmetric errors
        pull /= err

    else:
        # Asymmetric errors

        up = (pull >= 0)
        lw = (pull < 0)

        el, eu = err

        pull[up] /= el[up]
        pull[lw] /= eu[lw]

        perr_l, perr_u = perr

        perr_l[lw] = (el[lw]/eu[lw])
        perr_u[up] = (eu[up]/el[up])

    return pull, perr


def residual( vals, err, ref, ref_err = None ):
    '''
    Calculate the residual with its errors, for a set of values with
    respect to a reference.
    If uncertainties are also provided for the reference, then the
    definition is the same but considering the sum of squares rule:

    .. math::
       (\sigma'^{v}_{low})^2 = (\sigma^{v}_{low})^2 + (\sigma^{r}_{up})^2

    .. math::
       (\sigma'^{v}_{up})^2 = (\sigma^{v}_{up})^2 + (\sigma^{r}_{low})^2

    :param vals: values to compare with.
    :type vals: numpy.ndarray
    :param err: array of errors. Both symmetric and asymmetric errors \
    can be provided. In the latter case, they must be provided as a \
    (2, n) array.
    :type err: numpy.ndarray
    :param ref: reference to follow.
    :type ref: numpy.ndarray
    :param ref_err: possible errors for the reference.
    :type ref_err: numpy.ndarray
    :returns: Residual of the values with respect to the reference and \
    associated errors. In case asymmetric errors have been provided, \
    the returning array has shape (2, n).
    :rtype: numpy.ndarray, numpy.ndarray
    :raises TypeError: if any of the error arrays does not have shape (2, n) or (n,).

    .. seealso:: :func:`pull`
    '''
    res = np.array(vals - ref, dtype=float)

    for a in filter(lambda e: e is not None, (err, ref_err)):
        if (len(a.shape) == 2 and a.shape[0] != 2) or len(a.shape) > 2:
            raise TypeError('The error arrays must have shape (2, n) or (n,)')

    if ref_err is not None:
        # Recalculate the error using the sum of squares rule
        if len(ref_err.shape) == 2:
            ref_err = ref_err[::-1]

        err = np.sqrt(ref_err*ref_err + err*err)

    return res, err
