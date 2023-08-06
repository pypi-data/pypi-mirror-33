import configparser
from EPIC.utils.numbers import log2pi_over_2, speedoflight
from EPIC.utils.io_tools import readfile
from EPIC.utils.statistics import make_kde
from EPIC.utils.math_functions import corr_to_cov
import EPIC.cosmology.cosmic_objects as cosmo
from EPIC import root
import os 
import numpy as np
from collections import OrderedDict

try:
    import cPickle as pickle
except ImportError:
    import pickle

class Dataset(object):
    def function_of_predict(self, predict):
        return predict

class DataPoints(Dataset):
    def __init__(self, observable, dataset_loc, predicting_function_name):
        self.location = os.path.join(root, 'cosmology', 'observational_data',
                observable, dataset_loc)
        self.points, self.obs, self.errors = np.loadtxt(self.location, ndmin=2,
                unpack=True)
        self.predicting = predicting_function_name

    def log_likelihood(self, predict, **kwargs):
        predicted = self.function_of_predict(predict(self.points, **kwargs))
        #print(self.obs, predicted) ## for debugging
        chi2 = (self.obs - predicted)**2 / self.errors**2
        loglike = - log2pi_over_2 - np.log(self.errors) - chi2/2
        return chi2.sum(), loglike.sum()

class Generic_Covariant_Gaussian_Dataset(Dataset):
    def __init__(self, observable, dataset_loc, predicting_function_name,
            attributes=['points', 'obs', 'sigmas']):
        self.location = os.path.join(root, 'cosmology', 'observational_data', observable,
                dataset_loc)
        data = np.loadtxt(os.path.join(self.location, 'data.txt'), ndmin=2, unpack=True)
        self.predicting = predicting_function_name

        for attribute, array in zip(attributes, data):
            setattr(self, attribute, array)
        
        try: 
            with open(os.path.join(self.location, 'fiducial.p'), 'rb') as fhandle:
                self.fiducial = pickle.load(fhandle)
        except IOError:
            pass

        try:
            self.inverse_covariance_matrix = np.loadtxt(os.path.join(self.location, 'invcov.txt'))
        except IOError:
            try:
                cov = np.loadtxt(os.path.join(self.location, 'cov.txt'))
            except IOError:
                corr = np.loadtxt(os.path.join(self.location, 'corr.txt'))
                cov = corr_to_cov(self.sigmas, corr)
            self.inverse_covariance_matrix = np.linalg.inv(cov)

        self.log_det_inverse_covariance_matrix = np.linalg.slogdet(
                self.inverse_covariance_matrix)[1]

    def log_likelihood(self, predict, **kwargs):
        return generic_likelihood_Covariant_Gaussian(self, predict, **kwargs)

class BAO_isotropic_DataPoints(DataPoints):
    def __init__(self, observable, dataset_loc, predicting_function_name):
        self.location = os.path.join(root, 'cosmology', 'observational_data',
                observable, dataset_loc)
        self.points, self.obs, self.errors = np.loadtxt(
                os.path.join(self.location, 'data.txt'), ndmin=2, unpack=True)
        with open(os.path.join(self.location, 'fiducial.p'), 'rb') as fhandle:
            self.fiducial = pickle.load(fhandle)
        self.predicting = predicting_function_name

    def function_of_predict(self, ratio):
        # turns rs_zd/D_V into D_V/r_s * r_fid
        # fiducial rs_zd is in Mpc
        rs_zd_fiducial = self.fiducial.get('rs_zd_EH98',
                self.fiducial.get('rs_zd', self.fiducial.get('rs_zd_CAMB')))
        return rs_zd_fiducial / ratio

class BAO_WiggleZ_DataPoints(Generic_Covariant_Gaussian_Dataset):
    def function_of_predict(self, ratio):
        # turns rs_zd/D_V into D_V/r_s * r_fid
        # fiducial rs_zd is in Mpc
        rs_zd_fiducial = self.fiducial.get('rs_zd_EH98',
                self.fiducial.get('rs_zd', self.fiducial.get('rs_zd_CAMB')))
        return rs_zd_fiducial / ratio

