import scipy.stats as st
from scipy.special import erf
from scipy.interpolate import interp1d
import scipy.integrate as integrate
from collections import OrderedDict
import configparser
import multiprocessing
import numpy as np
import re
import click
from EPIC import root
from EPIC.utils import data_tools, io_tools, math_functions
import EPIC.cosmology.cosmic_objects as cosmo
from math import log
import os
try:
    import cPickle as pickle
except ImportError:
    import pickle

scipy_stats_standard_normal = st.distributions.norm(0, 1)
kde_numpoints = 500
kde2d_numpoints = 150

class Analysis(object):
    def __init__(self, datasets, model, prior_ranges, prior_distributions={},
            split={}, fixed={}):
        self.datasets = datasets
        self.model = model
        self.fixed = fixed

        nuisance_list = []
        for dataset in self.datasets.values():
            if hasattr(dataset, 'nuisance_parameters'):
                nuisance_list += list(dataset.nuisance_parameters.values())
                
        self.parameters = []
        self.derived_parameters = []
        for par in self.model.parameters + nuisance_list:
            if isinstance(par, cosmo.FreeParameter):
                if par.label in self.fixed:
                    if isinstance(par, cosmo.DensityFromTemperature):
                        par.temperature.fixed_value = self.fixed[par.label]
                    else:
                        par.fixed_value = self.fixed[par.label]
                else:
                    if par.label in prior_ranges:
                        interval = prior_ranges[par.label]
                        distribution = prior_distributions.get(par.label, 'Flat')
                        par.set_prior(*interval, distribution=distribution)
                    par.split = split.get(par.label)
                    self.parameters.append(par)
            elif isinstance(par, cosmo.DerivedParameter):
                self.derived_parameters.append(par)

        self.parnames = [par.label for par in self.parameters]
        self.nparams = len(self.parnames)

    def prepare_state(self, X):
        return OrderedDict(zip(self.parnames, X))

    def get_label(self):
        ini = configparser.ConfigParser()
        ini.read(self.ini_file)
        lbl = ini['analysis'].get('label')
        if lbl is None:
            return os.path.split(self.ini_file)[1]
        return lbl

    def log_likelihood(self, **kwargs):
        return np.sum([dataset.log_likelihood(
            getattr(self.model, dataset.predicting), **kwargs
            ) for dataset in self.datasets.values()], axis=0)

    def log_prior_probability(self, **kwargs):
        logprior = 0
        for par in self.parameters:
            if isinstance(par, cosmo.FreeParameter):
                parameter_space = kwargs.get('parameter_space', {})
                if par.label in parameter_space:
                    parameter_space_point = parameter_space[par.label]
                    assert hasattr(par, 'prior')
                    logprior += par.prior.log_prior_probability(
                            parameter_space_point)
                else:
                    accepts_default = kwargs.get('accepts_default', False)
                    assert accepts_default 
                    #dont do anything, logprior is zero
        return logprior

    def log_posterior(self, beta=1, interpolate_H=False, **kwargs):
        logprior = self.log_prior_probability(**kwargs)
        if np.isinf(logprior) or np.isnan(logprior):
            return -np.inf, -np.inf

        H_of_a_interpolate = self.cosmology_interpolate_H(**kwargs) \
                if interpolate_H else None

        chi2, ll = self.log_likelihood(H_of_a_interpolate=H_of_a_interpolate, **kwargs)
        #print('chi2', chi2)
        loglike = -chi2/2 if kwargs.get('chi2', False) else ll
        if np.isinf(loglike) or np.isnan(loglike):
            return -np.inf, -np.inf
        return beta * loglike + logprior, loglike

    def cosmology_interpolate_H(self, **kwargs):
        if not hasattr(self.model, 'a_range'):
            self.model.get_a_range(**kwargs)
        H_of_a = self.model.get_Hubble_Friedmann(self.model.a_range, **kwargs)
        return interp1d(self.model.a_range, H_of_a)

