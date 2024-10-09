import numpy as np
import numpy.typing as npt
from scipy import stats

from ..schemas.prior import VolumePrior


class ConjugateNormal:
    def __init__(self, prior: VolumePrior, percentile=0.20):
        """
        mu: prior mean
        k: uncertainty about the prior mean (pseudo-samples)
        alpha: shape of variance distribution
        beta: scale of variance distribution

        """
        self.mu = prior.mean
        self.k = prior.support
        self.alpha = prior.alpha
        self.beta = prior.beta
        self.percentile = percentile

    def update(self, x: npt.ArrayLike):
        """x: data"""
        self.mu = self.posterior_mean(x)
        self.alpha = self.posterior_alpha(x)
        self.beta = self.posterior_beta(x)
        self.k += len(x)

    def posterior_mean(self, x):
        n = len(x)
        numerator = (self.k * self.mu) + (n * np.mean(x))
        denominator = self.k + n
        return numerator / denominator

    def posterior_alpha(self, x):
        n = len(x)
        return self.alpha + (n / 2)

    def posterior_beta(self, x):
        n = len(x)
        mu_1 = np.mean(x)
        ssd = self.sum_square_diffs(x, mu_1)
        sd = (mu_1 - self.mu) ** 2
        return self.beta + 0.5 * (ssd + (self.k * n * sd) / (self.k + n))

    @property
    def sigma(self):
        assert self.alpha > 1, "alpha must be greater than 1"
        return np.sqrt(self.beta / (self.alpha - 1))

    @property
    def threshold(self):
        return stats.norm.ppf(self.percentile, loc=self.mu, scale=self.sigma)

    def sum_square_diffs(self, A, B):
        """Sum of squared differences"""
        squared_differences = (A - B) ** 2
        return np.sum(squared_differences)
