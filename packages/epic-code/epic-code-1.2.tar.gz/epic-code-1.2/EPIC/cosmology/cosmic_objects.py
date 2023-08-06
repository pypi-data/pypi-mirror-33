import numpy as np
import scipy.integrate as integrate
from scipy.interpolate import interp1d
from EPIC import Unsupported, NotAnalytic
from EPIC.cosmology import a_of_z, z_of_a, rho_critical, rho_critical_SI
from EPIC.utils.numbers import speedoflight, a_B_over_c2, GmumH, Mpc_to_km, G_SI, G
from EPIC.utils.io_tools import pasta
from EPIC import root
import uncertainties
from uncertainties import umath
from collections import OrderedDict
import os
import configparser

'''
The universe/cosmology, fluids, interacting fluids and equation of states are
here defined as class objects
'''

class CosmologicalSetup(object):
    def __init__(self, model, optional_species=[], combined_species=[],
            interaction_setup={}, physical=True, derived=None, a0=1):
        ''' keys for interaction_setup:
        species (-> list), propto_other (-> dict), parameter (-> dict), 
        tex (-> str), sign (-> dict)
        '''

        self.model = model
        self.a0 = a0
        self.physical_density_parameters = physical

        available_species = configparser.ConfigParser()
        available_species.read([
            os.path.join(root, 'cosmology', 'available_species.ini'),
            os.path.join(root, 'modifications', 'cosmology',
                'available_species.ini'),
            ])
        # this defines the list of fluids that will be present (strings), but
        # do not create the objects yet
        species_labels = self.get_species(
                available_species,
                optional_species=optional_species,
                combined_species=combined_species
                )
        
        for fluid in species_labels:
            eos_type = available_species['EoS type'][fluid]
            eos_value = eval(available_species['EoS value'].get(fluid, 'None'))
            eos_woa = fluid if eos_type == 'woa' \
                    and available_species['EoS woa parametrization'].getboolean(fluid) \
                    else None
            eos_parameters = eval(available_species['EoS parameters'].get(fluid, '[]'))
            eos_par_tex = eval(available_species['tex EoS parameters'].get(fluid, '[]'))
            eos_parameters_obj = [FreeParameter(par, tex=tex, model_name=self.model) \
                    for par, tex in zip(eos_parameters, eos_par_tex)]
            eos = EquationOfState(eos_type, value=eos_value,
                    parameters=eos_parameters_obj, woa=eos_woa)

            physical_densities = 'physical ' if self.physical_density_parameters else ''
            if derived == fluid:
                density_parameter = DerivedParameter(
                        available_species['%sdensity parameter' \
                                % physical_densities][fluid],
                        list(set(species_labels) - set([fluid,])),
                        tex=available_species['tex %sdensity parameter' \
                                % physical_densities][fluid],
                        physical=bool(self.physical_density_parameters)
                        )
            else:
                if fluid == 'radiation':
                    temperature_parameter = FreeParameter(
                            available_species['%sdensity parameter' \
                                    % physical_densities][fluid],
                            available_species['tex %sdensity parameter' \
                                    % physical_densities][fluid],
                            model_name=self.model
                            )
                    density_parameter = DensityFromTemperature(
                            temperature_parameter, 
                            physical=bool(self.physical_density_parameters),
                            model_name=self.model)
                else:
                    density_parameter = DensityParameter(
                            available_species['%sdensity parameter' \
                                    % physical_densities][fluid],
                            available_species['tex %sdensity parameter' \
                                    % physical_densities][fluid],
                            physical=bool(self.physical_density_parameters), model_name=self.model
                            )

            if fluid in interaction_setup.get('species', []):
                int_parameter = interaction_setup.get('parameter', {}).get(fluid)
                int_other = interaction_setup.get('propto_other', {}).get(fluid)

                this_fluid = InteractingFluid(
                        fluid, eos, density_parameter,
                        interaction_setup={
                            'parameter': int_parameter,
                            'tex_parameter': interaction_setup.get('tex') \
                                    if int_parameter else None,
                            'sign': interaction_setup.get('sign', {})[fluid],
                            'propto_other': int_other
                            }, model_name=self.model
                        )
            else:
                this_fluid = NonInteractingFluid(fluid, eos, density_parameter)
            self.add_species(fluid, this_fluid)

        for key in self.species.keys():
            if getattr(self.species[key], 'interaction_propto_other', None) is not None:
                self.species[key].interacts_with = \
                        self.species[self.species[key].interaction_propto_other]

        self.directly_solvable = self.is_directly_solvable()

        for par in self.parameters:
            if isinstance(par, DerivedParameter):
                par.dependencies = [free for free in self.parameters\
                        if isinstance(free, DensityParameter)]

        # defines Hubble parameter
        if self.physical_density_parameters:
            if derived is None:
                Hubble_parameter = HubbleDerivedParameter('h', 'Hubble',
                        [par for par in self.parameters if isinstance(par, DensityParameter)],
                        physical=self.physical_density_parameters
                        )
            else:
                Hubble_parameter = HubbleFreeParameter('h', model_name=self.model)
        else:
            Hubble_parameter = HubbleFreeParameter('H0', tex='H_0', model_name=self.model)
        self.parameters.append(Hubble_parameter)
        self.HubbleParameter = Hubble_parameter

        for fluid in self.species.values():
            if (isinstance(fluid.density_parameter, DerivedParameter) and \
                    not isinstance(fluid.density_parameter, (
                        HubbleDerivedParameter, DerivedDensityDistribution,
                        DerivedParameterDensityDistribution,
                        DerivedDensityFromTemperature
                        ))) or (not self.physical_density_parameters \
                                and isinstance(fluid.density_parameter,
                                    DensityFromTemperature)):
                fluid.density_parameter.hubble = self.HubbleParameter

    def is_directly_solvable(self):
        return np.all([self.species[key].is_directly_solvable() \
                for key in self.species.keys()])

    def show_defaults(self):
        return [par.default for par in self.parameters \
                if not isinstance(par, DerivedParameter)]

    def add_species(self, name, fluid):
        if not hasattr(self, 'species'):
            self.species = OrderedDict()
        if not hasattr(self, 'parameters'):
            self.parameters = []
        self.species[name] = fluid
        self.parameters.append(fluid.density_parameter)
        self.parameters.extend(fluid.EoS.parameters)
        #print(fluid.interaction_parameter)
        #print(getattr(fluid, 'interaction_parameter', 2))
        int_parameter = getattr(fluid, 'interaction_parameter', None)
        if int_parameter:
            self.parameters.append(int_parameter)

    def get_species(self, available_species, optional_species=[], combined_species=[]):
        model_recipes = configparser.ConfigParser()
        model_recipes.read([
            os.path.join(root, 'cosmology', 'model_recipes.ini'),
            os.path.join(root, 'modifications', 'cosmology',
                'model_recipes.ini'),
            ])
        self.tex = model_recipes[self.model].get('tex', self.model)
        # starts the list of species with the mandatory ones
        # example, lcdm requires lambda and cdm
        species = eval(model_recipes[self.model]['mandatory species'])

        # possibly extend with supported optional fluids
        # example, lcdm can add baryons and photons
        species.extend([fluid for fluid in optional_species \
                if fluid in eval(model_recipes[self.model].get('supported optional species', '[]'))])

        # check if user wants any of the combined species, like matter
        supported_composed_species = eval(model_recipes[self.model].get('supported composed species', '[]'))
        for fluid in combined_species:
            if fluid in supported_composed_species: # confirms support
                for component in eval(available_species['composed of'][fluid]):
                    try:
                        species.remove(component)
                    except ValueError:
                        # component fluid already not present, just pass
                        pass
                species.append(fluid)
        return species

    def get_age_of_the_universe(self, z, a_zinf=0, **kwargs):
        zinf = np.inf if a_zinf == 0 else z_of_a(a_zinf, a0=self.a0)
        t_of_z = integrate.quad(
                lambda Z: 1/self.get_Hubble_Friedmann_of_z(Z, **kwargs)/(1+Z), 
                z, zinf)[0] # in km^-1 s Mpc
        #except NotAnalytic:
        #    hubble = self.HubbleParameter.get_value(**kwargs) 
        #    H = np.sqrt(self.background_solution_rhos['total']) * \
        #            (100 if self.physical_density_parameters else hubble)
        #    a = self.a_range
        #    t_of_z = integrate.simps(1 / H[a>=a_zinf] / a[a>=a_zinf], 
        #            x=a[a>=a_zinf])
        t_of_z *= 976.480247152 # in Gyr
        return t_of_z

    def get_age_of_various_z(self, Z, **kwargs):
        return np.array([self.get_age_of_the_universe(z, **kwargs) for z in Z])

    def get_lookback_time(self, z, **kwargs):
        try:
            return self.get_age_of_the_universe(0, a_zinf=a_of_z(z), **kwargs)
        except ValueError:
            return np.array([self.get_age_of_the_universe(0, a_zinf=A, 
                **kwargs) for A in a_of_z(z)])

    def get_Hubble_Friedmann_of_z(self, z, **kwargs):
        a = a_of_z(z, a0=self.a0)
        return self.get_Hubble_Friedmann(a, **kwargs)

    def get_Hubble_Friedmann(self, a, given_densities=None, **kwargs):
        try:
            adim_Hubble = 0

            if given_densities is not None:
                adim_Hubble += sum(given_densities)
            else:
                for fluid in self.species.values():
                    rho0 = fluid.density_parameter.get_value(**kwargs)
                    adim_Hubble += fluid.rho_over_rho0(a, a0=self.a0, **kwargs) * rho0
            # curvature not implemented yet
            adim_Hubble = np.sqrt(adim_Hubble)
            # Note: result is E*h if density parameters are Omega h^2, or E if Omega
            # so we multiply h if physical to give H in km/s/Mpc
            return 100 * adim_Hubble if self.physical_density_parameters \
                    else adim_Hubble * self.HubbleParameter.get_value(**kwargs)
        except NotAnalytic:
            if not hasattr(self, 'background_solution_rhos'):
                self.solve_background(**kwargs)
            hubble = self.HubbleParameter.get_value(**kwargs)
            H = np.sqrt(self.background_solution_rhos['total']) * \
                    (100 if self.physical_density_parameters else hubble)
            H_of_a = interp1d(self.a_range, H)
            return float(H_of_a(a)) if isinstance(a, float) else H_of_a(a)

    def get_luminosity_distance(self, zhel, zcmb, **kwargs):
        luminosity_distance = (1+zhel)/self.a0 \
                * integrate.quad(lambda Z: 1/self.get_Hubble_Friedmann_of_z(
                    Z, **kwargs), 0, zcmb)[0]
                # this is the distance in Mpc/(km/s)
        luminosity_distance *= 1e6 # in pc/(km/s)
        luminosity_distance *= speedoflight/1e3 # in pc
        return luminosity_distance

    def get_distance_moduli(self, z, nuisance_magnitude, **kwargs):
        mu = 5 * np.log10( np.array([self.get_luminosity_distance(Z, Z, **kwargs)
            for Z in z], ndmin=2)/10)
        M = nuisance_magnitude['M'].get_value(**kwargs)
        return M + mu

    def get_distance_moduli_full(self, z, **kwargs):
        return 5 * np.log10( np.array([self.get_luminosity_distance(zhel, zcmb,
            **kwargs) for zhel, zcmb in z], ndmin=2)/10)

    def d_a(self, z, **kwargs): 
        # Comoving angular distance. in units of Mpc
        c = speedoflight/1e3
        try:
            da_c = c/self.a0 * integrate.quad(
                    lambda Z: 1/self.get_Hubble_Friedmann_of_z(Z, **kwargs),
                    0, z)[0]
        except ValueError:
            da_c = c/self.a0 * np.array([integrate.quad(
                    lambda Z: 1/self.get_Hubble_Friedmann_of_z(Z, **kwargs),
                    0, redshift)[0] for redshift in z])
        return da_c 

    def D_A(self, z, **kwargs):
        # physical angular distance in Mpc (flat)
        return self.d_a(z, **kwargs)*self.a0/(1 + z)

    def D_V(self, z, **kwargs): 
        # Volume averaged distance.
        # in units of Mpc
        DV = self.d_a(z, **kwargs)**2 * z * self.D_H(z, **kwargs)
        DV = DV**(1/3)
        return DV

    def D_H(self, z, **kwargs):
        return speedoflight/1e3/self.get_Hubble_Friedmann_of_z(z, **kwargs)

    def r_s(self, z, a_zinf=0, **kwargs): 
        # sound horizon size
        # in units of Mpc 
        # these are physical or not, but we only use their ratio, so does not matter
        baryons = self.species['baryons'].density_parameter.get_value(**kwargs)
        photons = self.species['radiation'].density_parameter.get_value(
                sub_species='photons', **kwargs)
        zinf = np.inf if a_zinf == 0 else z_of_a(a_zinf, a0=self.a0)
        c = speedoflight/1e3
        R_S = c * integrate.quad(
            lambda Z: 1/self.get_Hubble_Friedmann_of_z(
                Z, **kwargs) / np.sqrt( 3 * (1 + 3*baryons*self.a0/(4*photons*(1+Z))) ),
            z, zinf)[0]  
        return R_S

    def get_BAO_ratio(self, z, isotropic=True, **kwargs):
        if self.physical_density_parameters:
            Obh2 = self.species['baryons'].density_parameter.get_value(**kwargs)
            Och2 = self.species['cdm'].density_parameter.get_value(**kwargs)
        else:
            h = self.HubbleParameter.get_value(**kwargs) / 100
            h2 = h*h
            Obh2 = self.species['baryons'].density_parameter.get_value(**kwargs)*h2
            Och2 = self.species['cdm'].density_parameter.get_value(**kwargs)*h2

        Omh2 = Obh2 + Och2
        b1 = 0.313 * Omh2**-0.419 * (1 + 0.607 * Omh2**0.674)
        b2 = 0.238 * Omh2**0.223
        zd = 1291 * Omh2**0.251 * (1 + b1 * Obh2**b2) \
                / (1 + 0.659 * Omh2**0.828)
        rs_zd = self.r_s(zd, **kwargs)
        if isotropic:
            return rs_zd / self.D_V(z, **kwargs)
        return self.D_A(z, **kwargs)/rs_zd, rs_zd \
                * self.get_Hubble_Friedmann_of_z(z, **kwargs)

    def get_equilibrium_virial_ratio(self, **kwargs):
        # only applicable to cde model propto dm
        assert self.model in ['cde LI', 'wcde LI']
        xi = self.species['idm'].interaction_parameter.get_value(**kwargs)
        xi *= self.species['idm'].interaction_sign 
        # equation below has been derived for Q_c = 3 H xi_c rho_c
        return - (1 - 6*xi)/(2 + 3*xi)

    def get_a_range(self, **kwargs):
        log_a0 = np.log10(self.a0)
        log_a_initial = kwargs.get('log_a_initial', -5)
        numpoints = kwargs.get('numpoints', 10000)
        assert log_a_initial < log_a0
        self.a_range = np.logspace(log_a_initial, log_a0, numpoints)

    def solve_background(self, **kwargs):
        if not hasattr(self, 'a_range'):
            self.get_a_range(**kwargs)
        
        self.background_solution_Omegas = OrderedDict()
        self.background_solution_rhos = OrderedDict()

        if self.directly_solvable:
            for key in self.species.keys():
                fluid = self.species[key]
                rho0 = fluid.density_parameter.get_value(**kwargs)
                self.background_solution_rhos[fluid.name] = \
                        fluid.rho_over_rho0(self.a_range,
                                a0=self.a0, **kwargs) * rho0
        else:
            from EPIC.utils import integrators
            #Solve numerically
            numpoints = kwargs.get('numpoints', 10000)
            for key in self.species.keys():
                self.background_solution_rhos[key] = np.zeros(numpoints)
                self.background_solution_rhos[key][-1] = \
                        self.species[key].density_parameter.get_value(**kwargs)
            i = -2
            while i >= -numpoints:
                da = -(self.a_range[i+1] - self.a_range[i])
                densities = np.array(
                        [self.background_solution_rhos[key][i+1] \
                                for key in self.species.keys()])
                next_RK = integrators.generic_runge_kutta(
                        da, self.a_range[i+1], densities,
                        [fluid.drho_da for fluid in self.species.values()],
                        intermediate=[self.get_Hubble_Friedmann,], a0=self.a0,
                        **kwargs)
                for e, key in enumerate(self.background_solution_rhos.keys()):
                    self.background_solution_rhos[key][i] = next_RK[e]
                i -= 1

        self.background_solution_rhos['total'] = sum(self.background_solution_rhos.values())
        for key in self.background_solution_rhos.keys():
            if key != 'total': 
                self.background_solution_Omegas[key] = self.background_solution_rhos[key] \
                        / self.background_solution_rhos['total']  

    def clusters_dlnrho_over_H(self, cluster, nuisance, **kwargs):
        Hz = self.get_Hubble_Friedmann_of_z(cluster.z, **kwargs)
        # physical
        dlnpot_dlnr200 = 2 - cluster.dFdc/cluster.fc * cluster.c
        res = 3 * cluster.ovr + dlnpot_dlnr200

        logt0 = nuisance['logt0'].get_value(**kwargs)
        t0  = 10**logt0
        g = nuisance['gamma'].get_value(**kwargs)
        res *= (g*g*3**(g+1))**(1/(1-g)) / t0
        return res / Hz

    def get_Planck_Distance_Priors(self, *args, **kwargs):
        if self.physical_density_parameters:
            Obh2 = self.species['baryons'].density_parameter.get_value(**kwargs)
            Och2 = self.species['cdm'].density_parameter.get_value(**kwargs)
        else:
            h = self.HubbleParameter.get_value(**kwargs) / 100
            h2 = h*h
            Obh2 = self.species['baryons'].density_parameter.get_value(**kwargs)*h2
            Och2 = self.species['cdm'].density_parameter.get_value(**kwargs)*h2

        g1 = 0.0783 * Obh2**-0.238/(1 + 39.5 * Obh2**0.763)
        g2 = 0.560/(1 + 21.1 * Obh2**1.81)
        Omh2 = Obh2 + Och2
        zdec = 1048 * (1 + 0.00124 * Obh2**-0.738) * (1 + g1 * Omh2**g2)
        da_comoving = self.d_a(zdec, **kwargs) 
        R = np.sqrt(Omh2) * da_comoving * 1e5 / speedoflight
        rs = self.r_s(zdec, **kwargs)
        try:
            l_A = np.pi * da_comoving / rs
        except ZeroDivisionError:
            l_A = np.nan
        return np.array([R, l_A, Obh2])


