'''
Classes and functions to work with the CLs method.
'''

__author__ = ['Miguel Ramos Pernas']
__email__  = ['miguel.ramos.pernas@cern.ch']


# Python
import numpy as np
from scipy.stats import rv_discrete, rv_continuous
from collections import namedtuple

# Local
from hep_spt.core import decorate
from hep_spt.stats import rv_random_sample

__all__ = [
    'CLsTS', 'CLsTS_discrete', 'CLsTS_continuous',
    'CLsHypo', 'CLsHypo_discrete', 'CLsHypo_continuous',
    'cls_hypo', 'cls_ts'
    ]

# Class to hold the results of a CLs evaluation
CLsResult = namedtuple('CLsResult', ('CLs', 'CLb', 'CLsb'))


class CLsTS(object):

    def __init__( self, alt, null ):
        '''
        Base class to represent the test-statistics function to work with the
        CLs method. The class is built from the alternative and null hypotheses.

        :param alt: alternative hypothesis.
        :type alt: CLsHypo
        :param null: null hypothesis.
        :type null: CLsHypo

        :ivar ah: alternative hypothesis.
        :ivar nh: null hypothesis.

        .. seealso:: :class:`CLsTS_discrete`, :class:`CLsTS_continuous`
        '''
        self.ah = alt
        self.nh = null

    def _cl( self, hyp, tv, size ):
        '''
        Method to get the confidence level for a given hypothesis and value for
        the test statistics. The size determines the precision of the output
        value.

        :param hyp: hypothesis.
        :type hyp: CLsHypo
        :param tv: value of the test-statistics.
        :type tv: numpy.ndarray
        :param size: size of the sample to generate.
        :type size: int
        :returns: Confidence level.
        :rtype: float
        '''
        raise NotImplementedError('Attempt to call abstract class method')

    def test_stat( self, v ):
        '''
        Calculate the test-statistics associated to the given value.

        :param v: input value:
        :type v: numpy.ndarray
        :returns: Value of the test-statistics.
        :rtype: float
        '''
        num = self.ah(v)
        den = self.nh(v)

        return np.log(num/den)

    def evaluate( self, v, size = 100000 ):
        '''
        Calculate the CLs, CLb and CLsb for the given value. In order to boost
        any script using this function, and to prevent misbehaviours due
        to the use of different generated samples, it is recommended to call it
        using an array. As an examples, oftenly one wants to evaluate this
        function on the median, 1 and 2 \sigma intervals, and on the observed
        value. All this can be passed to the function as an array, and the
        CLsResult instance will contain, instead of single floating values,
        numpy.ndarray objects.

        :param v: input value
        :type v: numpy.ndarray
        :param size: size of the sample to generate.
        :type size: int
        :returns: Tuple with the CLs, CLb and CLsb values.
        :rtype: collections.namedtuple
        '''
        tv = self.test_stat(v)

        clsb = self._cl(self.ah, tv, size)

        clb = self._cl(self.nh, tv, size)

        cls = clsb/clb

        return CLsResult(cls, clb, clsb)


class CLsTS_discrete(CLsTS):

    def __init__( self, alt, null ):
        '''
        Base class to represent the test-statistics function to work with the
        CLs method using hypothesis working on a discrete domain. The class is
        built from the alternative and null hypotheses.

        :param alt: alternative hypothesis.
        :type alt: CLsHypo
        :param null: null hypothesis.
        :type null: CLsHypo

        :ivar ah: alternative hypothesis.
        :ivar nh: null hypothesis.

        .. seealso:: :class:`CLsTS`, :class:`CLsTS_continuous`
        '''
        CLsTS.__init__(self, alt, null)

    def _cl( self, hyp, tv, size ):
        '''
        Method to get the confidence level for a given hypothesis and value for
        the test statistics. The size determines the precision of the output
        value.

        :param hyp: hypothesis.
        :type hyp: CLsHypo
        :param tv: value of the test-statistics.
        :type tv: float or numpy.ndarray
        :param size: size of the sample to generate.
        :type size: int
        '''
        smp = rv_random_sample(hyp.func, size=size)

        ts = self.test_stat(smp)

        # Apart from boosting the process, this allows to correctly
        # calculate the CLs, since in the discrete case there can
        # be several cases where the values of the test-statistics are
        # the same.
        ts, values = np.unique(ts, return_counts=True)

        cs = values.cumsum()*1./size

        idx = np.searchsorted(ts, tv)

        if idx.ndim != 0:
            idx[idx == len(values)] -= 1
        elif idx == len(values):
            idx -= 1

        return cs[idx]