"""
class PT_Analysis(Analysis):
    def find_max_logposterior(self):
        maxlog = np.nanmax(self.list_of_chains[0][self.truncated_size//2:, self.nparams])
        max_index = list(self.list_of_chains[0][:,self.nparams]).index(maxlog) # this is the index in the entire list, not the slice!!!
        bestfit = [self.list_of_chains[0][max_index,i] for i in range(self.nparams)]
        maxlogposterior = self.list_of_chains[0][max_index,self.nparams]
        maxloglikelihood = self.list_of_chains[0][max_index,self.nparams+1]
        return maxlogposterior, maxloglikelihood, bestfit

    def logZ_thermo_integration(self, args):
        burn_in = getattr(args, 'burn_in', None)
        burn_in = burn_in or self.truncated_size//2
        interpol = getattr(args, 'interpolate_evidence', False)
        beta_means = np.array([self.list_of_chains[m][burn_in:,self.nparams+1].mean() for m, _ in enumerate(self.betas)])
        
        if interpol:
            from scipy import interpolate
            interp_beta_means = interpolate.interp1d(self.betas[::-1], beta_means[::-1], kind='linear')
            return integrate.quad(lambda b: interp_beta_means(b), self.betas[-1], 1)[0]
        else:
            np.savetxt(os.path.join(self.working_dir, 'beta_means_n%i.txt' % self.truncated_size), 
                    list(zip(self.betas[::-1], beta_means[::-1])))
            import matplotlib.pyplot as plt
            fig, ax = plt.subplots()
            ax.plot(self.betas[::-1], beta_means[::-1], lw=1, marker='s', markersize=3)
            ax.set_xlabel(r'$\beta$')
            ax.set_xscale('log')
            ax.set_ylabel(r'$\left\langle \ln \left[ p\left(D \mid M, X, I\right) \right] \right\rangle_{\beta}$')
            fig.savefig(os.path.join(self.working_dir, 'n%i' % self.truncated_size, 'beta_means.pdf'))
            return integrate.simps(beta_means[::-1], x=self.betas[::-1])

    def load_chains(self, args, stop_at=None): # PT
        with click.progressbar(length=len(self.chains), width=10,
                show_pos=True, empty_char='.',
                label=io_tools.fixed_length('Loading chains...'), info_sep=' | ', 
                show_eta=False) as bar:
            list_of_chains = [chain.load_from_file(progress_bar=bar) for chain in self.chains]
        self.truncated_size, self.list_of_chains = io_tools.truncate(
                list_of_chains, stop_at=stop_at)
        maxlogposterior, maxloglikelihood, bestfit = self.find_max_logposterior()
        AIC, BIC = self.Information_Criteria(maxloglikelihood)
        logZ = self.logZ_thermo_integration(args)
        info = configparser.ConfigParser()
        info.read(self.simulation_info)
        info.set('status', 'best fit', str(OrderedDict(zip(self.parnames, bestfit))))
        info.set('status', 'evidence', "%.2e" % logZ)
        info.set('status', 'AIC', "%.2f" % AIC)
        info.set('status', 'BIC', "%.2f" % BIC)
        with open(self.simulation_info, 'w+') as cfg:
            info.write(cfg)

    def separate_parameters_chains(self, args): #PT
        burn_in = getattr(args, 'burn_in', None)
        burn_in = burn_in or self.truncated_size//2
        return [self.list_of_chains[0][burn_in:,i] for i in range(self.nparams)]

    def walk_adapt_save(self, I, S, sig, cm, theta):
        np.savetxt(os.path.join(self.working_dir, 'theta%i.txt' % I), [theta,])
        np.savetxt(os.path.join(self.working_dir, 'chain_mean%i.txt' % I), cm)
        np.savetxt(os.path.join(self.working_dir, 'Sig%i.txt' % I), sig)
        np.savetxt(os.path.join(self.working_dir, 'Sm%i.txt' % I), S)
"""