##########
################ END OF CosmologicalSetup CLASS
############################################################

class EquationOfState(object):
    def __init__(self, EoStype, value=None, parameters=[], woa=None):
        self.type = EoStype
        self.parameters = parameters
        if not value is None:
            self.value = value
            # if not defined, value will be checked on demand, from the free
            # parameters
        elif woa:
            from EPIC.cosmology import EoS_parametrizations
            self.w_of_a = eval('EoS_parametrizations.%s' % woa)

        # some shortcuts
        self.cosmological_constant = self.type == 'cosmological_constant'
        self.pressureless = self.type == 'pressureless'
        self.constant_EoS = self.type == 'constant'

class Fluid(object):
    def __init__(self, name, w, density_parameter):
        self.name = name 
        self.EoS = w
        self.density_parameter = density_parameter

    def is_directly_solvable(self):
        conditions = []
        # The solution to the density of a fluid does not depend on an unknown
        # evolution of other fluid when:
        # it is not a InteractingFluid instance (sufficient for now, while two
        # types of fluids are implemented, interacting and non-interacting
        conditions.append(
                isinstance(self, NonInteractingFluid))
        # We still know how to obtain it when it interacts but either the interaction
        # term depends on its density only and not on another's or it does
        # depend on another's density but it is cosmological constant type EoS
        # itself. In all cases, the other fluid can have constant or
        # parametrized EoS
        conditions.append(
                isinstance(self, InteractingFluid) \
                        and (self.EoS.cosmological_constant or \
                            not hasattr(self, 'interacts_with')
                            )
                        )
        return np.any(conditions)

    def rho_over_rho0(self, a, a0=1, **kwargs):
        # possibility of interaction - check if it is child class
        # implemented notation corresponds to Q = + 3 H xi rho 
        if isinstance(self, NonInteractingFluid):
            if self.EoS.type == 'cosmological_constant':
                return 1 if isinstance(a, float) else np.ones_like(a)
            elif self.EoS.type == 'pressureless':
                return self.rho_parametric_EoS(a, w0=0, exp_integral=1, xi=0, a0=a0)
            elif self.EoS.type == 'constant':
                w0 = getattr(self.EoS, 'value', None)
                if w0 is None:
                    assert len(self.EoS.parameters) == 1
                    w0 = self.EoS.parameters[0].get_value(**kwargs)
                return self.rho_parametric_EoS(a, w0=w0, exp_integral=1, xi=0, a0=a0)
            else:
                return self.rho_parametric_EoS(a, w0=0, exp_integral=True, xi=0, a0=a0, **kwargs)

        elif isinstance(self, InteractingFluid):
            try:
                xi = self.interaction_parameter.get_value(**kwargs)
            except AttributeError:
                xi = self.interacts_with.interaction_parameter.get_value(**kwargs)
            xi *= self.interaction_sign
            if not hasattr(self, 'interacts_with'):
                if self.EoS.type in ['constant', 'cosmological_constant', 'pressureless']:
                    w0 = getattr(self.EoS, 'value', None)
                    # default -1 for DE
                    if w0 is None:
                        assert len(self.EoS.parameters) == 1
                        w0 = self.EoS.parameters[0].get_value(**kwargs)
                    exp_integral = 1
                else:
                    w0 = 0
                    exp_integral = True
                return self.rho_parametric_EoS(a, w0=w0,
                        exp_integral=exp_integral, xi=xi, a0=a0, **kwargs)

            else:
                if self.EoS.cosmological_constant:
                    assert self.EoS.value == -1
                    if self.interacts_with.EoS.type in ['cosmological_constant',  'constant', 'pressureless']:
                        wb = getattr(self.interacts_with.EoS, 'value', None)
                        if wb is None:
                            assert len(self.interacts_with.Eos.parameters) == 1
                            # default 0 for pressureless
                            wb = self.interacts_with.EoS.parameters[0].get_value(**kwargs)
                        return self.interacting_rho_parametric_EoS(a, wb=wb,
                                expintb=1, xi=xi, a0=a0, **kwargs)
                    else:
                        return self.interacting_rho_parametric_EoS(a, wb=0,
                                expintb=self.interacts_with, xi=xi, a0=a0,
                                **kwargs)
                else:
                    raise NotAnalytic('Should not have come here. Check direct' \
                            ' solving conditions.')
        else:
            raise Unsupported('What kind of fluid is this?')

    def interacting_rho_parametric_EoS(self, a, wb=0,
            expintb=1, xi=0, a0=1, **kwargs):
        if isinstance(expintb, InteractingFluid):
            expintb = expintb.get_exponential_int_w_over_a(a, a0=a0, **kwargs)
        xib = xi * self.interacts_with.interaction_sign
        xia = xi * self.interaction_sign
        assert self.interacts_with.interaction_sign == - self.interaction_sign
        rhoa0 = self.density_parameter.get_value(**kwargs)
        rhob0 = self.interacts_with.density_parameter.get_value(**kwargs)
        return 1 + rhob0/rhoa0 * xia/(xib-1-wb) * expintb**(-3) \
                * ( (a/a0)**(3*(xib-1-wb)) - 1)

    def rho_parametric_EoS(self, a, w0=0, exp_integral=1, xi=0, a0=1, **kwargs):
        if exp_integral is True:
            exp_integral = self.get_exponential_int_w_over_a(a, a0=a0,
                    **kwargs)
        return (a/a0)**(3*(xi-1-w0)) * exp_integral**(-3)

    def get_exponential_int_w_over_a(self, a, a0=1, **kwargs):
        # effective EoS is in the integral of the parametric EoS
        # integral = int_a0^a w(a') da'/a'
        # analytic
        try:
            return self.EoS.w_of_a(a, a0=a0, expIwoa=True, **kwargs)
        except NotAnalytic:
            # numeric
            return np.exp(integrate.quad(lambda A: \
                    self.EoS.w_of_a(A, a0=a0, **kwargs)/A, a0, a))

    def drho_da(self, rho, a, intermediate=[], a0=1, **kwargs):
        # This is the dot function for runge kutta integration
        # use when interaction is more complicated, depending on energy
        # density of other species 
        # if Q is not defined it is because the integration can be done
        # analytically, no need to use this
        assert len(intermediate) == 1
        #H = intermediate[0]
        # intermediate is just a placeholder in this case
        Q = self.Q(a, **kwargs) if hasattr(self, 'Q') else 0

        w = getattr(self.EoS, 'value', None)
        if w is None:
            if self.EoS.type == 'constant':
                w = self.EoS.parameters[0].get_value(**kwargs)
            else:
                w = self.EoS.w_of_a(a, a0=a0, **kwargs)

        return Q - 3 * rho * (1 + w) / a

