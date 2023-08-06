'''
Function and classes representing statistical tools.
'''

__author__ = ['Miguel Ramos Pernas']
__email__  = ['miguel.ramos.pernas@cern.ch']


# Python
import os, warnings
import numpy as np
from collections import namedtuple
from math import exp, log, sqrt
from scipy.interpolate import interp1d
from scipy.optimize import fsolve
from scipy.special import gamma
from scipy.stats import beta, chi2, kstwobign, poisson
from scipy.stats import ks_2samp as scipy_ks_2samp

# Local
from hep_spt import __project_path__
from hep_spt.core import decorate, taking_ndarray

# Define confidence intervals.
__chi2_one_dof__ = chi2(1)
__one_sigma__    = __chi2_one_dof__.cdf(1)

# Number after which the poisson uncertainty is considered to
# be the same as that of a gaussian with "std = sqrt(lambda)".
__poisson_to_gauss__ = 200


__all__ = ['calc_poisson_fu',
           'calc_poisson_llu',
           'cp_fu',
           'FlatDistTransform',
           'ks_2samp',
           'gauss_u',
           'poisson_fu',
           'poisson_llu',
           'rv_random_sample',
           'stat_values',
           'sw2_u'
          ]


def _access_db( name ):
    '''
    Access a database table under 'data/'.

    :param name: name of the file holding the data.
    :type name: str
    :returns: Array holding the data.
    :rtype: numpy.ndarray
    '''
    ifile = os.path.join(__project_path__, 'data', name)

    table = np.loadtxt(ifile)

    return table


@decorate(np.vectorize)
def calc_poisson_fu( m, cl = __one_sigma__ ):
    '''
    Return the lower and upper frequentist uncertainties for
    a poisson distribution with mean "m".

    :param m: mean of the Poisson distribution.
    :type m: float or np.ndarray(float)
    :param cl: confidence level (between 0 and 1).
    :type cl: float or np.ndarray(float)
    :returns: Lower and upper uncertainties.
    :rtype: (float, float) or np.ndarray(float, float)

    .. note:: This function might turn very time consuming. Consider using :func:`poisson_fu` instead.
    '''
    sm = sqrt(m)

    alpha = (1. - cl)/2.

    il, ir = _poisson_initials(m)

    if m < 1:
        # In this case there is only an upper uncertainty, so
        # the coverage is reset so it covers the whole "cl"
        lw = m
        alpha *= 2.
    else:
        fleft = lambda l: 1. - (poisson.cdf(m, l) - poisson.pmf(m, l)) - alpha

        lw = fsolve(fleft, il)[0]

    fright = lambda l: poisson.cdf(m, l) - alpha

    up = fsolve(fright, ir)[0]

    return _process_poisson_u(m, lw, up)


@decorate(np.vectorize)
def calc_poisson_llu( m, cl = __one_sigma__ ):
    '''
    Calculate poisson uncertainties based on the logarithm of likelihood.

    :param m: mean of the Poisson distribution.
    :type m: float or numpy.ndarray(float)
    :param cl: confidence level (between 0 and 1).
    :type cl: float or numpy.ndarray(float)
    :returns: Lower and upper uncertainties.
    :rtype: (float, float) or numpy.ndarray(float, float)

    .. note:: This function might turn very time consuming. Consider using :func:`poisson_llu` instead.
    '''
    ns = np.sqrt(__chi2_one_dof__.ppf(cl))

    nll = lambda x: -2.*np.log(poisson.pmf(m, x))

    ref = nll(m)

    func = lambda x: nll(x) - ref - ns

    il, ir = _poisson_initials(m)

    if m < 1:
        lw = m
    else:
        lw = fsolve(func, il)[0]

    up = fsolve(func, ir)[0]

    return _process_poisson_u(m, lw, up)