class BAO_alpha_DataPoints(BAO_isotropic_DataPoints):
    def function_of_predict(self, ratio):
        # returns alpha
        # fiducial rs_zd is in Mpc
        rs_zd_fiducial = self.fiducial.get('rs_zd_EH98',
                self.fiducial.get('rs_zd', self.fiducial.get('rs_zd_CAMB')))
        fiducial_ratio = rs_zd_fiducial / self.fiducial['DV']
        return fiducial_ratio / ratio

class Generic_Covariant_Gaussian_one_point(Generic_Covariant_Gaussian_Dataset):
    def __init__(self, observable, dataset_loc, predicting_function_name):
        super().__init__(observable, dataset_loc, predicting_function_name,
                attributes=['obs', 'sigmas'])

        with open(os.path.join(self.location, 'data.txt'), 'r') as fhandle:
            z = fhandle.readline()
        
        try:
            self.points = float(z.split()[-1].strip())
        except ValueError:
            # possibly will not need it
            self.points = None

class BAO_aniso_Dataset(Generic_Covariant_Gaussian_one_point):
    def function_of_predict(self, scales):
        DA_over_rd, rd_times_H = scales
        rs_zd_fiducial = self.fiducial.get('rs_zd_EH98',
                self.fiducial.get('rs_zd', self.fiducial.get('rs_zd_CAMB')))
        return DA_over_rd * rs_zd_fiducial, rd_times_H / rs_zd_fiducial

    def log_likelihood(self, predict, **kwargs):
        return generic_likelihood_Covariant_Gaussian_aniso(self, predict, **kwargs)

class BAO_QuasarLyman_Dataset(BAO_aniso_Dataset):
    def function_of_predict(self, scales):
        DA_over_rd, rd_times_H = scales
        return DA_over_rd, speedoflight/1e3/rd_times_H

class BAO_Lyalpha_Forests_Dataset(BAO_aniso_Dataset):
    def function_of_predict(self, scales):
        DA_over_rd, rd_times_H = scales
        return (1 + self.points) * DA_over_rd, speedoflight/1e3/rd_times_H

class BAO_SDSS_Consensus_Dataset(Generic_Covariant_Gaussian_Dataset):
    def __init__(self, observable, dataset_loc, predicting_function_name):
        super().__init__(observable, dataset_loc, predicting_function_name,
                attributes=['points', 'D_M', 'H'])
        self.obs = np.ravel(list(zip(self.D_M, self.H)))

    def function_of_predict(self, scales):
        DA_over_rd, rd_times_H = scales
        rs_zd_fiducial = self.fiducial['rs_zd']
        DM = (1+self.points) * DA_over_rd * rs_zd_fiducial
        H = rd_times_H / rs_zd_fiducial
        return np.ravel(list(zip(DM, H)))

    def log_likelihood(self, predict, **kwargs):
        return generic_likelihood_Covariant_Gaussian_aniso(self, predict, **kwargs)