class Bivariate_Normal(object):
    def __init__(self, Mu, Cov, factor=None):
        [a, b], [c, d] = np.array(Cov)
        self.Mu = np.array(Mu)
        self.detCov = a*d - b*c
        self.ICov = 1/self.detCov * np.array([[d, -b], [-c, a]])
        if factor is not None:
            self.detCov *= factor*factor
            self.ICov /= factor
        self.mvn_factor = 1/(2*np.pi)/np.sqrt(self.detCov)

    def pdf(self, support):
        support = np.array(support)#, ndmin=2)
        results = [ - 1/2 * np.dot( np.dot(sup-self.Mu, self.ICov), (sup-self.Mu).transpose()) for sup in support]
        if len(results) == 1:
            return self.mvn_factor * np.exp(results)[0]
        else:
            return self.mvn_factor * np.exp(results)

class ListDistributions(object):
    def __init__(self, listD):
        self.listD = listD

    def rvs(self):
        return np.array([l.rvs() for l in self.listD])   

    def pdf(self, X):
        return np.array([l.pdf(X) for l in self.listD])

class MixedDist(object):
    def __init__(self, xmode, xmin, xmax, NUM=None):
        self.lower_lim = xmin
        self.upper_lim = xmax
        self.mode, self.xplus, self.xminus = data_tools.convert_points_errorbars(xmode, xmin,
                xmax, fmt=None, factor=1)
        self.ampl_m = 2 * self.xminus / (self.xminus + self.xplus)
        self.ampl_p = 2 * self.xplus  / (self.xminus + self.xplus)

    def pdf(self, x):
        x = np.array(x)
        return np.where(
                x < self.mode,
                self.ampl_m * scipy_stats_standard_normal.pdf((x-self.mode)\
                        /self.xminus)/self.xminus, 
                self.ampl_p * scipy_stats_standard_normal.pdf((x-self.mode)\
                        /self.xplus)/self.xplus
                )

    def cdf(self, x):
        x = np.array(x)
        return np.where(
                x < self.mode,
                self.ampl_m * scipy_stats_standard_normal.cdf((x-self.mode)\
                        /self.xminus),
                self.ampl_p * scipy_stats_standard_normal.cdf((x-self.mode)\
                        /self.xplus)
                )

    def rvs(self, num=200000):
        np.random.seed()
        num_m = int(2*num * self.ampl_m)
        Zm = np.random.normal(size=num_m)
        Zm = Zm[Zm < 0]
        num_p = int(2*num * self.ampl_p)
        Zp = np.random.normal(size=num_p)
        Zp = Zp[Zp > 0]
        Z = np.concatenate([Zm, Zp])
        Z = Z[Z < 4] 
        Z = Z[Z > -4]
        np.random.shuffle(Z)
        Z = Z[:num]
        R = self.mode + Z * np.where(Z <= 0, self.xminus, self.xplus)
        return R

    def use_sample(self, a=None, b=None, num=10000):
        if hasattr(self, '_sample'):
            self_sample = self._sample
        else:
            self._sample = self.rvs(num=num)
            if a is not None:
                while self._sample[self._sample < a].size > 0:
                    new_samples = self.rvs(num=self._sample[self._sample < a].size)
                    self._sample = np.concatenate(
                            [self._sample[self._sample >= a], new_samples])
            if b is not None:
                while self._sample[self._sample > b].size > 0:
                    new_samples = self.rvs(num=self._sample[self._sample > b].size)
                    self._sample = np.concatenate(
                            [self._sample[self._sample <= b], new_samples])
            self_sample = self._sample
        return self_sample

    def __add__(self, other):
        if isinstance(other, MixedDist):
            z, function_sum = data_tools.pdf_convolution('sum', self, other)
            fit = fit_asymmetrical(None, kdefit_asym=(z, function_sum))
            return MixedDist(*fit)
        else:
            return MixedDist(
                    self.mode + other,
                    self.lower_lim + other,
                    self.upper_lim + other,
                    )

    def __radd__(self, other):
        return self.__add__(other)

    def __mul__(self, other):
        if isinstance(other, MixedDist):
            z, function_prod = data_tools.pdf_convolution('prod', self, other)
            fit = fit_asymmetrical(None, kdefit_asym=(z, function_prod))
            return MixedDist(*fit)
        else:
            if other == 0:
                return 0
            elif other > 0:
                return MixedDist(
                        other * self.mode,
                        other * self.lower_lim,
                        other * self.upper_lim
                        )
            else:
                return MixedDist(
                        other * self.mode,
                        other * self.upper_lim,
                        other * self.lower_lim,
                        )

    def __rmul__(self, other):
        return self.__mul__(other)

    def __sub__(self, other):
        if isinstance(other, MixedDist):
            z, function_subtract = data_tools.pdf_convolution('subtract', self, other)
            fit = fit_asymmetrical(None, kdefit_asym=(z, function_subtract))
            return MixedDist(*fit)
        else:
            return MixedDist(
                    self.mode - other,
                    self.lower_lim - other,
                    self.upper_lim - other
                    )

    def __rsub__(self, other):
        if isinstance(other, MixedDist):
            return other.__sub__(self)
        else:
            return MixedDist(
                    other - self.mode,
                    other - self.upper_lim,
                    other - self.lower_lim,
                    )

    def __truediv__(self, other):
        if isinstance(other, MixedDist):
            z, function_true_divide = data_tools.pdf_convolution('true_divide', self, other)
            fit = fit_asymmetrical(None, kdefit_asym=(z, function_true_divide))
            return MixedDist(*fit)
        else:
            return self.__mul__(1./other)

    def __rtruediv__(self, other):
        if isinstance(other, MixedDist):
            return other.__truediv__(self)
        else:
            array = other/self.use_sample()
            array = array[~np.isnan(array)]
            return MixedDist(*fit_asymmetrical(array))

    def __pow__(self, other):
        if isinstance(other, MixedDist):
            array = self.use_sample() ** other.use_sample()
            array = array[~np.isnan(array)]
            return MixedDist(*fit_asymmetrical(array))
        else:
            if other == 0:
                return 1
            elif isinstance(other, int):
                power = np.prod([self for _ in range(abs(other))])
                if other > 0:
                    return power
                else:
                    return 1/power
            else:
                array = self.use_sample() ** other
                array = array[~np.isnan(array)]
                return MixedDist(*fit_asymmetrical(array))

    def __rpow__(self, other):
        array = other ** self.use_sample()
        array = array[~np.isnan(array)]
        return MixedDist(*fit_asymmetrical(array))

    def __str__(self):
        return ": %.3e, %.3e, %.3e" % (
                self.mode, 
                self.xplus, 
                self.xminus,
                )