@taking_ndarray
def cp_fu( k, N, cl = __one_sigma__ ):
    '''
    Return the frequentist Clopper-Pearson uncertainties of having
    "k" events in "N".

    :param k: passed events.
    :type k: int or numpy.ndarray(int)
    :param N: total number of events.
    :type N: int or numpy.ndarray(int)
    :param cl: confidence level.
    :type cl: float or numpy.ndarray(float)
    :returns: Lower and upper uncertainties on the efficiency.
    :rtype: float or numpy.ndarray(float)
    '''
    p = k.astype(float)/N

    pcl = 0.5*(1. - cl)

    if k.ndim == 0:
        if k != 0:
            lw = beta(k, N - k + 1).ppf(pcl)
        else:
            lw = p

        if k != N:
            up = beta(k + 1, N - k).ppf(1. - pcl)
        else:
            up = p
    else:

        # Solve for low uncertainty
        lw = np.array(p)
        cd = (k != 0)

        if pcl.ndim == 0:
            lpcl = pcl
        else:
            lpcl = pcl[cd]

        lk, lN = k[cd], N[cd]

        lw[cd] = beta(lk, lN - lk + 1).ppf(lpcl)

        # Solve for upper uncertainty
        up = np.array(p)
        cd = (k != N)

        if pcl.ndim == 0:
            upcl = pcl
        else:
            upcl = pcl[cd]

        uk, uN = k[cd], N[cd]

        up[cd] = beta(uk + 1, uN- uk).ppf(1. - upcl)

    return p - lw, up - p


class FlatDistTransform(object):
    '''
    Instance to transform values following an unknown distribution :math:`f(x)`
    into a flat distribution. This class takes into account the inverse
    transform sampling theorem, which states that, given a distribution
    :math:`f(x)` where :math:`x\\in[a, b]` then, given a random variable
    following a flat distribution *r*,

    .. math::
       F(x) - F(x_0) = \int_{x_0}^x f(x) dx = \int_0^r r dr = r

    where :math:`F(x)` is the primitive of :math:`f(x)`. This allows us to
    generate values following the distribution :math:`f(x)` given values from
    a flat distribution

    .. math::
       x = F^{-1}(r + F(x_0))

    In this class, the inverse process is performed. From a given set of values
    of a certain distribution, we build a method to generate numbers following
    a flat distribution.

    The class performs an interpolation to get the transformated values from
    an array holding the cumulative of the distribution. The function
    :func:`scipy.interpolate.interp1d` is used for this purpose.
    '''
    def __init__( self, points, values=None, kind='cubic' ):
        '''
        Build the class from a given set of values following a certain
        distribution (the use of weights is allowed), or x and y values of
        a PDF. This last method is not recommended, since the precision
        relies on the dispersion of the values, sometimes concentrated around
        peaking regions which might not be well described by an interpolation.

        :param points: x-values of the distribution (PDF).
        :type points: numpy.ndarray
        :param values: weights or PDF values to use.
        :type values: numpy.ndarray
        :param kind: kind of interpolation to use. For more details see \
        :func:`scipy.interpolate.interp1d`.
        :type kind: str or int
        '''
        srt = points.argsort()

        points = points[srt]
        if values is None:
            c = np.linspace(1./len(points), 1., len(points))
        else:
            c  = np.cumsum(values[srt])
            c *= 1./c[-1]

        self._trans = interp1d(points, c,
                               copy=False,
                               kind=kind,
                               bounds_error=False,
                               fill_value=(0, 1)
        )

    def transform( self, values ):
        '''
        Return the value of the transformation of the given values.

        :param values: values to transform.
        :type values: numpy.ndarray
        '''
        return self._trans(values)


def gauss_u( s, cl = __one_sigma__ ):
    '''
    Calculate the gaussian uncertainty for a given confidence level.

    :param s: standard deviation of the gaussian.
    :type s: float or numpy.ndarray(float)
    :param cl: confidence level.
    :type cl: float
    :returns: Gaussian uncertainty.
    :rtype: float or numpy.ndarray(float)

    .. seealso:: :func:`poisson_fu`, :func:`poisson_llu`, :func:`sw2_u`
    '''
    n = np.sqrt(__chi2_one_dof__.ppf(cl))

    return n*s


