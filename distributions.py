"""
Distribution utility classes to be used in other projects.
"""

import numpy as np
import math


class Lognormal:
    """Lognormal distribution sampler.

    Parameters
    ----------
    mean : float
        Mean of the lognormal distribution.
    stdev : float
        Standard deviation of the lognormal distribution.
    seed : int or numpy.random.SeedSequence, optional
        Seed for the RNG.
    """
    def __init__ (
        self,
        mean,
        stdev,
        seed=None
    ):
        self.rand = np.random.default_rng(seed)
        mu, sigma = self.normal_moments_from_lognormal(mean, stdev**2)
        self.mu = mu
        self.sigma = sigma
        self.mean = mean
        self.stdev = stdev
    
    def normal_moments_from_lognormal(self, m, v):
        phi = math.sqrt(v + m**2)
        mu = math.log(m**2 / phi)
        sigma = math.sqrt(math.log(phi**2 / m**2))
        return mu, sigma
    
    def sample(self, size=None):
        return self.rand.lognormal(self.mu, self.sigma, size)
        
        
        
class Exponential:
    """Exponential distribution sampler.

    Parameters
    ----------
    mean : float
        Mean of the exponential distribution.
    seed : int or numpy.random.SeedSequence, optional
        Seed for the RNG.
    """
    def __init__(self, mean, seed=None):
        self.rand = np.random.default_rng(seed)
        self.mean = mean
        
    def sample(self, size=None):
        return self.rand.exponential(self.mean, size)
    


class Normal:
    """Normal (Gaussian) distribution sampler.

    Parameters
    ----------
    mean : float
        Mean of the normal distribution.
    stdev : float
        Standard deviation of the normal distribution.
    seed : int or numpy.random.SeedSequence, optional
        Seed for the RNG.
    """
    def __init__(self, mean, stdev, seed=None):
        self.rand = np.random.default_rng(seed)
        self.mean = mean
        self.stdev = stdev

    def sample(self, size=None):
        return self.rand.normal(self.mean, self.stdev, size)
    


class Bernoulli:
    """Bernoulli distribution sampler.

    Parameters
    ----------
    p : float
        Probability of success in each trial.
    seed : int or numpy.random.SeedSequence, optional
        Seed for the RNG.
    """
    def __init__(self, p, seed=None):
        self.rand = np.random.default_rng(seed)
        self.p = p

    def sample(self, size=None):
        return self.rand.binomial(n=1, p=self.p, size=size)
    

class Weibull:
    """Weibull distribution sampler.

    Parameters
    ----------
    k : float
        Shape parameter of the Weibull distribution.
    lmbd : float
        Scale parameter of the Weibull distribution.
    seed : int or numpy.random.SeedSequence, optional
        Seed for the RNG.
    """
    def __init__(self, k, lmbd, seed=None):
        self.rand = np.random.default_rng(seed)
        self.k = k
        self.lmbd = lmbd
        
    def sample(self, size=None):
        return self.rand.weibull(self.k, size) * self.lmbd
    
    
class Uniform:
    """Uniform distribution sampler.

    Parameters
    ----------
    a : float
        Lower bound of the uniform distribution.
    b : float
        Upper bound of the uniform distribution.
    seed : int or numpy.random.SeedSequence, optional
        Seed for the RNG.
    """
    def __init__(self, a, b, seed=None):
        self.rand = np.random.default_rng(seed)
        self.a = a
        self.b = b
        
    def sample(self, size=None):
        return self.rand.uniform(low=self.a, high=self.b, size=size)