class CLsTS_continuous(CLsTS):

    def __init__( self, alt, null ):
        '''
        Base class to represent the test-statistics function to work with the
        CLs method using hypothesis working on a continuous domain.
        The class is built from the alternative and null hypotheses.

        :param alt: alternative hypothesis.
        :type alt: CLsHypo
        :param null: null hypothesis.
        :type null: CLsHypo

        :ivar ah: alternative hypothesis.
        :ivar nh: null hypothesis.

        .. seealso:: :class:`CLsTS`, :class:`CLsTS_discrete`
        '''
        CLsTS.__init__(self, alt, null)

    def _cl( self, hyp, tv, size ):
        '''
        Method to get the confidence level for a given hypothesis and value for
        the test statistics. The size determines the precision of the output
        value.

        :param hyp: hypothesis.
        :type hyp: CLsHypo
        :param tv: value of the test-statistics.
        :type tv: numpy.ndarray
        :param size: size of the sample to generate.
        :type size: int
        '''
        smp = rv_random_sample(hyp.func, size=size)

        ts = self.test_stat(smp)

        srt = ts.argsort()

        ts = ts[srt]

        cs = np.linspace(1./size, 1., size)

        idx = np.searchsorted(ts, tv)

        if idx.ndim != 0:
            idx[idx == size] -= 1
        elif idx == len(values):
            idx -= 1

        return cs[idx]


@decorate
def _call_wrap( meth ):
    '''
    Wrapper function for the __call__ method of classes inheriting from
    :class:`CLsHypo`.

    :param meth: method to wrap.
    :type meth: method
    :returns: Wrapped function.
    :rtype: function
    '''
    def _wrapper( self, *args, **kwargs ):
        '''
        Wrapper function which calls the method multiplying the probabilities
        if necessary.
        '''
        prob = meth(self, *args, **kwargs)

        la = len(np.array(self.func.args).shape)
        lp = len(prob.shape)

        if lp == 1:

            # The probability is an array of the form (n,)

            if la != 1:

                # The arguments of the probability function are arrays

                prob = np.prod(prob)

        elif lp == 2:

            # Multiply the probabilities for each column

            prob = np.prod(prob, axis=1)

        return prob

    return _wrapper


class CLsHypo(object):

    def __init__( self, pf ):
        '''
        Represent an hypothesis to be used in the CLs method.
        The class is built from a given probability function.

        :param pf: probability density/mass function.
        :type pf: scipy.stats.rv_frozen

        :ivar func: probability density/mass function representing the \
        hypothesis.

        .. seealso:: :class:`CLsHypo_discrete`, :class:`CLsHypo_continuous`
        '''
        self.func = pf

    def __call__( self, v ):
        '''
        Calculate the global probability for the given input value(s). If the
        arguments of the probability function are arrays, then it is assumed
        that "v" is either an array of length equal to the number of values
        per argument, or that it is an array of arrays following the latter
        structure. If "v" does not match any of the previous requirements,
        then the global probability is calculated assuming this value for
        all the sub-functions. Assuming "pmf" as "poisson.pmf":

        >>> import numpy as np
        >>> from scipy.stats import poisson
        >>> ha = cls_hypo(poisson, 4)
        >>> ha(4) # Same as pmf(4, 4)
        0.19536681481316454
        >>> hb = cls_hypo(poisson, np.array([4, 8]))
        >>> hb([4, 8]) # Same as pmf(4, 4)*pmf(4, 8)
        0.02727057613800409
        >>> hb([[4, 8], [6, 10]]) # Same as [pmf(4, 4)*pmf(8, 8), pmf(6, 4)*pmf(10, 8)]
        >>> hb(4) # Same as pmf(4, 4)*pmf(4, 4)
        0.011185197244103258

        :param v: input value(s).
        :type v: numpy.ndarray
        :returns: Global probability.
        :rtype: float
        '''
        raise NotImplementedError('Attempt to call abstract class method')

    def median( self ):
        '''
        Calculate the median of the distribution associated to this
        hypothesis. This is equivalent to call CLsHypo.percentil(0.5).

        :returns: Median of the distribution.
        :rtype: numpy.ndarray
        '''
        return self.percentil(0.5)

    def percentil( self, prob ):
        '''
        Calculate the percentil associated to the given probability.

        :param prob: probability.
        :type prob: float
        :returns: Percentil.
        :rtype: numpy.ndarray
        '''
        return self.func.ppf(prob)