def _ks_2samp_values( arr, weights = None ):
    '''
    Calculate the values needed to perform the Kolmogorov-Smirnov test.

    :param arr: input sample.
    :type arr: numpy.ndarray
    :param weights: possible weights.
    :type weights: None or numpy.ndarray
    :returns: Sorted sample, stack with the cumulative distribution and
    sum of weights.
    :rtype: numpy.ndarray, numpy.ndarray, float
    '''
    weights = weights if weights is not None else np.ones(len(arr), dtype=float)

    ix  = np.argsort(arr)
    arr = arr[ix]
    weights = weights[ix]

    cs = np.cumsum(weights)

    sw = cs[-1]

    hs = np.hstack((0, cs/sw))

    return arr, hs, sw


def ks_2samp( a, b, wa = None, wb = None ):
    '''
    Compute the Kolmogorov-Smirnov statistic on 2 samples.
    This is a two-sided test for the null hypothesis that 2 independent
    samples are drawn from the same continuous distribution.
    Weights for each sample are accepted. If no weights are provided, then
    the function :func:`scipy.stats.ks_2samp` is called instead.

    :param a: first sample.
    :type a: numpy.ndarray
    :param b: second sample.
    :type b: numpy.ndarray
    :param wa: set of weights for "a". Same length as "a".
    :type wa: numpy.ndarray or None.
    :param wb: set of weights for "b". Same length as "b".
    :type wb: numpy.ndarray or None.
    :returns: Test statistic and two-tailed p-value.
    :rtype: float, float
    '''
    if wa is None and wb is None:
        return scipy_ks_2samp(a, b)

    a, cwa, na = _ks_2samp_values(a, wa)
    b, cwb, nb = _ks_2samp_values(b, wb)

    m = np.concatenate([a, b])

    cdfa = cwa[np.searchsorted(a, m, side='right')]
    cdfb = cwb[np.searchsorted(b, m, side='right')]

    d = np.max(np.abs(cdfa - cdfb))

    en = np.sqrt(na*nb/float(na + nb))
    try:
        prob = kstwobign.sf((en + 0.12 + 0.11/en)*d)
    except:
        prob = 1.

    return d, prob


# Tuple to hold the return values of the function "stat_values"
StatValues = namedtuple('StatValues', ('mean', 'var', 'std', 'var_mean', 'std_mean'))


def stat_values( arr, axis = None, weights = None ):
    '''
    Calculate mean and variance and standard deviations of the sample and the
    mean from the given array.
    Weights are allowed.
    The definition of the aforementioned quantities are:

    - Mean:

    .. math::
       \\bar{x} = \\sum_{i=0}^{n - 1}{\\frac{x_i}{n}}

    - Weighted mean:

    .. math::
       \\bar{x}^w = \\frac{\\sum_{i=0}^{n - 1}{\omega_i x_i}}{\\sum_{i=0}^{n - 1}{\omega_i}}

    - Variance of the sample:

    .. math::
       \sigma_s = \sum_{i=0}^{n - 1}{\\frac{(x_i - \\bar{x})^2}{n - 1}}

    - Weighted variance of the sample:

    .. math::
       \sigma^w_s = \\frac{N'}{(N' - 1)}\\frac{\sum_{i=0}^{n - 1}{\omega_i(x_i - \\bar{x}^w)^2}}{\sum_{i=0}^{n - 1}{\omega_i}}

    where :math:`\omega_i` refers to the weights associated with the value
    :math:`x_i`, and in the last equation N' refers to the number of non-zero
    weights. The variance and standard deviations of the mean are then given by:

    - Standard deviation of the mean:

    .. math::
       s_\\bar{x} = \\sqrt{\\frac{\sigma_s}{n}}

    - Weighted standard deviation of the mean:

    .. math::
       s^w_\\bar{x} = \\sqrt{\\frac{\sigma^w_s}{N'}}

    :param arr: input array of data.
    :type arr: numpy.ndarray
    :param axis: axis or axes along which to calculate the values for "arr".
    :type axis: None or int or tuple(int)
    :param weights: array of weights associated to the values in "arr".
    :type weights: None or numpy.ndarray
    :returns: Mean, variance, standard deviation, variance of the mean and \
    standard deviation of the mean.
    :rtype: numpy.ndarray, numpy.ndarray, numpy.ndarray, numpy.ndarray, numpy.ndarray
    '''
    keepdims = (axis is not None)

    asum = lambda a: np.sum(a, axis=axis, keepdims=keepdims, dtype=float)

    if weights is None:

        mean = np.mean(arr, axis=axis, keepdims=keepdims)

        if keepdims:
            lgth = arr.shape[axis]
        else:
            lgth = arr.size

        var = asum((arr - mean)**2)/(lgth - 1.)

        var_mean = var/lgth

    else:
        sw = asum(weights)

        # We can not use "count_nonzero" ince it does not keep
        # the dimensions through "keepdims"
        nzw = asum(weights != 0)

        mean = asum(weights*arr)/sw
        var  = asum(weights*(arr - mean)**2)*nzw/(sw*(nzw - 1.))

        var_mean = var/nzw

    std = np.sqrt(var)

    std_mean = np.sqrt(var_mean)

    return StatValues(mean, var, std, var_mean, std_mean)


