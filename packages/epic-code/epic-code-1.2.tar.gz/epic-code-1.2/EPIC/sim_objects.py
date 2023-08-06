import os
import re
import shutil
from EPIC.utils import statistics, io_tools, data_tools, math_functions
from EPIC.cosmology import observations, cosmic_objects as cosmo
from EPIC import root
import scipy.stats as st
import configparser
from collections import OrderedDict
import numpy as np
import time
import pickle
import ctypes
import click
import multiprocessing

# generic simulation object class
class Simulation(object):
    def __init__(self, working_dir, analysis, print_info=True):
        self.working_dir = working_dir
        self.ini_file = os.path.join(self.working_dir, 'simulation_info.ini')
        if print_info:
            print('Simulation at %s.' % self.working_dir)
        self.conf = configparser.ConfigParser()
        self.read_conf()
        self.chains_size = self.conf['status'].getint('chains size')
        self.counter = self.conf['status'].getint('counter')
        self.cumulated_time = self.conf['status'].getfloat('cumulated time')
        self.chains = []
        for i in range(self.conf['settings'].getint('chains')):
            self.chains.append(self.build_chain(self.working_dir, i))
        self.proposal_distribution = np.random.multivariate_normal
        self.working_dir = working_dir
        self.analysis = analysis

    def plot_location(self, stop_at=None):
        results = [f for f in os.listdir(self.working_dir) \
                if os.path.isdir(os.path.join(self.working_dir, f)) \
                and re.match('n\d+$', f)]
        results = sorted(results, key=lambda r: int(r.lstrip('n')))
        if stop_at is not None:
            results = [r for r in results if int(r.lstrip('n')) <= stop_at]
        loc = os.path.join(self.working_dir, results[-1])
        return loc

    def read_conf(self):
        self.conf.read(self.ini_file)

    def remove_bad_chains(self, rates, limits=[0.1, 0.5]):
        amin, amax = limits
        chain_removed = False

        for i in range(len(self.chains))[::-1]:
            if not amin <= rates[i] <= amax:
                self.remove_chain(i)
                print('Chain %i removed (acc = %.4f).' % (i, rates[i]))
                chain_removed = True
                rates.pop(i)
        return rates

    def remove_chain(self, i):
        folders = ['chains', 'current_states']

        self.chains[i].index = None
        for chain_file in folders:
            os.remove(os.path.join(self.working_dir, chain_file,
                'chain_{0}.txt'.format(i)))
            #print('Removed chain_{1}.txt from {0}'.format(chain_file, i))

        for j in range(i+1, len(self.chains)):
            for chain_file in folders:
                os.rename(
                        os.path.join(self.working_dir, chain_file,
                            'chain_{0}.txt'.format(j)),
                        os.path.join(self.working_dir, chain_file,
                            'chain_{0}.txt'.format(j-1))
                        )
                #print('Renamed chain_{1}.txt to chain_{2}.txt in {0}'.format(
                #    chain_file, j, j-1))
            self.chains[j].index -= 1
            #print('Chain {0} index changed to {1}'.format(j,
            #    self.chains[j].index))

        self.chains.pop(i)
        self.read_conf()
        self.conf.set('settings', 'chains', int(len(self.chains)))
        self.conf_write_to_file()

    def get_derived_distributions(self):
        distributions = OrderedDict({})
        #if physical:
        if hasattr(self.analysis.model.HubbleParameter, 'fixed_value'):
            hubble_bf = self.analysis.model.HubbleParameter.fixed_value
            hubble = float(hubble_bf)
        else:
            h_index = [isinstance(par, cosmo.HubbleFreeParameter) \
                    for par in self.analysis.parameters]
            h_index = h_index.index(True)
            hubble = np.array(self.processed_chains[h_index])
            hubble_bf = float(self.bestfit[self.analysis.parnames[h_index]])
        if not self.analysis.model.physical_density_parameters:
            hubble /= 100
            hubble_bf /= 100
        independent_Omegas = []
        independent_Omegas_bf = []
        I = int(not self.analysis.model.physical_density_parameters) # index 0 is physical
        for fluid in self.analysis.model.species.values():
            if fluid.density_parameter.label in self.analysis.parnames:
                index = self.analysis.parnames.index(fluid.density_parameter.label)
                if isinstance(fluid.density_parameter,
                        cosmo.DensityFromTemperature):
                    Tg = np.array(self.processed_chains[index])
                    distributions[fluid.name] = cosmo.DerivedDensityFromTemperature(
                            fluid.name, hubble, Tg, hubble_bf,
                            self.bestfit[fluid.density_parameter.label])
                    independent_Omegas.append(distributions[fluid.name].Omega[I]) 
                    independent_Omegas_bf.append(distributions[fluid.name].bestfit[I])
                elif isinstance(fluid.density_parameter, cosmo.DensityParameter):
                    dens_parameter = np.array(self.processed_chains[index])
                    independent_Omegas.append(dens_parameter)
                    dens_parameter_bf = self.bestfit[fluid.density_parameter.label]
                    independent_Omegas_bf.append(dens_parameter_bf)
                    distributions[fluid.name] = cosmo.DerivedDensityDistribution(
                            fluid.name, hubble, dens_parameter, hubble_bf,
                            dens_parameter_bf,
                            physical=self.analysis.model.physical_density_parameters)
            elif fluid.density_parameter.label in self.analysis.fixed:
                fixed_value = self.analysis.fixed[fluid.density_parameter.label]
                fixed_value_bf = float(fixed_value)
                if isinstance(fluid.density_parameter,
                        cosmo.DensityFromTemperature):
                    fixed_value = cosmo.get_Omega_from_Temperature(fixed_value)
                    fixed_value_bf = float(fixed_value)
                    if not self.analysis.model.physical_density_parameters:
                        fixed_value /= hubble**2
                        fixed_value_bf /= hubble_bf**2
                independent_Omegas.append(fixed_value)
                independent_Omegas_bf.append(fixed_value_bf)

        derived_fluid = [fluid for fluid in self.analysis.model.species.values() \
                if (fluid.density_parameter.label not in self.analysis.parnames) and \
                (fluid.density_parameter.label not in self.analysis.fixed)][0]
        distributions[derived_fluid.name] = cosmo.DerivedParameterDensityDistribution(
                derived_fluid.name, hubble, independent_Omegas, hubble_bf,
                independent_Omegas_bf,
                physical=self.analysis.model.physical_density_parameters)
        model_recipes = configparser.ConfigParser()
        model_recipes.read([
            os.path.join(root, 'cosmology', 'model_recipes.ini'),
            os.path.join(root, 'modifications', 'cosmology',
                'model_recipes.ini'),
            ])
        supported_composed_species = eval(model_recipes[self.analysis.model.model].get(
            'supported composed species', '[]'))
        physical_ = 'physical ' if self.analysis.model.physical_density_parameters else ''
        available_species = configparser.ConfigParser()
        available_species.read([
            os.path.join(root, 'cosmology', 'available_species.ini'),
            os.path.join(root, 'modifications', 'cosmology',
                'available_species.ini'),
            ])
        for fluid in supported_composed_species:
            constituents = [component for component in eval(available_species['composed of'][fluid]) \
                    if component in self.analysis.model.species]
            if len(constituents) > 1:
                components = []
                components_bf = []
                for component in constituents:
                    label = available_species['%sdensity parameter' % physical_][component]
                    index = self.analysis.parnames.index(label)
                    components.append(self.processed_chains[index])
                    components_bf.append(self.bestfit[label])
                distributions[fluid] = cosmo.DerivedParameterMatterDensityDistribution(
                        fluid, hubble, components, hubble_bf, components_bf,
                        physical=self.analysis.model.physical_density_parameters)
        derived_bf_dict = OrderedDict({})
        for derived in distributions.values():
            for label, bf in zip(derived.label, derived.bestfit):
                derived_bf_dict[label] = bf
        self.read_conf()
        self.conf.set('status', 'derived best fit', str(derived_bf_dict))
        self.conf_write_to_file()
        return distributions

    def plot_sequences(self, args):
        burn_in = getattr(args, 'burn_in', None) or self.truncated_size//2
        thin = getattr(args, 'thin', None) or 1
        stop_at = getattr(args, 'stop_at', None)

        plt = load_plt(args)
        fig, axes = plt.subplots(self.analysis.nparams, len(self.chains), sharex='col')
        fig.set_size_inches(len(self.chains)*2.5, self.analysis.nparams*1.5)
        
        with click.progressbar(length=self.analysis.nparams*len(self.chains), width=10,
                show_pos=False, empty_char='.',
                label=io_tools.fixed_length('Plotting sequences...'),
                info_sep='  |  ', show_eta=False) as bar:
            for i in range(self.analysis.nparams * len(self.chains)):
                jx, jy = divmod(i, len(self.chains))
                axes[jx][jy].plot(range(self.list_of_chains[jy][:,jx].size)[burn_in::thin],
                        self.list_of_chains[jy][burn_in::thin,jx], lw=0.5)
                bar.update(1)

        for j in range(len(self.chains)):
            axes[-1][j].set_xlabel('Sequence number')
            axes[0][j].xaxis.set_label_position('top')
            axes[0][j].set_xlabel('Chain %i' % j)

        for i, par in enumerate(self.analysis.parameters):
            axes[i][0].set_ylabel(r'$' + par.tex + '$')

        fig.tight_layout()
        loc = self.plot_location(stop_at=stop_at)
        fig.savefig(os.path.join(loc, 'sequences.pdf'))

    def ACF(self, args):
        thin = getattr(args, 'thin', None)
        burn_in = getattr(args, 'burn_in', None)
        stop_at = getattr(args, 'stop_at', None) 
        loc = self.plot_location(stop_at=stop_at)
        io_tools.pasta(loc, 'correlation_lengths')
        jobs = [multiprocessing.Process(
            target=self.twopar_correlation,
            args=(m,),
            kwargs={'thin': thin, 'burn_in': burn_in, 'stop_at': stop_at}
            ) for m in range(len(self.chains))]

        print('Calculating correlations...')
        itime = time.time()
        for j in jobs:
            j.start()
        for j in jobs:
            j.join()

        print('Now plotting...', end=' ')
        for m in range(len(self.chains)):
            self.plot_correlations(m, args)
        print('Done! (in {0})'.format(io_tools.printtime(time.time() - itime)))

    def twopar_correlation(self, m, burn_in=None, stop_at=None, thin=None,
            bar=None):
        burn_in = burn_in or self.truncated_size//2
        thin = thin or 1

        chain_autocorr = []
        loc = self.plot_location(stop_at=stop_at)

        for i in range(self.analysis.nparams * self.analysis.nparams):
            jx, jy = divmod(i, self.analysis.nparams)
            if jx > jy:
                lagsize = self.list_of_chains[m][burn_in:,jx].size
                assert self.list_of_chains[m][burn_in:,jy].size == lagsize
                tpcorr = [statistics.correlation(self.list_of_chains[m][burn_in:,jy],
                    self.list_of_chains[m][burn_in:,jx], lag) \
                            for lag in range(lagsize//2)[::thin]]
                np.savetxt(os.path.join(loc, 'correlation_lengths',
                    'corr%i_%s_%s.txt' % (m, self.analysis.parameters[jx].label,
                        self.analysis.parameters[jy].label)),
                    list(zip(list(range(lagsize//2))[::thin], tpcorr))) 

            elif jx < jy:
                pass 

            else:
                lagsize = self.list_of_chains[m][burn_in:,jx].size
                aucorr = [statistics.auto_correlation(
                    self.list_of_chains[m][burn_in:,jx], lag) \
                            for lag in range(lagsize//2)[::thin]]
                chain_autocorr.append(aucorr)
                np.savetxt(os.path.join(loc, 'correlation_lengths',
                    'aucorr%i_%s.txt' % (m, self.analysis.parameters[jx].label)),
                    list(zip(list(range(lagsize//2)[::thin]), aucorr)))
                if bar:
                    bar.update(1)

        return chain_autocorr

    def plot_correlations(self, m, args, P0=None):
        plt = load_plt(args)
        grid, subplots = plt.subplots(self.analysis.nparams,
                self.analysis.nparams, sharex='col', sharey='row')
        grid.set_size_inches(self.analysis.nparams*2.5, self.analysis.nparams*1.6)

        loc = self.plot_location(stop_at=args.stop_at)
        for i in range(self.analysis.nparams * self.analysis.nparams):
            jx, jy = divmod(i, self.analysis.nparams)
            if jx > jy:
                x, tpcorr = np.loadtxt(os.path.join(loc, 'correlation_lengths',
                    'corr%i_%s_%s.txt' % (m, self.analysis.parameters[jx].label,
                        self.analysis.parameters[jy].label)), unpack=True)
                subplots[jx][jy].plot(x, tpcorr, lw=1, 
                        label=r'$' + self.analysis.parameters[jy].tex \
                                + r' \times ' + self.analysis.parameters[jx].tex + '$')
                subplots[jx][jy].axhline(0, ls='--', lw=0.3, color='k')
                #if P0:
                #    tau = math_functions.fit_tau(x, tpcorr, P0)
                #    subplots[jx][jy].plot(math_functions.exponential_corr(x,
                #    tau), lw=0.5, color='C1', ls=':', label=r'$\tau = ' +
                #    "%.2f" % tau + '$')
                #    np.savetxt(os.path.join(loc, 'correlation_lengths',
                #    'tau%i_%s_%s.txt' % (m, self.analysis.parameters[jx].label,
                #    self.analysis.parameters[jy].label)), [tau,])
                subplots[jx][jy].legend(loc='upper right', frameon=False,
                        borderaxespad=0.5, handletextpad=0.5)
                subplots[jx][jy].tick_params(size=3)
            elif jx < jy:
                grid.delaxes(subplots[jx][jy])

            else:
                x, aucorr = np.loadtxt(os.path.join(loc, 'correlation_lengths',
                    'aucorr%i_%s.txt' % (m, self.analysis.parameters[jx].label)),
                    unpack=True)
                subplots[jx][jy].plot(x, aucorr, lw=1,
                        label=r'$' + self.analysis.parameters[jy].tex + '$')
                subplots[jx][jy].axhline(0, ls='--', lw=0.3, color='k')
                if P0:
                    tau = math_functions.fit_tau(x, aucorr, P0)
                    subplots[jx][jy].plot(math_functions.exponential_corr(x,
                        tau), lw=0.5, color='C1', ls=':',
                        label=r'$\tau = ' + "%.2f" % tau + '$')
                    np.savetxt(os.path.join(loc, 'correlation_lengths',
                        'tau%i_%s.txt' % (m, self.analysis.parameters[jx].label)),
                        [tau,])
                subplots[jx][jy].legend(loc='upper right', frameon=False,
                        borderaxespad=0.5, handletextpad=0.5)
                subplots[jx][jy].tick_params(size=3)

        for jy in range(self.analysis.nparams):
            subplots[-1][jy].set_xlabel('Lag')
            subplots[jy][0].set_ylabel('Correlation')

        grid.tight_layout()
        grid.subplots_adjust(hspace=0,wspace=0)
        grid.savefig(os.path.join(loc, "correlation_lengths",
            'grid_chain%i.pdf' % m))

    def prepare_data_view_1D(self, loc, args, bar=None):
        derived_labels = []
        derived_Omegas = []
        for derived in self.derived_distributions.values():
            for label, Omega in zip(derived.label, derived.Omega):
                derived_labels.append(label)
                derived_Omegas.append(Omega)
        priors = OrderedDict([(par.label, par.prior) for par in self.analysis.parameters])
        splits = OrderedDict([(par.label, par.split) for par in self.analysis.parameters])
        is_derived = np.concatenate([np.zeros(self.analysis.nparams,
            dtype=bool), np.ones(len(derived_labels), dtype=bool)])
        self.weakly_constrained = OrderedDict({})

        for par_label, chain, is_this_derived in zip(
                self.analysis.parnames + derived_labels, 
                self.processed_chains + derived_Omegas,
                is_derived):
            count, seps, widths = data_tools.numpyhist(chain, args.bins)
            self.weakly_constrained[par_label] = False if is_this_derived else(
                    count.std()/count.mean() <= 0.5 \
                            or count.min()/count.max() >= 0.05 \
                            or count[0] / count.max() >= 0.05 \
                            or count[-1] / count.max() >= 0.05
                            )
            np.savetxt(os.path.join(loc,
                'combo_count_{0}.txt'.format(par_label)), count)
            np.savetxt(os.path.join(loc, 
                'combo_seps_{0}.txt'.format(par_label)), seps)
            np.savetxt(os.path.join(loc,
                'combo_widths_{0}.txt'.format(par_label)), widths)

            normalization = len(chain) * (seps[-1] - seps[0])/len(count)
            count = np.array(count) * normalization
            np.savetxt(os.path.join(loc, 'doacount_{0}.txt'.format(par_label)),
                    count)
            np.savetxt(os.path.join(loc, 'seps_{0}.txt'.format(par_label)),
                    seps)
            np.savetxt(os.path.join(loc,
                'normalization_{0}.txt'.format(par_label)), (normalization,))

        kde = getattr(args, 'kde', False)
        if kde:
            jobs = []
            io_tools.pasta(loc, 'kde')
            for par_label, chain in zip(
                    self.analysis.parnames + derived_labels,
                    self.processed_chains + derived_Omegas):
                density_file = os.path.join(loc, 'kde',
                        'kdensity_{0}.txt'.format(par_label))
                kded = os.path.isfile(density_file)
                if args.redo_kde or not kded:
                    seps = np.loadtxt(os.path.join(loc,
                        'seps_{0}.txt'.format(par_label)))
                    try:
                        a_edg = priors[par_label].vmin
                        b_edg = priors[par_label].vmax
                    except (TypeError, KeyError):
                        a_edg = seps[0]
                        b_edg = seps[-1]
                    
                    axpad = (chain.max() - chain.min()) * 0.15
                    try:
                        hx1 = max(priors[par_label].vmin, chain.min()-axpad)
                        hx2 = min(priors[par_label].vmax, chain.max()+axpad)
                    except (TypeError, KeyError):
                        hx1 = seps[0] - axpad
                        hx2 = seps[-1] + axpad

                    split_par = splits.get(par_label, None)
                    if split_par is not None:
                        jobs.append(
                                multiprocessing.Process(
                                    target = statistics.make_kde,
                                    args = (
                                        [
                                            chain[chain < split_par], 
                                            chain[chain > split_par],
                                        ],
                                    ),
                                    kwargs = {
                                        'support_file': os.path.join(loc,
                                            'kde',
                                            'ksupport_{0}.txt'.format(par_label)),
                                        'density_file': density_file,
                                        'thin': args.thin,
                                        'bar': bar
                                    }
                                )
                        )

                    else:
                        jobs.append(
                                multiprocessing.Process(
                                    target = statistics.make_kde,
                                    args = ([chain,],),
                                    kwargs = {
                                        'a_support': hx1,
                                        'b_support': hx2,
                                        'a_edg': a_edg, 'b_edg': b_edg,
                                        'support_file': os.path.join(loc,
                                            'kde',
                                            'ksupport_{0}.txt'.format(par_label)
                                        ),
                                        'density_file': density_file, 
                                        'thin': args.thin,
                                        'correct_boundaries': self.weakly_constrained[par_label],
                                        'kde_shuffle': args.kde_shuffle,
                                        'bar': bar
                                    }
                                )
                        )
                else:
                    bar.update(1)

            for job in jobs:
                job.start()
            for job in jobs:
                job.join()

    def prepare_data_view_2D(self, loc, args, bar=None):
        free_parameters = [par for par in self.analysis.parameters if isinstance(par,
            cosmo.FreeParameter)]
        combo = [chain for chain, par in zip(self.processed_chains,
            self.analysis.parameters) if isinstance(par, cosmo.FreeParameter)]
        nparams = len(free_parameters)

        for i in range(nparams * nparams):
            jx, jy = divmod(i, nparams)
            if jx > jy:
                ax = np.array(combo[jy])
                ay = np.array(combo[jx])
                np.savetxt(os.path.join(loc,
                    'corr_xy_{0}_{1}.txt'.format(free_parameters[jx].label,
                        free_parameters[jy].label)),
                    (statistics.correlation(ax, ay, 0),)
                    )
                ws = None

                axpad = (ax.max() - ax.min()) * 0.15
                hx1 = max(ax.min()-axpad, free_parameters[jy].prior.vmin)
                hx2 = min(ax.max()+axpad, free_parameters[jy].prior.vmax)
                aypad = (ay.max() - ay.min()) * 0.15
                hy1 = max(ay.min()-aypad, free_parameters[jx].prior.vmin)
                hy2 = min(ay.max()+aypad, free_parameters[jx].prior.vmax)
                hrange = [[hx1, hx2], [hy1, hy2]]
                H, xedg, yedg = np.histogram2d(ax, ay, bins=args.bins,
                    range=hrange, normed=False, weights=ws)
                np.savetxt(os.path.join(loc,
                    'xedg_{0}_{1}.txt'.format(free_parameters[jx].label,
                        free_parameters[jy].label)), xedg)
                np.savetxt(os.path.join(loc,
                    'yedg_{0}_{1}.txt'.format(free_parameters[jx].label,
                        free_parameters[jy].label)), yedg)
                np.savetxt(os.path.join(loc,
                    'H_{0}_{1}.txt'.format(free_parameters[jx].label,
                        free_parameters[jy].label)), H)
                np.savetxt(os.path.join(loc,
                    'hrange_{0}_{1}.txt'.format(free_parameters[jx].label,
                        free_parameters[jy].label)), hrange)
                XX, YY = np.meshgrid(xedg, yedg)
                np.savetxt(os.path.join(loc,
                    'XX_{0}_{1}.txt'.format(free_parameters[jx].label,
                        free_parameters[jy].label)), XX)
                np.savetxt(os.path.join(loc,
                    'YY_{0}_{1}.txt'.format(free_parameters[jx].label,
                        free_parameters[jy].label)), YY)
                if bar:
                    bar.update(1)

            else:
                pass
            
        kde = getattr(args, 'kde', False)
        if kde:
            jobs = []
            io_tools.pasta(loc, 'kde')
            for i in range(nparams * nparams):
                jx, jy = divmod(i, nparams)
                if jx > jy:
                    density_file = os.path.join(loc, 'kde',
                            'kdensity2_{0}_{1}.txt'.format(free_parameters[jx].label,
                                free_parameters[jy].label)
                            )
                    kded = os.path.isfile(density_file)
                    if args.redo_kde or not kded:
                        ax = np.array(combo[jy])
                        ay = np.array(combo[jx])
                        if self.weakly_constrained[free_parameters[jx].label]:
                            hy1 = free_parameters[jx].prior.vmin
                            hy2 = free_parameters[jx].prior.vmax
                        else:
                            aypad = (ay.max() - ay.min()) * 0.15
                            hy1 = max(ay.min()-aypad, free_parameters[jx].prior.vmin)
                            hy2 = min(ay.max()+aypad, free_parameters[jx].prior.vmax)

                        if self.weakly_constrained[free_parameters[jy].label]:
                            hx1 = free_parameters[jy].prior.vmin
                            hx2 = free_parameters[jy].prior.vmax
                        else:
                            axpad = (ax.max() - ax.min()) * 0.15
                            hx1 = max(ax.min()-axpad, free_parameters[jy].prior.vmin)
                            hx2 = min(ax.max()+axpad, free_parameters[jy].prior.vmax)

                        kde_hrange = [[hx1, hx2], [hy1, hy2]]
                        np.savetxt(os.path.join(
                            loc, 'kde', 'kdensity2_hrange_{0}_{1}.txt'.format(
                                free_parameters[jx].label, free_parameters[jy].label
                                )
                            ), kde_hrange)
                        xedg = np.loadtxt(os.path.join(
                            loc, 'xedg_{0}_{1}.txt'.format(free_parameters[jx].label,
                                free_parameters[jy].label
                                )
                            ))
                        yedg = np.loadtxt(os.path.join(
                            loc, 'yedg_{0}_{1}.txt'.format(free_parameters[jx].label,
                                free_parameters[jy].label
                                )
                            ))

                        xa_edg = free_parameters[jy].prior.vmin
                        xb_edg = free_parameters[jy].prior.vmax
                        ya_edg = free_parameters[jx].prior.vmin
                        yb_edg = free_parameters[jx].prior.vmax

                        jobs.append(
                                multiprocessing.Process(
                                    target = statistics.make_kde2d,
                                    args = ([ax,], [ay,]),
                                    kwargs = {
                                        'xa_support': hx1, 'xb_support': hx2, 
                                        'ya_support': hy1, 'yb_support': hy2,
                                        'xa_edg': xa_edg, 'xb_edg': xb_edg,
                                        'ya_edg': ya_edg, 'yb_edg': yb_edg,
                                        'xsupport_file': os.path.join(loc, 'kde',
                                            'kdensity2_xsupport_{0}_{1}.txt'.format(free_parameters[jx].label,
                                                free_parameters[jy].label)),
                                        'ysupport_file': os.path.join(loc, 'kde',
                                            'kdensity2_ysupport_{0}_{1}.txt'.format(free_parameters[jx].label,
                                                free_parameters[jy].label)),
                                        'density_file': density_file,
                                        'thin': args.thin,
                                        'correct_boundaries': self.weakly_constrained[free_parameters[jx].label] \
                                                or self.weakly_constrained[free_parameters[jy].label],
                                        'bar': bar
                                        }
                                    )
                                )
                    else:
                        bar.update(1)
                else:
                    pass

            cpu = multiprocessing.cpu_count()
            if cpu < len(jobs):
                j = 0
                for i in range(len(jobs)//cpu):
                    for job in jobs[j:(i+1)*cpu]:
                        job.start()
                    for job in jobs[j:(i+1)*cpu]:
                        job.join()
                    j += cpu
                for job in jobs[j:(i+1)*cpu + len(jobs)%cpu]:
                    job.start()
                for job in jobs[j:(i+1)*cpu + len(jobs)%cpu]:
                    job.join()
            else:
                for job in jobs:
                    job.start()
                for job in jobs:
                    job.join()

# specific MCMC simulation
class MCMC_Simulation(Simulation):
    def __init__(self, wdir, analysis, print_info=True):
        super().__init__(wdir, analysis, print_info=print_info)
        if print_info:
            print('Mode MCMC.')
        self.proposal_covariance = Proposal_Covariance(self)

    def build_chain(self, wdir, i):
        return MCMC_Chain(wdir, i)

    def conf_write_to_file(self):
        with open(self.ini_file, 'w+') as cfg:
            self.conf.write(cfg)

    def inform_start(self, steps, free, adapt):
        print('Initiating MCMC...')
        if adapt:
            adapt_burnin = (free + adapt) * steps
            print('Adaptive MCMC burn-in: {0}'.format(adapt_burnin))
            self.conf.read(self.ini_file)
            self.conf.set('status', 'adaptive burn-in', str(adapt_burnin))
            self.conf_write_to_file()

    def recalibrate(self, accept_rate, Sigma, N, theta, X, mu):

        gamma = N**-0.6

        for i in range(len(self.chains)):
            mu[i] = (1 - gamma) * mu[i] + gamma * X[i]

        Xmu = X[0] - mu[0]
        Xmu = np.array(Xmu, ndmin=2)
        Sigma = (1 - gamma) * Sigma + gamma * np.dot(Xmu.transpose(), Xmu)

        # Method 1
        # S = 5.6644 / self.analysis.nparams  * Sigma

        # Method 2
        eta = accept_rate[0]
        theta += gamma * (eta - 0.234)
        S = np.exp(2*theta) * Sigma

        return S, Sigma, mu, theta

    def adapt_covariance(self, size, acc_rates):
        if not hasattr(self, 'mu'):
            f = [chain.load_from_file() for chain in self.chains]
            _, f = io_tools.truncate(f)
            self.mu = []
            for F in f:
                self.mu.append(np.mean(F, axis=0)[:self.analysis.nparams])

        S, self.Sigma, self.mu, self.theta = self.recalibrate(
                acc_rates, self.Sigma, size, self.theta,
                self.shared_current_states, self.mu)
        np.savetxt(self.proposal_covariance.covariance_file, S)
        return S

    def MetropolisHastings(self, i, N, **kwargs):
        # thins inner routine does not know whether adapting is on or off
        # sim_value's and sim_matrix'es are defined outside, in start module,
        # when not adapting, so during adaptation get_current_state() and
        # get_matrix() will always read from files. No need to set these values
        # as attributes

        np.random.seed()

        X0 = self.chains[i].get_current_state()
        Xt = np.array(X0[:self.analysis.nparams], ndmin=1)
        lpXt = X0[self.analysis.nparams] 
        llXt = X0[self.analysis.nparams+1] 

        accepted_states = 0
        states_this_run = []
        if lpXt == 0.: 
            lpXt, llXt = self.analysis.log_posterior(
                    parameter_space=self.analysis.prepare_state(Xt), **kwargs
                    )

        for _ in range(N):
            # drawing Y from ~Q(Y, Xt) with numpy. For scipy.stats, use Y =
            # Q(Xt, S).rvs()
            Y = self.proposal_distribution(Xt, self.proposal_covariance.get_matrix())

            candidate_state = self.analysis.prepare_state(Y)

            for par in self.analysis.parameters + self.analysis.derived_parameters:
                par.sim_value = par.get_value(
                        parameter_space=candidate_state, **kwargs)

            lpY, llY = self.analysis.log_posterior(
                    parameter_space=candidate_state, **kwargs)

            for par in self.analysis.parameters + self.analysis.derived_parameters:
                delattr(par, 'sim_value')

            q = 1. if lpY > lpXt else np.exp(lpY - lpXt)
            #q = min(1, np.exp(lpY - lpXt))
            # * Q(Y,S).pdf(Xt)/Q(Xt,S).pdf(Y)) #* np.prod([dpar[var] for var in\
            # analysis.parnames])**-1 ...
            # Metropolis-Hastings
            ## the proposal/kernel distribution Q I'm using is symmetric, then
            ## the second ratio should always be 1 and that's fine. Remember to
            ## include the calculation of the second ratio if I eventually use
            ## an asymmetrical function Q.
            #original: q = posterior(Y)*Q(Y,S).pdf(Xt)/(posterior(Xt)*Q(Xt,S).pdf(Y))
            r = np.random.uniform()
            if r <= q:
                # new state has been accepted
                Xt = Y
                lpXt = lpY
                llXt = llY
                accepted_states += 1

            states_this_run.append(build_stored_line(Xt, lpXt, llXt))

        # this also updates current state chains files
        self.shared_current_states[i] = np.array(Xt)
        self.chains[i].write_compressed(states_this_run)
        self.shared_accepted_states_each_chain[i] += accepted_states

    def find_max_logposterior(self):
        maxlogposterior = []
        for j in range(len(self.chains)): 
            maxlog_thischain = np.nanmax(
                    self.list_of_chains[j][self.truncated_size//2:,
                        self.analysis.nparams]
                    ) # replace reducedburn[j]: with 1: to pick any bf among all points
            maxlogposterior.append(maxlog_thischain)
            max_index = list(self.list_of_chains[j][:,self.analysis.nparams]).index(maxlog_thischain) 
            # this is the index in the entire list, not the slice!!!
        a_with_best_maxlog = maxlogposterior.index(max(maxlogposterior))
        max_index = list(self.list_of_chains[a_with_best_maxlog][:, self.analysis.nparams])\
                .index(np.nanmax(self.list_of_chains[a_with_best_maxlog]\
                [self.truncated_size//2:,self.analysis.nparams])) 
                # here, j = a_with_best_maxlog
        bestfit = [self.list_of_chains[a_with_best_maxlog][max_index,i] \
                for i in range(self.analysis.nparams)]
        maxlogposterior = self.list_of_chains[a_with_best_maxlog][max_index, 
                self.analysis.nparams]
        maxloglikelihood = self.list_of_chains[a_with_best_maxlog][max_index,
                self.analysis.nparams+1]
        return maxlogposterior, maxloglikelihood, bestfit

    def information_criteria(self, maxll):
        nnuisance = len([par for par in self.analysis.parameters \
                if isinstance(par, cosmo.NuisanceParameter)])
        nBIC = sum([len(dataset.obs) for dataset in self.analysis.datasets.values()])
        AIC = -2 * maxll + 2 * (self.analysis.nparams - nnuisance)
        BIC = -2 * maxll + np.log(nBIC) * (self.analysis.nparams-nnuisance)
        return AIC, BIC

    def load_chains(self, args, stop_at=None): # MCMC
        with click.progressbar(length=len(self.chains), width=10,
                show_pos=True, empty_char='.',
                label=io_tools.fixed_length('Loading chains...'), 
                info_sep=' | ', show_eta=False) as bar:
            list_of_chains = [chain.load_from_file(progress_bar=bar) for chain in self.chains]
        self.truncated_size, self.list_of_chains = io_tools.truncate(list_of_chains,
                stop_at=stop_at)
        maxlogposterior, maxloglikelihood, bestfit = self.find_max_logposterior()
        AIC, BIC = self.information_criteria(maxloglikelihood)
        self.read_conf()
        self.bestfit = self.analysis.prepare_state(bestfit)
        self.conf.set('status', 'best fit', str(self.bestfit))
        self.conf.set('status', 'AIC', "%.2f" % AIC)
        self.conf.set('status', 'BIC', "%.2f" % BIC)
        self.conf_write_to_file()

    def separate_parameters_chains(self, args):
        burn_in = getattr(args, 'burn_in', None)
        return [np.concatenate(
            [chain[burn_in or self.truncated_size//2:,i] \
                    for chain in self.list_of_chains]
            ) for i in range(self.analysis.nparams)]

    def analyze_chains(self, args, stop_at=None): 
        self.load_chains(args, stop_at=stop_at)
        loc = os.path.join(self.working_dir, 'n{0}'.format(self.truncated_size))
        if not os.path.isdir(loc):
            os.mkdir(loc)
        if getattr(args, 'sequences', False):
            self.plot_sequences(args) 
        if getattr(args, 'correlation_function', False):
            self.ACF(args)
        self.processed_chains = self.separate_parameters_chains(args)
        self.fits = self.analysis.prepare_state(
            [st.distributions.norm.fit(chain) for chain in self.processed_chains]
            )
        #derived_parameters
        self.derived_distributions = self.get_derived_distributions()
        self.derived_fits = OrderedDict({})
        for derived in self.derived_distributions.values():
            for label, Omega in zip(derived.label, derived.Omega):
                self.derived_fits[label] = st.distributions.norm.fit(Omega)
        self.read_conf()
        self.conf.set('status', 'parameter fits', str(self.fits))
        self.conf.set('status', 'derived parameter fits', str(self.derived_fits))
        self.conf_write_to_file()
        # sigf, sigd
        kde = getattr(args, 'kde', False)
        if kde:
            print('Saving...', end=' ')
            start_time = time.time()
        self.prepare_data_view_1D(loc, args) 
        self.prepare_data_view_2D(loc, args) 
        if kde:
            print('Done! (in {0})'.format(
                io_tools.printtime(time.time()-start_time)))

        for derived in self.derived_distributions.values():
            delattr(derived, 'Omega')
        with open(os.path.join(loc, 'derived_parameters.p'), 'wb') as dd_file:
            pickle.dump(self.derived_distributions, dd_file, 0)

    def get_V_W_R(self, k, i_k=None, L=None, bar=None):
        nparams = self.analysis.nparams
        nchains = len(self.chains)
        psi_barj_bart = np.array(
                [np.mean([np.mean(self.list_of_chains[j][k//2:k,i]) for j in range(nchains)]
                    ) for i in range(nparams)]
                )
        PW = np.zeros((nparams, nparams))
        PBn = np.zeros((nparams, nparams))
        pbn = 0
        s2, seq_means = [], []
        for j in range(nchains):
            s2.append(np.zeros(nparams))
            psij_bart = np.array(
                    [np.mean(self.list_of_chains[j][k//2:k,i]) for i in range(nparams)]
                    )
            mb = psij_bart - psi_barj_bart
            pbn += mb**2 # not a matrix product
            mb = np.array(mb, ndmin=2)
            PBn += np.dot(mb.transpose(), mb)
            seq_means.append(psij_bart)
            for half_par_chain in self.list_of_chains[j][k//2:k,:]:
                m = np.array(half_par_chain[:nparams]) - psij_bart
                M = np.array(m, ndmin=2)
                PW += np.dot(M.transpose(), M)
                s2[j] += m**2 # not a matrix product
            s2[j] /= k//2 - 1
            if bar:
                bar.update(1)

        w =  np.array(
                [np.mean([s2[j][i] for j in range(nchains)]) for i in range(nparams)]
                )
        W = 1/(nchains*(k//2-1)) * PW
        Bovern = 1/(nchains-1) * PBn
        bovern = 1/(nchains-1) * pbn

        hatV = statistics.estimate_sigma2(k//2, nchains, W, Bovern)
        eigenvalues = np.linalg.eigvals(np.dot(np.linalg.inv(W), hatV))
        try:
            assert np.all(np.isreal(eigenvalues)) or np.all(np.abs(np.imag(eigenvalues)) < 1e-10)
        except AssertionError:
            print(eigenvalues)
            raise AssertionError
        eigenvalues = eigenvalues.real
        hatRp2 = max(eigenvalues)
        hatv = statistics.estimate_sigma2(k//2, nchains, w, bovern)
        hatrp2 = hatv/w

        varv = np.array(
                [statistics.estimate_varV(k//2, nchains, bovern[i], 
                    np.array([S[i] for S in s2]), 
                    np.array([xmean[i] for xmean in seq_means]),
                    psi_barj_bart[i]) for i in range(nparams)]
                )
        df = 2 * np.dot(hatv, hatv) / varv
        hatrp2 *= (df+3)/(df+1)

        res = np.array(
                [k, np.sqrt(hatRp2), math_functions.det(hatV), math_functions.det(W)]
                ), np.array([np.sqrt(hatrp2), hatv, w])
        if L:
            L[i_k] = res
        return res

    def Gelman_Rubin(self, args, last_few=0):
        list_of_k = range(self.truncated_size, 1,
                -self.truncated_size//args.GR_steps)[::-1]
        if list_of_k[0] < (list_of_k[1] - list_of_k[0])//2:
            list_of_k.pop(0)
        list_of_k = list_of_k[-last_few:]

        manager = multiprocessing.Manager()
        monitor_convergence = manager.list(range(len(list_of_k)))
        cpu = multiprocessing.cpu_count()
        if len(list_of_k) <= cpu - 1:
            with click.progressbar(length=len(self.chains), width=10,
                    show_pos=False, empty_char='.',
                    label=io_tools.fixed_length('Monitoring convergence...'),
                    info_sep='  |  ', show_eta=False) as bar:
                jobs = [multiprocessing.Process(
                    target = self.get_V_W_R,
                    args = (k,),
                    kwargs = {'i_k': i_k, 'L': monitor_convergence},
                    ) for i_k, k in enumerate(list_of_k[:-1])]
                # updates progressbar only with the larger run, since all will
                # run together
                jobs.append(multiprocessing.Process(
                    target = self.get_V_W_R,
                    args = (list_of_k[-1],),
                    kwargs = {'i_k': len(list_of_k)-1, 'L': monitor_convergence, 'bar': bar},
                    ))

                for j in jobs:
                    j.start()

                for j in jobs:
                    j.join()

        else:
            with click.progressbar(length=len(list_of_k), width=10,
                    show_pos=False, empty_char='.',
                    label=io_tools.fixed_length('Monitoring convergence...'),
                    info_sep='  |  ', show_eta=False) as bar:
                jobs = [multiprocessing.Process(
                    target = self.get_V_W_R,
                    args = (k,),
                    kwargs = {'i_k': i_k, 'L': monitor_convergence}
                    ) for i_k, k in enumerate(list_of_k)]

                j = 0
                for i in range(len(jobs)//cpu):
                    for job in jobs[j:(i+1)*cpu]:
                        job.start()
                    for job in jobs[j:(i+1)*cpu]:
                        job.join()
                        bar.update(1)
                    j += cpu
                for job in jobs[j:(i+1)*cpu + len(jobs)%cpu]:
                    job.start()
                for job in jobs[j:(i+1)*cpu + len(jobs)%cpu]:
                    job.join()
                    bar.update(1)

        multivariate_results, univariate_results = [], []
        for m_c in monitor_convergence:
            multivariate_results.append(m_c[0])
            univariate_results.append(m_c[1])

        loc = os.path.join(self.working_dir, 'n{0}'.format(self.truncated_size))
        assert self.analysis.nparams > 1
        for i in range(self.analysis.nparams):
            np.savetxt(os.path.join(loc, 'monitor_par{0}.txt'.format(i)),
                    [univariate_results[ik][:,i] for ik, _ in enumerate(list_of_k)],
                    header='hatrp, hatv, w (univariate analysis)')

        np.savetxt(os.path.join(loc, 'monitor_convergence.txt'),
                multivariate_results, 
                header='k, hatRp, |hatV|, |hatW| (multivariate analysis)')
        hatRp_of_k = np.array(multivariate_results)[:,1]
        return list_of_k, hatRp_of_k

    def start(self, args):
        # initialize counters
        total_time = 0
        last_update_N = 0

        # start last few hatRp at 2 to enter loop
        hatRp = 2 * np.ones(args.GR_last)

        # numbers of free random-walk, adaptive loops and
        # number of steps
        free, adapt, adapt_steps = setup_adaption(args)

        # limit size for run
        limit = args.limit or np.inf

        # print Initialization message
        self.inform_start(adapt_steps, free, adapt)

        if adapt:
            self.theta = 0
            self.Sigma = self.proposal_covariance.obtain_Sigma(self.analysis.nparams)

        manager = multiprocessing.Manager()
        self.read_conf()
        self.shared_current_states = manager.list([None for _ in self.chains])
        self.shared_accepted_states_each_chain = manager.list(
                [self.conf['accepted states'].getint(chain.get_id()) \
                        for chain in self.chains]
                )

        # MCMC loops
        while np.any(abs(hatRp-1) > args.tolerance) and last_update_N < limit:
            initial_time = time.time()

            still_adapting_condition = adapt \
                    and free <= self.counter < free + adapt * adapt_steps
            real_Nsteps = 1 if still_adapting_condition else (args.steps if self.counter >= free else adapt_steps)

            if still_adapting_condition:
                # sim_matrix not defined initially, but adapting needs at least
                # one free random-walk loop first anyway
                ##delattr(self.proposal_covariance, 'sim_matrix')
                #edit: not deleting, but instead setting manually after calibration
                pass
            else:
                self.proposal_covariance.sim_matrix = \
                        self.proposal_covariance.get_matrix()

            jobs = [multiprocessing.Process(
                target = self.MetropolisHastings,
                args = (i, real_Nsteps),
                kwargs = {
                    'chi2': args.chi2,
                    'model': self.analysis.model
                    }
                ) for i in range(len(self.chains))]

            for j in jobs:
                j.start()

            for j in jobs:
                j.join()

            self.counter += 1
            iteration_time = time.time() - initial_time
            total_time += iteration_time
            # in adapt, will print only after adapt_steps
            if real_Nsteps > 1 or (real_Nsteps + last_update_N) % adapt_steps == 0:
                print('i {0}, {1} steps, {2} ch; {3}, {4}.'.format(
                    self.counter, real_Nsteps + last_update_N, len(self.chains),
                    io_tools.printtime(
                        iteration_time * (1 if real_Nsteps > 1 else adapt_steps)
                        ), time.ctime()
                    ), end=' ')
            next_check = args.check_interval - total_time
            last_update_N += real_Nsteps

            # updates size of chains and gets acceptance rates
            self.chains_size += real_Nsteps
            acc_rates = np.array(self.shared_accepted_states_each_chain)\
                    /self.chains_size

            # adaptation
            if still_adapting_condition:
                self.proposal_covariance.sim_matrix = self.adapt_covariance(
                        free*(adapt_steps-1) + self.counter,
                        acc_rates) # this also saves to disk 

            self.read_conf()
            self.conf.set('status', 'chains size', str(self.chains_size))
            self.cumulated_time += total_time

            if next_check > 0.5 * iteration_time and last_update_N < limit:
                if real_Nsteps > 1 or last_update_N % adapt_steps == 0:
                    print('Next: ~{0}.'.format(io_tools.printtime(next_check)))
            else:
                print('Checking now...')
                acc_rates = self.remove_bad_chains(list(acc_rates),
                        limits=args.acceptance_limits)
                total_time = 0

                self.analyze_chains(args, stop_at=None)
                _, hatRp = self.Gelman_Rubin(args, last_few=args.GR_last) # burn_in-independent
                print('R-1 tendency: ' + ', '.join(["%.3e" % (R-1) for R in hatRp]))
                self.conf.set('status', 'convergence', str(hatRp[-1]-1))

            self.conf['acceptance rates'] = {}
            self.conf['accepted states'] = {}
            for acc, chain, accepted_states in zip(acc_rates, self.chains,
                    self.shared_accepted_states_each_chain):
                self.conf.set('acceptance rates', chain.get_id(), "%.4f" % acc)
                self.conf.set('accepted states', chain.get_id(),
                        str(accepted_states))

            self.conf.set('status', 'cumulated time', str(self.cumulated_time))
            self.conf.set('status', 'counter', str(self.counter))
            self.conf_write_to_file()

        if self.truncated_size < limit:
            print('Convergence within {0} achieved after {1} steps.'.format(
                "%.2e" % args.tolerance, self.truncated_size))
            self.read_conf()
            self.conf.set('status', 'convergence', '{0} after {1} steps.'.format(
                "%.2e" % args.tolerance, self.truncated_size)
                )
        else:
            print('''Failed to converge within required tolerance ({0}) after {1}
                    steps'''.format("%.2e" % args.tolerance, self.truncated_size)
                    )

class Proposal_Covariance(object):
    def __init__(self, sim, chain=None, beta=1):
        conf = configparser.ConfigParser()
        conf.read(sim.analysis.ini_file)
        sigmas = OrderedDict(eval(conf['simulation']['proposal covariance']))
        self.original_matrix = \
                np.diag([sigmas.get(par.label)**2/beta \
                for par in sim.analysis.parameters])
        self.covariance_file = os.path.join(sim.working_dir, 
            'proposal_covariance.txt') if chain is None \
                    else os.path.join(sim.working_dir, 'proposal_covariance',
                        'chain_{0}.txt'.format(chain))

    def get_matrix(self):
        try:
            return self.sim_matrix
        except AttributeError:
            try:
                return np.loadtxt(self.covariance_file)
            except IOError:
                return self.original_matrix

    def obtain_Sigma(self, n):
        return np.array(self.get_matrix()) * n/5.6644

# generic Chain class object
class Chain(object):
    def __init__(self, wdir, i):
        self.sim_dir = wdir
        self.index = i

    def get_id(self, replace_space=' '):
        return 'chain {0}'.format(self.index).replace(' ', replace_space)

    def get_chain_file(self, obj='chains'):
        return os.path.join(self.sim_dir, obj, "%s.txt" % self.get_id('_'))

    def get_current_state(self):
        return np.loadtxt(self.get_chain_file(obj='current_states'))

    def write_compressed(self, lines):
        with open(self.get_chain_file(), 'a') as f:
            i = 0
            while i < len(lines):
                line = lines[i]
                g = 0
                while i < len(lines) and lines[i] == line:
                    g += 1
                    i += 1
                f.write('\t'.join([str(L) for L in line+[g,]]) + '\n')

        with open(self.get_chain_file(obj='current_states'), 'w') as f:
            f.write('\t'.join([str(L) for L in lines[-1]+[1,]]) + '\n')

    def load_from_file(self, progress_bar=None):
        chain = np.loadtxt(self.get_chain_file())
        chain = io_tools.unzip_chain(chain)
        if progress_bar:
            progress_bar.update(1)
        return chain

# MCMC chain
class MCMC_Chain(Chain):
    pass

def create_new_simulation(args):
    assert os.path.isfile(args.ini)
    assert args.ini.endswith('.ini')
    ini_analysis, working_dir = define_working_directory(args)
    if args.proposal_covariance:
        shutil.copy2(
                args.proposal_covariance,
                os.path.join(working_dir, 'proposal_covariance.txt')
                )
    analysis = load_analysis_from_ini(ini_analysis)
    X0 = define_starting_point(args, analysis)
    io_tools.pasta(working_dir, 'chains')
    io_tools.pasta(working_dir, 'current_states')
    conf_sim = configparser.ConfigParser()
    conf_sim['settings'] = {'mode': args.mode, 'chains': args.chains}
    #if args.mode == 'PT':
    #    io_tools.pasta(working_dir, 'chain_means')
    #    conf_sim.set('settings', 'beta scale', args.beta_scale)
    #    conf_sim.set('settings', 'beta max', str(args.beta_max))
    #    conf_sim.set('settings', 'swap every ~', str(args.swap))
    conf_sim['accepted states'] = {}
    for i in range(args.chains):
        state = [par.prior.rvs() for par in analysis.parameters] if X0 is None else list(X0)
        state.extend([0., 0., 1])
        this_chain = Chain(working_dir, i) 
        with open(this_chain.get_chain_file(), 'w') as f:
            f.write('\t'.join([str(x) for x in state]) + '\n')
        shutil.copy2(
                this_chain.get_chain_file(),
                this_chain.get_chain_file(obj='current_states')
                )
        conf_sim.set('accepted states', this_chain.get_id(), '1')

    conf_sim['status'] = {
            'counter': 0,
            'cumulated time': 0,
            'chains size': 1,
            }
    with open(os.path.join(working_dir, 'simulation_info.ini'), 'w') as f:
        conf_sim.write(f)

    return working_dir, analysis

def load_existing_simulation(working_dir, analysis=None, print_info=True):
    ini_simulation = os.path.join(working_dir, 'simulation_info.ini')
    if analysis is None:
        ini_analysis = os.listdir(working_dir)
        ini_analysis = list(filter(lambda f: f.endswith('.ini'), ini_analysis))
        ini_analysis.remove('simulation_info.ini')
        analysis = load_analysis_from_ini(os.path.join(working_dir, ini_analysis[0]))
    conf_sim = configparser.ConfigParser()
    conf_sim.read(ini_simulation)
    mode = conf_sim['settings']['mode']
    assert mode == 'MCMC'
    sim = MCMC_Simulation(working_dir, analysis, print_info=print_info)
    #else:
    #    assert mode == 'PT'
    #    sim = PT_Simulation(working_dir, analysis)
    if print_info:
        print('The following datasets will be used:')
        for dataset in sorted(sim.analysis.datasets):
            print('    {0}'.format(dataset))
    return sim

def define_starting_point(args, analysis):
    if args.starting_point:
        diff_params = len(args.starting_point) - analysis.nparams
        if diff_params < 0:
            raise Exception(
                    'Values for {0} free parameters missing in given starting point.'\
                            .format(-diff_params)
                    )
        elif diff_params > 0:
            raise Exception(
                    '{0} extra values of free parameters in the given starting point.'\
                            .format(diff_params)
                    )
        return args.starting_point
    elif args.multi_start:
        return None
    else:
        return [par.default for par in analysis.parameters]

def define_working_directory(args):
    altdir = args.alt_dir or open('altdir.txt', 'r').readline().strip()
    hora = args.sim_full_name or io_tools.define_time()
    if args.sim_tag:
        hora = '-'.join([args.sim_tag, hora])
    parent_dir = os.path.join(altdir, args.ini.replace('.ini', ''))
    if not os.path.isdir(parent_dir):
        os.mkdir(parent_dir)
    working_dir = os.path.join(parent_dir, hora)
    assert not os.path.isdir(working_dir)
    os.mkdir(working_dir)
    shutil.copy2(args.ini, working_dir)
    ini_file = os.path.join(working_dir, args.ini)
    return ini_file, working_dir

def load_analysis_from_ini(ini_file):
    ini = configparser.ConfigParser()
    ini.read(ini_file)
    cosmology_model = cosmo.CosmologicalSetup(
            ini['model']['type'],
            optional_species=eval(ini['model'].get('optional species', '[]')),
            combined_species=eval(ini['model'].get('combined species', '[]')),
            interaction_setup=eval(ini['model'].get('interaction setup', '{}')),
            physical=ini['model'].getboolean('physical', True),
            derived=ini['model'].get('derived', None),
            a0=ini['model'].getfloat('a0', 1),
            )

    datasets = eval(ini['analysis']['datasets'])
    prior_ranges = eval(ini['analysis']['priors'])
    prior_distributions = eval(ini['analysis'].get('prior distributions') or '{}')
    split = eval(ini['analysis'].get('split') or '{}')
    fixed_parameters = eval(ini['analysis'].get('fixed') or '{}')
    datasets = observations.choose_from_datasets(datasets)

    analysis = statistics.Analysis(datasets, cosmology_model, prior_ranges,
            prior_distributions=prior_distributions, split=split,
            fixed=fixed_parameters)
    analysis.ini_file = ini_file
    return analysis

def build_stored_line(X, *args):
    X = list(X)
    for arg in args:
        X.append(arg)
    return X

def load_plt(args):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt

    # wether to use tex in plots
    use_tex = getattr(args, 'use_tex', False)

    if use_tex:
        #plt.rc('font',**{'family':'serif','serif':['cmr10']}) # 'Times'
        #plt.rcParams['text.latex.preamble'] = [r'\usepackage{amsmath}',
        #        r'\usepackage{siunitx}']
        plt.rc('text', usetex=True)

    plt.rcParams['axes.linewidth'] = 0.5
    #plt.rcParams['text.latex.unicode'] = True
    #plt.rcParams['font.serif'] = 'Palatino'
    #plt.rcParams['legend.fontsize'] = 'medium'
    plt.rcParams['xtick.top'] = True
    plt.rcParams['ytick.right'] = True
    plt.rcParams['xtick.direction'] = 'in'
    plt.rcParams['ytick.direction'] = 'in'
    plt.rcParams['xtick.major.width'] = 0.5
    plt.rcParams['ytick.major.width'] = 0.5

    return plt

def setup_adaption(args):
    try:
        return args.adapt[:3]
    except (ValueError, TypeError):
        try:
            free, adapt = args.adapt[:2]
        except (ValueError, TypeError):
            free = args.adapt
            adapt = int(free)
        adapt_steps = args.steps
        return free, adapt, adapt_steps

def line_to_state(line, nparams):
    Xt = line[:nparams]
    lpXt, llXt = line[nparams:]
    return Xt, lpXt, llXt