class NonInteractingFluid(Fluid):
    def __init__(self, name, w, density_parameter):
        super().__init__(name, w, density_parameter)
        self.directly_solvable = self.is_directly_solvable()

class InteractingFluid(Fluid):
    '''
    because of interacting_other, must always define first the simpler
    interacting fluid, which depends on its own density.
    '''
    def __init__(self, name, w, density_parameter, interaction_setup={}, model_name=None):
        ''' uses the following keys for interaction_setup:
        parameter, tex_paramter, sign, propto_other.
        Omitting any of them will default to None.
        '''
        super().__init__(name, w, density_parameter)
        self.interaction_parameter = interaction_setup.get('parameter')
        if self.interaction_parameter is not None:
            # promotes it to a FreeParameter obj
            tex_parameter = interaction_setup.get('tex_parameter')
            self.interaction_parameter = FreeParameter(self.interaction_parameter,
                    tex=tex_parameter, model_name=model_name)
        self.interaction_sign = interaction_setup.get('sign')
        self.interaction_propto_other = interaction_setup.get('propto_other')
        if self.interaction_propto_other is None:
            assert self.interaction_sign is not None
        else:
            # interaction with two or more fluids not implemented at the moment
            self.Q = self.two_fluid_propto_other
        self.directly_solvable = self.is_directly_solvable()

    def two_fluid_propto_other(self, a, **kwargs):
        # should not be called if self.interaction_propto_other is None
        xi = self.interacts_with.interaction_parameter.get_value(**kwargs)
        other = self.interacts_with.density_parameter.get_value(**kwargs)
        return self.interaction_sign * 3 * other * xi / a