class CLsHypo_discrete(CLsHypo):

    def __init__( self, pmf ):
        '''
        Represent an hypothesis which works on a discrete domain.
        The class is built from a given probability function.

        :param pmf: probability mass function.
        :type pmf: scipy.stats.rv_frozen

        :ivar func: probability mass function representing the hypothesis.

        .. seealso:: :class:`CLsHypo`, :class:`CLsHypo_continuous`
        '''
        CLsHypo.__init__(self, pmf)

    @_call_wrap
    def __call__( self, v ):
        '''
        Calculate the global probability for the given input value(s). See
        :meth:`CLsHypo.__call__` for more details.

        :param v: input value(s).
        :type v: numpy.ndarray
        :returns: Global probability.
        :rtype: float
        '''
        return self.func.pmf(v)


class CLsHypo_continuous(CLsHypo):

    def __init__( self, pdf ):
        '''
        Represent an hypothesis which works on a continuous domain.
        The class is built from a given probability function.

        :param pdf: probability density function.
        :type pdf: scipy.stats.rv_frozen

        :ivar func: probability density function representing the hypothesis.

        .. seealso:: :class:`CLsHypo`, :class:`CLsHypo_discrete`
        '''
        CLsHypo.__init__(self, pdf)

    @_call_wrap
    def __call__( self, v ):
        '''
        Calculate the global probability for the given input value(s). See
        :meth:`CLsHypo.__call__` for more details.

        :param v: input value(s).
        :type v: numpy.ndarray
        :returns: Global probability.
        :rtype: float
        '''
        return self.func.pdf(v)


def cls_ts( alt, null ):
    '''
    Create an instance of :class:`CLsTS` from the alternative an null
    hypotheses.
    A check is done to see if both refere to the same type of probability
    function (discrete or continuous).

    :param alt: alternative hypothesis.
    :type alt: CLsHypo
    :param null: null hypothesis.
    :type null: CLsHypo
    :returns: CLs test-statistics proxy.
    :rtype: CLsTS
    :raises RuntimeError: if the type of both hypotheses is different.

    .. seealso:: :class:`CLsTS_discrete`, :class:`CLsTS_continuous`
    '''
    discrete = isinstance(alt, CLsHypo_discrete)
    if discrete != isinstance(null, CLsHypo_discrete):
        raise RuntimeError('Both hypotheses must be of the same type')

    if discrete:
        return CLsTS_discrete(alt, null)
    else:
        return CLsTS_continuous(alt, null)


def cls_hypo( func, *args, **kwargs ):
    '''
    Create an instance of CLsHypo given a probability density(mass) function,
    as an object of type :class:`scipy.stats.rv_discrete` or
    :class:`scipy.stats.rv_continuous`.

    :param func: probability function.
    :type func: scipy.stats.rv_discrete or scipy.stats.rv_continuous
    :param args: input arguments to "func".
    :type args: tuple
    :param kwargs: input arguments to "func".
    :type kwargs: dict

    .. seealso:: :class:`CLsHypo_discrete`, :class:`CLsHypo_continuous`
    '''
    if isinstance(func, rv_discrete):
        return CLsHypo_discrete(func(*args, **kwargs))
    else:
        return CLsHypo_continuous(func(*args, **kwargs))