def poisson_fu( m ):
    '''
    Return the poisson frequentist uncertainty at one standard
    deviation of confidence level.

    :param m: measured value(s).
    :type m: int or numpy.ndarray(int)
    :returns: Lower and upper frequentist uncertainties.
    :rtype: numpy.ndarray(float, float)

    .. seealso:: :func:`gauss_u`, :func:`poisson_llu`, :func:`sw2_u`
    '''
    return _poisson_u_from_db(m, 'poisson_fu.dat')


def poisson_llu( m ):
    '''
    Return the poisson uncertainty at one standard deviation of
    confidence level. The lower and upper uncertainties are defined
    by those two points with a variation of one in the value of the
    negative logarithm of the likelihood multiplied by two:

    .. math::
       \sigma_\\text{low} = n_\\text{obs} - \lambda_\\text{low}

    .. math::
       \\alpha - 2\log P(n_\\text{obs}|\lambda_\\text{low}) = 1

    .. math::
       \sigma_\\text{up} = \lambda_\\text{up} - n_\\text{obs}

    .. math::
       \\alpha - 2\log P(n_\\text{obs}|\lambda_\\text{up}) = 1

    where :math:`\\alpha = 2\log P(n_\\text{obs}|n_\\text{obs})`.

    :param m: measured value(s).
    :type m: int or numpy.ndarray(int)
    :returns: Lower and upper frequentist uncertainties.
    :rtype: numpy.ndarray(float, float)

    .. seealso:: :func:`gauss_u`, :func:`poisson_fu`, :func:`sw2_u`
    '''
    return _poisson_u_from_db(m, 'poisson_llu.dat')


@taking_ndarray
def _poisson_initials( m ):
    '''
    Return the boundaries to use as initial values in
    scipy.optimize.fsolve when calculating poissonian
    uncertainties.

    :param m: mean of the Poisson distribution.
    :type m: float or numpy.ndarray(float)
    :returns: Upper and lower boundaries.
    :rtype: (float, float) or numpy.ndarray(float, float)
    '''
    sm = np.sqrt(m)

    il = m - sm
    ir = m + sm

    # Needed by "calc_poisson_llu"
    if il.ndim == 0:
        if il <= 0:
            il = 0.1
    else:
        il[il <= 0] = 0.1

    return il, ir