class NonVirializedClusters(Dataset):
    def __init__(self, observable, dataset_file, predicting_function_name):
        #print('    Reading clusters virial ratio data...')
        #print('        %s' % dataset_file)

        self.location = os.path.join(root, 'cosmology', 'observational_data',
                observable)
        self.clusters = []

        with open(os.path.join(self.location, dataset_file), 'r') as datafile:
            line = datafile.readline()
            while line.startswith('#'):
                line = datafile.readline()
            while line:
                self.clusters.append(
                        cosmo.Cluster(*line.strip().split())
                        )
                line = datafile.readline()

        with open(os.path.join(self.location, dataset_file.replace('.txt',
            '.ovr')), 'w') as ovr_file:
            ovr_file.write('# Cluster\tovr\tfc\tdFdc\n')
            for cl in self.clusters:
                ovr_file.write('\t'.join([cl.name, str(cl.ovr), str(cl.fc),
                    str(cl.dFdc)]) + '\n')

        #print('        Clusters ' + ', '.join(
        #    [CL.name for CL in self.clusters]) + '.')
        self.obs = self.clusters
        self.predicting = predicting_function_name
        self.nuisance_parameters = OrderedDict([
                ('gamma', cosmo.NuisanceParameter('gamma', tex=r'\gamma')),
                ('logt0', cosmo.NuisanceParameter('logt0', tex=r'\log_{10}t_0'))
                ])

    def log_likelihood(self, predict, **kwargs):
        ovr = [cl.ovr for cl in self.clusters]
        model = kwargs['model']
        xi = model.species['idm'].interaction_parameter.get_value(**kwargs)
        xi *= model.species['idm'].interaction_sign
        dlnrhoH = [model.clusters_dlnrho_over_H(cl, self.nuisance_parameters,
            **kwargs) for cl in self.clusters]
        DfE = [(- 1/(2+3*xi)) * num for num in dlnrhoH]
        obs_tvr = [OVR-DFE for OVR, DFE in zip(ovr, DfE)]
        predict_tvr = predict(**kwargs) 

        chi2 = np.array([(num.nominal_value - predict_tvr)**2/num.std_dev**2 for num in obs_tvr])
        ll = - log2pi_over_2 - np.log([num.std_dev for num in obs_tvr]) - chi2/2

        return chi2.sum(), ll.sum()

class JLA_SimplifiedDataset(Dataset):
    def __init__(self, observable, dataset_loc, predicting_function_name):
        self.location = os.path.join(root, 'cosmology', 'observational_data',
                observable)
        self.points, self.obs = np.loadtxt(os.path.join(self.location,
            dataset_loc, 'data', 'jla_mub.txt'), ndmin=2, unpack=True)
        self.covariance_matrix = np.loadtxt(os.path.join(self.location,
            dataset_loc, 'data', 'jla_mub_covmatrix.dat'),
            skiprows=1).reshape([ self.points.size, self.points.size])
        self.inverse_covariance_matrix = np.linalg.inv(self.covariance_matrix)
        self.log_det_inverse_covariance_matrix = np.linalg.slogdet(
                self.inverse_covariance_matrix)[1]
        self.predicting = predicting_function_name 
        self.nuisance_parameters = OrderedDict([('M', cosmo.NuisanceParameter('M')),])

    def log_likelihood(self, predict, **kwargs):
        return generic_likelihood_Covariant_Gaussian_with_nuisance(self,
                predict, **kwargs)

class full_JLA_likelihood(Dataset):
    def __init__(self, observable, dataset_loc, predicting_function_name):
        from astropy.io import fits
        from glob import glob
        self.location = os.path.join(root, 'cosmology', 'observational_data',
                observable, dataset_loc)
        z_cmb, z_hel, muB, x1, color, self.log10MB = np.loadtxt(
                os.path.join(self.location, 'data', 'jla_lcparams.txt'),
                unpack=True, usecols=(1,2,4,6,8,10))
        self.points = list(zip(z_hel, z_cmb))
        scoh, slens, sz = np.loadtxt(os.path.join(self.location, 'covmat',
            'sigma_mu.txt'), unpack=True)
        eta = np.zeros(3 * muB.size)
        distance_estimate = muB, x1, color
        for k, de in enumerate(distance_estimate):
            eta[k::3] = de
        self.eta = np.array(eta, ndmin=2)
        self.C_eta = np.sum([fits.getdata(mat) for mat in glob(
            os.path.join(self.location, 'covmat', 'C*.fits'))], axis=0)
        
        A012 = [np.zeros((muB.size, 3*muB.size)) for k in range(3)]
        for i in range(muB.size):
            for k in range(3):
                A012[k][i, 3*i+k] = 1
        self.A0, self.A1, self.A2 = A012

        sigz = 5 * 150 * 1e3/speedoflight/sz/np.log(10)
        self.sum_sig2 = np.diag(sigz**2 + slens**2 + scoh**2)
        self.nuisance_parameters = OrderedDict([
            ('alpha', cosmo.NuisanceParameter('alpha', tex=r'\alpha')),
            ('beta', cosmo.NuisanceParameter('beta', tex=r'\beta')),
            ('M_B', cosmo.NuisanceParameter('M_B')),
            ('DeltaM', cosmo.NuisanceParameter('DeltaM', tex=r'{\Delta}M')),
            ])
        self.predicting = predicting_function_name + '_full'

    def get_mu_cov(self, **kwargs):
        alpha = self.nuisance_parameters['alpha'].get_value(**kwargs)
        beta = self.nuisance_parameters['beta'].get_value(**kwargs)
        A = self.A0 + alpha * self.A1 - beta * self.A2
        C = np.dot(np.dot(A, self.C_eta), A.transpose())
        return A.transpose(), C + self.sum_sig2

    def Matrix_MB(self, **kwargs):
        M_B = self.nuisance_parameters['M_B'].get_value(**kwargs)
        DeltaM = self.nuisance_parameters['DeltaM'].get_value(**kwargs)
        return np.array([M_B + DeltaM * (logM>10) for logM in self.log10MB], ndmin=2)

    def log_likelihood(self, predict, **kwargs):
        alpha = self.nuisance_parameters['alpha'].get_value(**kwargs)
        beta = self.nuisance_parameters['beta'].get_value(**kwargs)

        A, cov = self.get_mu_cov(**kwargs)
        self.obs = np.dot(self.eta, A) - self.Matrix_MB(**kwargs)
        self.inverse_covariance_matrix = np.linalg.inv(cov)
        self.log_det_inverse_covariance_matrix = np.linalg.slogdet(
                self.inverse_covariance_matrix)[1]
        return generic_likelihood_Covariant_Gaussian(self, predict, **kwargs)