# Free parameter applies to w0, wa, etc...
# densities will be a special subclass
# define sample in runtime
class Parameter(object):
    def __repr__(self):
        return ' '.join([str(self.__class__).split('.')[-1].rstrip("'>"), \
                self.label])

class FreeParameter(Parameter):
    def __init__(self, label, tex=None, model_name='DEFAULT'):
        self.label = label
        self.tex = tex or label

        default_values = configparser.ConfigParser()
        default_values.read([
            os.path.join(root, 'cosmology', 'default_parameter_values.ini'),
            os.path.join(root, 'modifications', 'cosmology',
                'default_parameter_values.ini'),
            ])
        model_name_or_default = model_name if model_name in default_values else 'DEFAULT'
        self.default = eval(default_values[model_name_or_default].get(label,
            '"(missing default value for %s)"' % self.label))

    def set_prior(self, *pars, distribution='Flat'): # or 'Gaussian'
        from EPIC.utils.statistics import FlatPrior, GaussianPrior
        self.prior = eval("%sPrior" % distribution)(*pars)

    def get_value(self, **kwargs):
        try:
            return self.sim_value
        except AttributeError:
            if hasattr(self, 'fixed_value'):
                return self.fixed_value
            parameter_space = kwargs.get('parameter_space', {})
            accepts_default = kwargs.get('accepts_default', False)
            return parameter_space.get(self.label,
                    self.default if accepts_default else None)