def _poisson_u_from_db( m, database ):
    '''
    Used in functions to calculate poissonian uncertainties,
    which are partially stored on databases. If "m" is above the
    maximum number stored in the database, the gaussian approximation
    is taken instead.

    :param m: measured value(s).
    :type m: int or numpy.ndarray(int)
    :param database: name of the database.
    :type database: str
    :returns: Lower and upper frequentist uncertainties.
    :rtype: (float, float) or numpy.ndarray(float, float)
    :raises TypeError: if the input is a (has) non-integer value(s).
    :raises ValueError: if the input value(s) is(are) not positive.
    '''
    m = np.array(m)
    if not np.issubdtype(m.dtype, np.integer):
        raise TypeError('Calling function with a non-integer value')
    if np.any(m < 0):
        raise ValueError('Values must be positive')

    scalar_input = False
    if m.ndim == 0:
        m = m[None]
        scalar_input = True

    no_app = (m < __poisson_to_gauss__)

    if np.count_nonzero(no_app) == 0:
        # We can use the gaussian approximation in all
        out = np.array(2*[np.sqrt(m)]).T
    else:
        # Non-approximated uncertainties
        table = _access_db(database)

        out = np.zeros((len(m), 2), dtype = np.float64)

        out[no_app] = table[m[no_app]]

        mk_app = np.logical_not(no_app)

        if mk_app.any():
            # Use the gaussian approximation for the rest
            out[mk_app] = np.array(2*[np.sqrt(m[mk_app])]).T

    if scalar_input:
        return np.squeeze(out)
    return out


def _process_poisson_u( m, lw, up ):
    '''
    Calculate the uncertainties and display an error if they
    have been incorrectly calculated.

    :param m: mean value.
    :type m: float
    :param lw: lower bound.
    :type lw: float
    :param up: upper bound.
    :type up: float
    :returns: Lower and upper uncertainties.
    :type: numpy.ndarray(float, float)
    '''
    s_lw = m - lw
    s_up = up - m

    if any(s < 0 for s in (s_lw, s_up)):
        warnings.warn('Poisson uncertainties have been '\
                      'incorrectly calculated')

    # numpy.vectorize needs to know the exact type of the output
    return float(s_lw), float(s_up)


def rv_random_sample( func, size = 10000, **kwargs ):
    '''
    Create a random sample from the given rv_frozen object.
    This is usually used after creating a :class:`scipy.stats.rv_discrete`
    or :class:`scipy.stats.rv_continuous` class.

    :param func: function to use for the generation.
    :type func: :class:`scipy.stats.rv_frozen`
    :param size: size of the sample.
    :type size: int
    :param kwargs: any other argument to :class:`scipy.stats.rv_frozen.rvs`.
    :type kwargs: dict
    :returns: Generated sample.
    :rtype: numpy.ndarray
    '''
    args = np.array(func.args)

    if len(args.shape) == 1:
        size = (size,)
    else:
        size = (size, args.shape[1])

    return func.rvs(size=size, **kwargs)


def sw2_u( arr, bins = 20, range = None, weights = None ):
    '''
    Calculate the errors using the sum of squares of weights.
    The uncertainty is calculated as follows:

    .. math::

       \sigma_i = \sqrt{\sum_{j = 0}^{n - 1} \omega_{i,j}^2}

    where *i* refers to the i-th bin and :math:`j \in [0, n)` refers to
    each entry in that bin with weight :math:`\omega_{i,j}`. If "weights" is
    None, then this coincides with the square root of the number of entries
    in each bin.

    :param arr: input array of data to process.
    :param bins: see :func:`numpy.histogram`.
    :type bins: int, sequence of scalars or str
    :param range: range to process in the input array.
    :type range: None or tuple(float, float)
    :param weights: possible weights for the histogram.
    :type weights: None or numpy.ndarray(value-type)
    :returns: Symmetric uncertainty.
    :rtype: numpy.ndarray

    .. seealso:: :func:`gauss_u`, :func:`poisson_fu`, :func:`poisson_llu`
    '''
    if weights is not None:
        values = np.histogram(arr, bins, range, weights = weights*weights)[0]
    else:
        values = np.histogram(arr, bins, range)[0]

    return np.sqrt(values)


if __name__ == '__main__':
    '''
    Generate the tables to store the pre-calculated values of
    some uncertainties.
    '''
    m = np.arange(__poisson_to_gauss__)

    print('Creating databases:')
    for func in (calc_poisson_fu, calc_poisson_llu):

        ucts = np.array(func(m, __one_sigma__)).T

        name = func.__name__.replace('calc_', '') + '.dat'

        fpath = os.path.join('data', name)

        print('- {}'.format(fpath))

        np.savetxt(fpath, ucts)