class Prior(object):
    pass

class FlatPrior(Prior):
    def __init__(self, vmin, vmax):
        self.vmin = vmin
        self.vmax = vmax
        self.ref = (self.vmax + self.vmin)/2
        # ref is used by initialize_chains to sample starting points
        self.interval_size = self.vmax - self.vmin
        self.log_flat_prior = log(1/self.interval_size)

    def __repr__(self):
        return '[{0}, {1}]'.format("%.3e" % self.vmin, "%.3e" % self.vmax)

    def log_prior_probability(self, parameter_space_point):
        return self.log_flat_prior \
                if self.vmin <= parameter_space_point <= self.vmax else -np.inf

    def rvs(self):
        return np.random.rand() * self.interval_size + self.vmin

class GaussianPrior(Prior):
    def __init__(self, mu, sigma):
        self.mu = mu
        self.sigma = sigma
        self.vmin = self.mu - 6 * self.sigma
        self.vmax = self.mu + 6 * self.sigma
        self.ref = self.mu
        # ref is used by initialize_chains to sample starting points
        self.interval_size = self.vmax - self.vmin

    def __repr__(self):
        return 'N({0}, {1})'.format("%.3e" % self.mu, "%.3e" % self.sigma)

    def log_prior_probability(self, parameter_space_point):
        prior = 1/self.sigma * scipy_stats_standard_normal.pdf(
                (parameter_space_point - self.mu)/self.sigma
                )
        return log(prior)

    def rvs(self):
        return np.random.randn() * self.sigma + self.mu

def estimate_sigma2(n, m, W, B_n):
    return (1-1/n) * W + (1 + 1/m) * B_n