class NuisanceParameter(FreeParameter):
    pass

class HubbleFreeParameter(FreeParameter):
    pass

# This has only a flag to say whether or not it is a physical density parameter
class DensityParameter(FreeParameter):
    def __init__(self, label, tex, physical=True, model_name='DEFAULT'):
        super().__init__(label, tex=tex, model_name=model_name)
        self.physical = physical

class DensityFromTemperature(DensityParameter):
    def __init__(self, temp_parameter, physical=True, model_name='DEFAULT'):
        self.temperature = temp_parameter
        super().__init__(self.temperature.label, self.temperature.tex,
                physical=physical, model_name=model_name)

    def get_value(self, **kwargs):
        try:
            return self.sim_value
        except AttributeError:
            try:
                return self.fixed_value
            except AttributeError:
                T = self.temperature.get_value(**kwargs) # in units of K
                Omega = get_Omega_from_Temperature(T)
                sub_species = kwargs.get('sub_species', None)

                if sub_species == 'photons':
                    pass
                elif sub_species == 'neutrinos':
                    Omega *= 0.68132195298 # 3 * 7/8 * (4/11)**(4/3)
                else:
                    assert sub_species is None
                    Omega *= 1.68132195298 # (1 + 3 * (7/8) * (4/11)**(4/3))

                if self.physical:
                    return Omega
                h = self.hubble.get_value(**kwargs)/100
                if hasattr(self.temperature, 'fixed_value'):
                    self.fixed_value = Omega/h**2
                    return self.fixed_value
                return Omega/h**2