def generic_likelihood_Covariant_Gaussian(dataset, predict, **kwargs):
    predicted = dataset.function_of_predict(predict(dataset.points, **kwargs))
    return chisquare(dataset, predicted)

def generic_likelihood_Covariant_Gaussian_with_nuisance(dataset, predict, **kwargs):
    predicted = dataset.function_of_predict(predict(dataset.points,
        dataset.nuisance_parameters, **kwargs))
    return chisquare(dataset, predicted)

def chisquare(dataset, predicted):
    #print(dataset.obs, predicted) ## for debugging
    X = np.array(dataset.obs - predicted, ndmin=2)
    chi2 = np.dot(np.dot(X, dataset.inverse_covariance_matrix), X.transpose())
    chi2 = float(chi2)
    return chi2, - dataset.obs.size * log2pi_over_2 \
            + dataset.log_det_inverse_covariance_matrix/2 - chi2/2

def generic_likelihood_Covariant_Gaussian_aniso(*args, **kwargs):
    kwargs.pop('isotropic', None)
    return generic_likelihood_Covariant_Gaussian(*args, isotropic=False, **kwargs)

def check_conflicting_datasets(datasets):
    for path in [
            os.path.join(root, 'cosmology', 'observational_data',
                'conflicting_dataset_pairs.txt'),
            os.path.join(root, 'modifications', 'cosmology',
                'observational_data', 'conflicting_dataset_pairs.txt'),
            ]:
        with open(path, 'r') as fhandle:
            line = fhandle.readline()
            while line:
                if line.startswith('#'):
                    pass
                else:
                    a, b = line.split(',')
                    if a.strip() in datasets and b.strip() in datasets:
                        return True
                line = fhandle.readline()

def choose_from_datasets(dataset_dictionary):
    available = configparser.ConfigParser()
    available.read([
        os.path.join(root, 'cosmology', 'observational_data',
            'available_observables.ini'),
        os.path.join(root, 'modifications', 'cosmology', 'observational_data',
            'available_observables.ini'),
        ])
    datasets = {}
    for key in dataset_dictionary:
        names = dataset_dictionary[key]
        if isinstance(names, str):
            names = [names,]
        assert isinstance(names, list)
        for name in names:
            datasets[name] = eval(available['DatasetType'][name])(
                    key, available[key][name] or name,
                    available[key]['predicting_function_name'])
    if check_conflicting_datasets(datasets):
        from EPIC import DataError
        raise DataError('Two or more datasets are conflicting. Check' \
                ' conflicting_dataset_pairs.txt in' \
                ' EPIC/cosmology/observational_data/')
    return datasets