def estimate_varV(n, m, B_n, s2, xbar, xbarbar):
    varV = (1-1/n)**2 / m * sample_variance(s2)
    varV += (1 + 1/m)**2 * 2 / (m - 1) * np.dot(B_n, B_n)
    last_term = 2 * (m+1) * (n-1) / m**2 / n # expression in the article: / m / n**2 * n/m
    last_term *= sample_covariance(s2, xbar**2) - 2 * xbarbar * sample_covariance(s2, xbar) # xbar**2 not matrix product
    varV += last_term
    return varV

def LogNormalMode(mu, sigma):
    return np.exp(mu - sigma**2)

def LogNormalPDF(x, mu, sigma):
    return 1/x/sigma/np.sqrt(2*np.pi) * np.exp(-1/2*(np.log(x)-mu)**2/sigma**2)

def LogNormalCDF(x, mu, sigma):
    return 1/2 + 1/2 * erf((np.log(x)-mu)/np.sqrt(2)/sigma)

def MVUdistribution(X, S):
    Y = [st.uniform(x-s, 2*s) for (x, s) in zip(X, S)]
    return ListDistributions(Y)

def MVNdistribution(X, S):
    '''
    Multivariate Normal Distribution
    S is the covariance matrix
    '''
    Y =  st.multivariate_normal(X, S)
    return Y

def logpriordist(params, priors):
    logpriorpdf = {}
    for par in params:
        #x = params[par]
        #mu = priors[par].ref
        #sigma = (priors[par].vmax - priors[par].vmin) / 2.
        #logpriorpdf[par] = np.log(1./sigma/np.sqrt(2*np.pi)) - (x-mu)**2/2./sigma**2 # gaussian priors
        if hasattr(priors[par], 'mu'):
            logpriorpdf[par] = np.log(1/priors[par].sigma \
                    * scipy_stats_standard_normal.pdf(
                        (params[par] - priors[par].mu)/priors[par].sigma
                        ))
        else:
            if priors[par].vmin <= params[par] <= priors[par].vmax:
                logpriorpdf[par] = np.log(math_functions.uniform(priors[par].vmin, priors[par].vmax)) # flat priors
            else:
                logpriorpdf[par] = -np.inf
    return sum([logpriorpdf[par] for par in params])

def general_average_std(values, weights=None):
    ave = np.average(values, weights=weights)
    var = np.average((values-ave)**2, weights=weights)
    return ave, np.sqrt(var)

def make_kde(samples, x=None, a_support=None, b_support=None, a_edg=None,
        b_edg=None, bandwidth=None, support_file=None, density_file=None,
        thin=None, correct_boundaries=False, normalization=None,
        kde_shuffle=False, bar=None):

    if x is None:
        supports = []
    densities = []
    thin_samples = []
    samples_norm = []
    samples_std = []

    for sample in samples:
        this_sample_thin = thin or thin_factor(sample.size)[0]
        if kde_shuffle:
            np.random.shuffle(sample)
        sample = sample[::this_sample_thin]
        thin_samples.append(sample)
        this_sample_normalization = np.ones_like(sample) if normalization is None else normalization
        samples_norm.append(this_sample_normalization)
        std = general_average_std(sample, weights=this_sample_normalization)[1]
        samples_std.append(std)
        if x is None:
            this_sample_a_support = data_tools.get_min_out(sample) if a_support is None else a_support
            this_sample_b_support = data_tools.get_max_out(sample) if b_support is None else b_support
            numpoints_factor = max(1, (this_sample_b_support-this_sample_a_support)/std) 
            support = np.linspace(this_sample_a_support, this_sample_b_support, int(round(numpoints_factor * kde_numpoints)))
            supports.append(support)

    if x is None:
        support = np.concatenate(supports)
        support.sort()
        x_or_support = support
    else:
        x_or_support = np.array(x, ndmin=1)

    for sample, norm, std in zip(thin_samples, samples_norm, samples_std):
        this_sample_bandwidth = bandwidth or std
        this_sample_bandwidth *= (4/3/sample.size)**(1/5)
        normX = st.distributions.norm(0, this_sample_bandwidth)
        density = np.zeros_like(x_or_support)
        if correct_boundaries:
            for X, n in zip(sample, norm):
                density += n/3 * (
                        normX.pdf(x_or_support-X) +\
                                normX.pdf(2*a_edg-x_or_support-X) +\
                                normX.pdf(2*b_edg-x_or_support-X)
                                )
        else:
            for X, n in zip(sample, norm):
                density += n * normX.pdf(x_or_support-X)
        # this offers a quicker but not optimal boundary correction when parameter
        # is weakly constrained (flat distribution):
        ##kernels = [kern/ integrate.simps(kern, x=support) for kern in kernels]

        densities.append(density)

    density = np.sum(densities, axis=0)
    if x is None:
        density /= integrate.simps(density, x=x_or_support) # or trapz
    else:
        density /= np.sum([sample.size for sample in thin_samples])

    if support_file:
        np.savetxt(support_file, x_or_support)
    if density_file:
        np.savetxt(density_file, density)
    if bar:
        bar.update(1)
    return x_or_support, density