class DerivedParameter(Parameter):
    def __init__(self, label, dependencies, tex=None, physical=None):
        self.label = label
        self.tex = tex or label
        self.physical = physical
        self.dependencies = dependencies

    def flatness(self, densities, **kwargs):
        Omegas_sum = sum([Omega.get_value(**kwargs) for Omega in densities])
        if self.physical:
            return self.hubble.get_value(**kwargs)**2 - Omegas_sum
        return 1 - Omegas_sum

    def Hubble(self, densities, **kwargs):
        assert self.physical
        Omegas_sum = sum([Omega.get_value(**kwargs) for Omega in densities])
        return np.sqrt(Omegas_sum)

    def get_value(self, **kwargs):
        try:
            return self.sim_value
        except AttributeError:
            if isinstance(self, HubbleDerivedParameter):
                return self.Hubble(self.dependencies, **kwargs)
            return self.flatness(self.dependencies, **kwargs)

    def get_available_species(self):
        available_species = configparser.ConfigParser()
        available_species.read([
            os.path.join(root, 'cosmology', 'available_species.ini'),
            os.path.join(root, 'modifications', 'cosmology',
                'available_species.ini'),
            ])
        return available_species

class HubbleDerivedParameter(DerivedParameter):
    pass

class DerivedDensityDistribution(DerivedParameter):
    def __init__(self, name, h, dens_parameter, h_bf, bestfit, physical=True):
        self.name = name
        if physical:
            self.Omega = [dens_parameter/h**2,]
            self.bestfit = [bestfit/h_bf**2,]
        else:
            self.Omega = [dens_parameter*h**2,]
            self.bestfit = [bestfit*h_bf**2,]
        available_species = self.get_available_species()
        physical_ = '' if physical else 'physical ' 
        self.label = [available_species['%sdensity parameter' % physical_].get(self.name),]
        self.tex = [available_species['tex %sdensity parameter' % physical_].get(self.name,
                self.label[0]),]

class DerivedParameterDensityDistribution(DerivedParameter):
    def __init__(self, name, h, dependencies, h_bf, dependencies_bf, physical=True):
        self.name = name
        self.physical = physical
        self.Omega = self.flatness(dependencies, h=h)
        self.bestfit = self.flatness(dependencies_bf, h=h_bf)
        available_species = self.get_available_species()
        self.label = [available_species['physical density parameter'].get(self.name), 
                available_species['density parameter'].get(self.name)]
        self.tex = [available_species['tex physical density parameter'].get(self.name), 
                available_species['tex density parameter'].get(self.name)]

    def flatness(self, densities, h=None):
        # densities is a list of arrays (MCMC distributions)
        Omegas_sum = sum(densities)
        h2 = h**2
        if self.physical: # checking with the last density but could be any
            return [h2 - Omegas_sum, 1 - Omegas_sum/h2]
        return [h2 - Omegas_sum*h2, 1 - Omegas_sum]

class DerivedParameterMatterDensityDistribution(DerivedParameterDensityDistribution):
    def flatness(self, constituents, h=None):
        Omega = sum(constituents)
        h2 = h**2
        if self.physical:
            return [Omega, Omega/h2]
        return [Omega*h2, Omega]

class DerivedDensityFromTemperature(DerivedParameter):
    def __init__(self, name, h, Tg, h_bf, bestfit):
        self.name = name
        Omega = get_Omega_from_Temperature(Tg)
        self.Omega = [Omega, Omega/h**2]
        Omega_bf = get_Omega_from_Temperature(bestfit)
        self.bestfit = [Omega_bf, Omega_bf/h_bf**2]
        self.label = ['Orh2', 'Or0']
        self.tex = [r'\Omega_{r0}h^2', r'\Omega_{r0}']