def resample(sample, size):
    if sample.size < size:
        import multiprocessing
        support, density = make_kde([sample,],)
        cpu = multiprocessing.cpu_count()
        size = size - sample.size
        manager = multiprocessing.Manager()
        slices = manager.list(range(cpu))
        if size % cpu == 0:
            jobs = [multiprocessing.Process(
                target = resample_job,
                args = (support, density, size//cpu, i, slices)
                ) for i in range(cpu)]
        else:
            jobs = [multiprocessing.Process(
                target = resample_job,
                args = (support, density, size//(cpu-1), i, slices)
                ) for i in range(cpu-1)]
            if size % (cpu - 1) > 0:
                jobs.append(multiprocessing.Process(
                    target = resample_job,
                    args = (support, density, size % (cpu-1), cpu - 1, slices)
                    ))
        for j in jobs:
            j.start()
        for j in jobs:
            j.join()
        newsample = np.concatenate([sample, np.concatenate([sl for sl in slices if type(sl) is np.ndarray])])
        np.random.shuffle(newsample)
        assert newsample.size == size + sample.size
        return newsample
    else:
        return sample[:size]

def resample_job(support, density, size, i, slices):
    from scipy.optimize import bisect
    np.random.seed()
    uniform = scipy_stats_standard_normal.rvs(size)
    newsample = []
    for u in uniform:
        F = interp1d(support, [integrate.trapz(
            density[:j+1], x=support[:j+1]) - u for j in range(len(support))])
        q = bisect(F, support[0], support[-1])
        newsample.append(q)
    slices[i] = np.array(newsample)
    return np.array(newsample)

def fit_asymmetrical(sample, nbins=140, kdefit_asym=False, THIN=None):
    if kdefit_asym is False:
        count, seps, widths = data_tools.numpyhist(sample, nbins)
        sample_totallength = len(sample)
        normalization = sample_totallength * (seps[-1]-seps[0])/len(count)
        count = np.array(count) * normalization
        onesigma, count = data_tools.sigmalevels_1D(count, seps, levels=[1,])
        peaks1s = np.where(count > onesigma)[0]
        sep_peaks_1s = data_tools.listsplit(peaks1s)
        #print(len(sep_peaks_1s))
        #print(sep_peaks_1s, onesigma, peaks1s)
        #print(onesigma, count)
        cl = data_tools.Lim(sep_peaks_1s[0], count, seps)
        #plt.fill_between(x, 0, mix_dist.pdf(x), where=np.where(mix_dist.pdf(x) > onesigma/normalization, True, False), alpha=0.4)
        return cl.xmode, cl.xmin, cl.xmax
    elif kdefit_asym == 'lognormal':
        logsample = np.log(sample)
        LN = st.distributions.lognorm(logsample.std(), scale=np.exp(logsample.mean()))
        xa, xb = sample.min(), sample.max()
        amp = xb - xa
        x = np.linspace(sample.min() - amp/10, sample.max() + amp/10, 1001)
        return fit_asymmetrical(None, kdefit_asym=(x, LN.pdf(x)))
    else:
        support, kde_orig = make_kde([sample,], thin=THIN) if kdefit_asym is True else kdefit_asym
        try:
            onesigma, kde = data_tools.sigmalevels_1D(kde_orig, support, levels=[1,])
            peaks1s = np.where(kde > onesigma)[0]
            sep_peaks_1s = data_tools.listsplit(peaks1s)[0]
            clmin = support[sep_peaks_1s[0]]
            clmax = support[sep_peaks_1s[-1]]
            interval = kde[sep_peaks_1s[0]:sep_peaks_1s[-1]]
            interval = sorted(interval)[::-1]
            imode = [list(kde).index(value) for value in interval[:5]]
            clmode = np.mean([support[i] for i in imode])
            #imode = list(kde).index(kde[sep_peaks_1s[0]:sep_peaks_1s[-1]].max())
            #clmode = support[imode]
        except ValueError:
            import matplotlib
            matplotlib.use('Agg')
            import matplotlib.pyplot as plt
            fig, ax = plt.subplots()
            ax.plot(support, kde_orig, lw=0.5, color='r')
            fig.savefig('debug_fitasym.pdf')
            raise ValueError
        return clmode, clmin, clmax

def CL_excluding_value_kde(support, kde1, exclude=0.0):
    ikde = interp1d(support, kde1)
    try:
        k_exclude = ikde(exclude)
        if exclude not in support:
            newsupport = np.concatenate([support[support < exclude], [exclude,],
                support[support > exclude]])
            kde1 = np.concatenate([kde1[support < exclude], [k_exclude,],
                kde1[support > exclude]])
            support = newsupport
        percent = integrate.trapz(
                kde1[kde1 >= k_exclude], 
                x=support[kde1 >= k_exclude]
                )/ integrate.trapz(kde1, x=support)
    except ValueError:
        percent = integrate.trapz(kde1, x=support)
    return scipy_stats_standard_normal.ppf(percent/2+0.5)

def CL_excluding_value_data(sample, exclude=0.0):
    return CL_excluding_value_kde(*make_kde([sample,], thin=1), exclude=exclude)

def thin_factor(sample_size, desired_order=4):
    thin = max(0, int(round(np.log10(sample_size) - desired_order)))
    thin = max(1, 10**thin//2)
    return thin, sample_size//thin

def make_kde2d(xsamples, ysamples, xa_support=None, xb_support=None,
        ya_support=None, yb_support=None, xa_edg=None, xb_edg=None,
        ya_edg=None, yb_edg=None, bandwidth=None, xsupport_file=None,
        ysupport_file=None, density_file=None, thin=None,
        correct_boundaries=False, normalization=None, numpoints=None,
        bar=None):

    densities = []
    array_supports = {'x': [], 'y': []}
    thin_samples = {'x': [], 'y': []}
    Asupport = {}

    for xysample in zip(xsamples, ysamples):
        for xy, sample, a_support, b_support in zip(
                ('x', 'y'),
                xysample, 
                (xa_support, ya_support), 
                (xb_support, yb_support)
                ):
            this_sample_a_support = data_tools.get_min_out(sample) if a_support is None else a_support
            this_sample_b_support = data_tools.get_max_out(sample) if b_support is None else b_support
            this_sample_thin = thin or thin_factor(sample.size)[0]
            sample = sample[::this_sample_thin]
            thin_samples[xy].append(sample)
            u = np.linspace(this_sample_a_support, this_sample_b_support, kde2d_numpoints)
            array_supports[xy].append(u)

    for xy in ('x', 'y'):
        # must be uniformly spaced
        Asupport[xy] = np.linspace(np.min(array_supports[xy]), np.max(array_supports[xy]), num=np.size(array_supports[xy]))
        #Asupport[xy] = np.concatenate(array_supports[xy])
        #Asupport[xy].sort()

    support = np.array([[(X, Y) for Y in Asupport['y']] for X in Asupport['x']])
    shapex, shapey, support_reshaped = reshape_3d_2d(support)

    for xysample in zip(thin_samples['x'], thin_samples['y']):
        this_sample_normalization = np.ones_like(xysample[0]) \
                if normalization is None else normalization
        assert xysample[0].size == xysample[1].size
        bw_factor = (1/xysample[0].size)**(1/3)
        these_samples_bandwidth = np.cov(*xysample) if bandwidth is None else bandwidth
        these_samples_bandwidth *= bw_factor

        try:
            mvn = st.multivariate_normal([0, 0], these_samples_bandwidth)
        except (np.linalg.LinAlgError, ValueError):
            mvn = Bivariate_Normal([0, 0], these_samples_bandwidth)

        if correct_boundaries:
            density = reflected_bivariate_normal(support_reshaped, xa_edg,
                    xb_edg, ya_edg, yb_edg, mvn, xysample[0], xysample[1],
                    shapex, shapey, this_sample_normalization)
        else:
            density = np.zeros((shapex, shapey))
            for s in zip(xysample[0], xysample[1], this_sample_normalization):
                density += np.reshape(
                        s[2] * mvn.pdf(support_reshaped - s[:2]),
                        (shapex, shapey)
                        )

        densities.append(density)

    density = np.sum(densities, axis=0)
    density /= integrate.simps(integrate.simps(density, x=Asupport['y']), x=Asupport['x'])
    if xsupport_file:
        np.savetxt(xsupport_file, Asupport['x'])
    if ysupport_file:
        np.savetxt(ysupport_file, Asupport['y'])
    if density_file:
        np.savetxt(density_file, density)
    if bar:
        bar.update(1)
    return Asupport['x'], Asupport['y'], density

def reshape_3d_2d(support):
    shapex, shapey, shapez = support.shape
    assert shapez == 2
    return shapex, shapey, support.reshape(shapex*shapey, shapez)

def reflected_bivariate_normal(support, xa, xb, ya, yb, mvn, xsample, ysample,
        shapex, shapey, normalization):
    xa_reflection = np.array([[2*xa - sup[0], sup[1]] for sup in support])
    xb_reflection = np.array([[2*xb - sup[0], sup[1]] for sup in support])
    ya_reflection = np.array([[sup[0], 2*ya - sup[1]] for sup in support])
    yb_reflection = np.array([[sup[0], 2*yb - sup[1]] for sup in support])
    density = np.zeros((shapex, shapey))
    for s in zip(xsample, ysample, normalization):
        density += np.reshape(s[2]/5 * (
            mvn.pdf(support-s[:2]) + mvn.pdf(xa_reflection-s[:2]) +\
                    mvn.pdf(xb_reflection-s[:2]) + mvn.pdf(ya_reflection-s[:2]) +\
                    mvn.pdf(yb_reflection-s[:2])
                    ), (shapex, shapey)
                    )
    return density

def correlation(X, Y, j):
    Xbar, Ybar = X.mean(), Y.mean()
    SX, SY = X.size, Y.size
    assert SX == SY
    rho = np.sum( (X[:SX-j]-Xbar) * (Y[j:]-Ybar) )
    rho /= np.sqrt( np.sum( (X[:SX-j]-Xbar)**2 ) )
    rho /= np.sqrt( np.sum( (Y[j:]-Ybar)**2 ) )
    return rho

def auto_correlation(X, j):
    return correlation(X, X, j)

#def auto_correlation(X, j):
#    Xbar = X.mean()
#    S = X.size
#    rho = np.sum( (X[:S-j]-Xbar) * (X[j:]-Xbar) )
#    rho /= np.sqrt( np.sum( (X[:S-j]-Xbar)**2 ) )
#    rho /= np.sqrt( np.sum( (X[j:]-Xbar)**2 ) )
#    return rho

def double_Gaussian(x, mu1, sig1, mu2, sig2, A):
    pdf = A/sig1 * np.exp(-1/2 * ((x-mu1)/sig1)**2) +\
            (1-A)/sig2 * np.exp(-1/2 * ((x-mu2)/sig2)**2)
    return pdf/np.sqrt(2*np.pi)

def sample_variance(x):
    return sample_covariance(x, x)

def sample_covariance(x, y):
    assert x.size == y.size
    X = x - x.mean()
    Y = y - y.mean()
    cov = (np.sum(X*Y) - X.sum() * Y.sum() / X.size) / X.size
    return cov

def Sigma_from_S(S, n):
    return np.array(S) * n/5.6644