class Cluster(object):
    def __init__(self, name, redshift, Mmu, Msig, cmu, csig, Tmu, Tsig, Tsym,
            dT):
        self.name = name
        self.z = float(redshift)
        logM200 = uncertainties.ufloat_fromstr(Mmu + '+/-' + Msig) 
        logc = uncertainties.ufloat_fromstr(cmu + '+/-' + csig)
        Om = 0.3
        Ode = 1 - Om
        self.Hz = 100 * np.sqrt(Om*(1+self.z)**3 + Ode)
        self.rhoc = rho_critical(self.Hz)
        # r200 over M200**(1/3)
        roM = (3 / (4*np.pi) / 200 / self.rhoc )**(1/3) * (1e14)**(1/3)
        #self.r200 = (3 / (4*np.pi) / 200 / self.rhoc )**(1/3) * (1e14)**(1/3) \
        #        * self.M200**(1/3)
        temperature = {}
        try:
            temperature['logT'] = uncertainties.ufloat_fromstr(Tmu + '+/-' + Tsig)
        except ValueError:
            temperature['Tsym'] = uncertainties.ufloat_fromstr(Tsym + '+/-' + dT)
        self.fc, self.dFdc = self.fc_gc_dFdc_from_c(logc)
        self.ovr = get_OVR(roM, temperature, logM200, self.fc)

    def fc_gc_dFdc_from_c(self, logc):
        self.c = umath.exp(logc)
        c = self.c
        one_plus_c = 1+c
        two_plus_c = 2+c
        c_squared = c*c
        log_one_plus_c = umath.log(one_plus_c)
        one_plus_c__times__log_opc = one_plus_c * log_one_plus_c
        one_plus_c__times__logsquare = one_plus_c__times__log_opc \
                * log_one_plus_c
        fc = one_plus_c__times__logsquare - 2 * c * log_one_plus_c
        fc = fc + one_plus_c * c_squared / one_plus_c**2
        fc = fc / c / (0.5*(one_plus_c- 1/one_plus_c) - log_one_plus_c)

        dFdc = 2 * (one_plus_c__times__log_opc - c) 
        dFdc = dFdc * (c*(4+5*c+c_squared) * log_one_plus_c -c_squared *(2+3*c) \
                - 2 * one_plus_c__times__logsquare)
        dFdc = -1 * dFdc /(c_squared \
                * (c *two_plus_c-2*one_plus_c__times__log_opc)**2)
        return fc, dFdc

    def __repr__(self):
        return self.name

def get_OVR(roM, temperature, logM200, fc):
    try:
        ovr = umath.exp(-2/3 * logM200 + temperature['logT'])
    except KeyError:
        ovr = umath.exp(-2/3 * logM200) * temperature['Tsym']
    ovr *= roM * fc
    ovr *= (-3/2 * 1e-14/GmumH)
    return ovr

def get_Omega_from_Temperature(T):
    rho = a_B_over_c2 * T**4 # in units of kg m^-3
    rho_cr = rho_critical_SI(100) # in units of h^2 kg m^-3
    return rho / rho_cr # in units of h^-2

