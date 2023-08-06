import numpy as np
import os
from collections import OrderedDict
import configparser
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import itertools
from EPIC import root
from EPIC.cosmology import cosmic_objects as cosmo
from EPIC.utils import data_tools, io_tools
from EPIC.utils.math_functions import normalize, draw_ellipse
from EPIC.utils.statistics import scipy_stats_standard_normal
from EPIC.utils.statistics import CL_excluding_value_kde
try:
    import cPickle as pickle
except ImportError:
    import pickle

# alphas_lighter = [0.40, 0.25, 0.11, ...]
def al_fit(x):
    return 0.739313 * np.exp(-0.596639*x)

# alphas_darker = [0.70, 0.35, 0.15, ...]
def ad_fit(x):
    return 1.46183 * np.exp(-0.73224*x)

class Histogram(object):
    def __init__(self, par, color, count, seps, normalization, bestfit,
            sigma_up):
        self.par = par
        self.color = color
        self.count = count
        self.separators = seps
        self.norm = normalization
        self.bestfit = bestfit
        self.sigma_up = sigma_up

def mark_sigmas(ax, gauss_pars, X, mhist, newlims, levels=[1, 2]):
    mu, sigma = gauss_pars
    for level in levels:
        ax.axvline(mu - level * sigma, ls='--', lw=0.3, color='b')
        ax.axvline(mu + level * sigma, ls='--', lw=0.3, color='b')
    normalized_fit_curve = normalize(
            1/mhist * scipy_stats_standard_normal.pdf((X-mu)/sigma) \
                    *1/sigma, (0, 1), newlims=newlims
                    )
    return normalized_fit_curve

def preparehistogram(loc, H, b, w, vmin, vmax, parname, mhist=None,
        crange=False, kde=False):
    if mhist:
        if crange:
            h = normalize(H, (0, mhist), newlims=crange)
        else:
            h = normalize(H, (0, mhist), newlims=(vmin, vmax))
    else:
        h = H

    if kde:
        x = np.loadtxt(os.path.join(loc, 'kde', 'ksupport_%s.txt' % parname))
        y = np.loadtxt(os.path.join(loc, 'kde', 'kdensity_%s.txt' % parname))
        if mhist:
            if crange:
                y = normalize(y, (0, mhist), newlims=crange)
            else:
                y = normalize(y, (0, mhist), newlims=(vmin, vmax))
        else:
            pass

    else:
        x = None
        y = None

    hx = np.ravel(list(zip(b[:-1], b[:-1]+w)))
    hy = np.ravel(list(zip(h, h)))
    hx = np.concatenate(([hx[0]], hx, [hx[-1]]))
    hy = np.concatenate(([vmin], hy, [vmin]))

    return x, y, hx, hy
        
def make_plots(list_of_sims, args=None):

    labelsize = plt.rcParams['axes.labelsize']
    plt.style.use(getattr(args, 'style', 'default'))
    plt.rcParams['axes.labelsize'] = labelsize

    plt.rcParams['figure.frameon'] = True
    plt.rcParams['axes.linewidth'] = 0.5
    #plt.rcParams['text.latex.unicode'] = True
    plt.rcParams['legend.fontsize'] = 'small'
    plt.rcParams['xtick.top'] = True
    plt.rcParams['ytick.right'] = True
    plt.rcParams['xtick.direction'] = 'in'
    plt.rcParams['ytick.direction'] = 'in'
    plt.rcParams['xtick.major.width'] = 0.5
    plt.rcParams['ytick.major.width'] = 0.5

    plt.rcParams['axes.grid'] = False
    plt.rcParams['axes.edgecolor'] = plt.rcParams['axes.labelcolor']
    plt.rcParams['xtick.color'] = plt.rcParams['axes.edgecolor']
    plt.rcParams['ytick.color'] = plt.rcParams['axes.edgecolor']

    if args is not None:
        try:
            plt.rcParams['font.size'] = args.font_size
            if args.use_tex:
                font_preamble = io_tools.tex_packages(
                        io_tools.pdf_fonts[args.font])
                plt.rcParams['text.latex.preamble'] = font_preamble
            plt.rc('text', usetex=args.use_tex)
        except AttributeError:
            pass
        exclude = getattr(args, 'exclude', None)
        if exclude:
            for sim in list_of_sims:
                sim.analysis.parameters = [par for par in sim.analysis.parameters \
                        if par.label not in exclude]
                if 'nuisance' in exclude:
                    sim.analysis.parameters = [par for par in sim.analysis.parameters \
                            if not isinstance(par, cosmo.NuisanceParameter)]
                sim.analysis.parnames = [par.label for par in sim.analysis.parameters]
                sim.analysis.nparams = len(sim.analysis.parnames)

    list_hist_properties = generate_data_view_1D(list_of_sims, args=args)
    nparams = max([sim.analysis.nparams for sim in list_of_sims])
    grid, subplots = plt.subplots(nparams, nparams, sharex='col', sharey='row')
    if nparams == 1:
        subplots = [[subplots,],]
    saved_hist = generate_data_view_2D(grid, subplots, list_hist_properties,
            list_of_sims, args=args)

    separate_figs=[[plt.subplots() if i<=j else (None, None) \
            for i in range(nparams)] for j in range(nparams)]
    generate_data_view_2D(
            [[fig[0] for fig in sep_fig] for sep_fig in separate_figs],
            [[fig[1] for fig in sep_fig] for sep_fig in separate_figs],
            list_hist_properties, list_of_sims, args=args
            )

    if saved_hist:
        print('Saved {0}'.format(saved_hist))

def get_auto_factors(sim):
    def int_factor(x):
        return int(np.ceil(-np.log10(x)))

    factors = {}
    parameters = [par.label for par \
            in sim.analysis.parameters + sim.analysis.derived_parameters]
    for derived in sim.derived_distributions.values():
        for label in derived.label:
            if label not in parameters:
                parameters.append(label)
    for label in parameters:
        try:
            mu, sig = sim.fits[label]
        except KeyError:
            mu, sig = sim.derived_fits[label]
        factor = min(
                int_factor(abs(mu)),
                int_factor(sig/abs(mu))
                )
        if abs(factor) != 1:
            factors[label] = factor
    return factors

def get_auto_ranges(list_of_sims, list_hist_properties):
    ranges = dict(((par.label, (np.inf, -np.inf)) for par \
            in list_of_sims[0].analysis.parameters))

    for sim in list_of_sims:
        for par in sim.analysis.parameters:
            if hasattr(sim, 'fits'):
                mu, sigma = sim.fits[par.label]
                ranges[par.label] = min(ranges[par.label][0],
                        max(par.prior.vmin, mu - 3.5 * sigma)), \
                                max(ranges[par.label][1], min(par.prior.vmax,
                                    mu + 3.5 * sigma))
    return ranges

def divide_range(lims, n=3):
    x1, x2 = lims
    imarg = (x2 - x1)/3/2
    return lims, np.linspace(x1+imarg, x2-imarg, num=n)

def process_ticks(customrange, customfactors, units, par, lim=None):
    try:
        label = par.label
        tex = par.tex
    except AttributeError:
        label, tex = par
    par_tex, log10factor = format_factor_parameter(label, tex, customfactors, units=units)
    if customrange and label in customrange:
        lims, ticks = divide_range(customrange[label])
    else:
        if lim is None:
            lims, ticks = divide_range([par.prior.vmin, par.prior.vmax])
        else:
            lims, ticks = divide_range(lim)
    precision, ticks = reprocess_ticks(ticks, log10factor)

    if log10factor is None:
        ticklabels = [r'$%s$' % x.__format__('.%ig' % precision) for x in ticks]
    else:
        ticklabels = [r'$%s$' % x.__format__('.%ig' % precision) for x in ticks \
                * eval('1e%i' % log10factor)]
    axis_label = r'$' + par_tex + '$'

    return lims, ticks, ticklabels, axis_label

def reprocess_ticks(ticks, log10factor=0):
    precision = abs(int(round(-np.log10(np.diff(ticks * 10**(log10factor or 0))[0])))) + 2
    return precision, np.array([float(x.__format__('.%sg' % precision)) \
            for x in ticks])

def generate_data_view_2D(grid, subplots, list_hist_properties,
        list_of_sims, kde=False, show_hist=False, show_gaussian_fit=False,
        mark_best_fit=True, png=False, levels=[1, 2], single_color='C0',
        color_scheme='tableau', group_name=None, no_auto_factors=False,
        no_custom_ticks=False, no_auto_range=False, no_units=False,
        stop_at=None, UseTex=False, args=None):
    kde = getattr(args, 'kde', kde)
    show_hist = getattr(args, 'show_hist', show_hist)
    show_gaussian_fit = getattr(args, 'show_gaussian_fits', show_gaussian_fit)
    mark_best_fit = getattr(args, 'mark_best_fit', mark_best_fit)
    png = getattr(args, 'png', png)
    levels = getattr(args, 'levels', levels)
    gname = getattr(args, 'group_name', group_name)
    no_auto_factors = getattr(args, 'no_auto_factors', no_auto_factors)
    no_custom_ticks = getattr(args, 'no_custom_ticks', no_custom_ticks)
    no_auto_range = getattr(args, 'no_auto_range', no_auto_range)
    no_units = getattr(args, 'no_units', no_units)
    stop_at = getattr(args, 'stop_at', stop_at)
    single_color = [getattr(args, 'color', single_color),]
    color_scheme = getattr(args, 'color_scheme', color_scheme)
    color_scheme = get_color_names(color_scheme)

    # loads custom configuration from first ini
    ini = configparser.ConfigParser()
    ini.read(list_of_sims[0].analysis.ini_file)
    customticks = {} if no_custom_ticks else \
            eval(ini['simulation'].get('custom ticks', '{}'))
    customfactors = eval(ini['simulation'].get('custom factors', 'None'))
    if customfactors is None:
        customfactors = {} if no_auto_factors \
                else get_auto_factors(list_of_sims[0])
    customrange = {} if no_auto_range else \
            eval(ini['simulation'].get('custom range', 'None'))
    if customrange is None:
        customrange = get_auto_ranges(list_of_sims, list_hist_properties)
    default_units = configparser.ConfigParser()
    default_units.read([
        os.path.join(root, 'cosmology', 'default_parameter_units.ini'),
        os.path.join(root, 'modifications', 'cosmology',
            'default_parameter_units.ini'),
        ])
    default_units_dict = {}
    for par in list_of_sims[0].analysis.parameters:
        if par.label in default_units['DEFAULT']:
            default_units_dict[par.label] = io_tools.parse_unit(default_units['DEFAULT'][par.label])
    units = {} if no_units else eval(ini['simulation'].get('units', 'default_units_dict'))

    def load_txt_from(prefix, wdir, sim, jx, jy):
        return np.loadtxt(os.path.join(wdir, '%s_%s_%s.txt' % (prefix,
            sim.analysis.parameters[jx].label,
            sim.analysis.parameters[jy].label)
            ))

    xalpha = np.linspace(1, 3, max(3, len(levels)))
    alphas = al_fit(xalpha) if len(list_of_sims) > 1 else ad_fit(xalpha)

    superposalpha = 1 # min(1, sum(alphas[:len(levels)]))
    
    ticklabels = {}
    axis_label = {}

    nparams = list_of_sims[0].analysis.nparams # so, the largest one should be the first
    for i in range(nparams*nparams):
        jx, jy = divmod(i, nparams)
        if jx > jy: 
            mcolor = itertools.cycle(color_scheme if len(list_of_sims) > 1 \
                    else single_color)
            for sim, hist_properties in zip(list_of_sims,
                    list_hist_properties):
                try:
                    mcor = next(mcolor)
                    loc = sim.plot_location(stop_at=stop_at)
                    H = load_txt_from('H', loc, sim, jx, jy)
                    #seps = load_txt_from('seps', loc, sim, jx, jy)
                    xedg = load_txt_from('xedg', loc, sim, jx, jy)
                    yedg = load_txt_from('yedg', loc, sim, jx, jy)
                    sigmalevels, H = data_tools.sigmalevels_2D(H, xedg, yedg, levels=levels)
                    hrange = load_txt_from('hrange', loc, sim, jx, jy)
                    # contorno:
                    if kde:
                        kde_loc = os.path.join(loc, 'kde')
                        kde_hrange = load_txt_from('kdensity2_hrange', kde_loc,
                                sim, jx, jy)
                        kde_H = load_txt_from('kdensity2', kde_loc, sim, jx, jy)
                        kde_xsupport = load_txt_from('kdensity2_xsupport',
                                kde_loc, sim, jx, jy) 
                        kde_ysupport = load_txt_from('kdensity2_ysupport',
                                kde_loc, sim, jx, jy) 
                        kde_sigmalevels, kde_H = data_tools.sigmalevels_2D(
                                kde_H, kde_xsupport, kde_ysupport, levels=levels)

                    if len(list_of_sims) > 1:
                        if kde:
                            subplots[jx][jy].contour(kde_H.transpose(),
                                    levels=kde_sigmalevels[::-1],
                                    extent=kde_hrange.flatten(),
                                    colors=mcor, linewidths=0.5,
                                    linestyles=['solid', 'solid'])
                            if show_hist:
                                subplots[jx][jy].contour(H.transpose(),
                                        levels=sigmalevels[::-1],
                                        extent=hrange.flatten(),
                                        colors=mcor, linewidths=0.5,
                                        linestyles=['dotted', 'dotted'])
                        else:
                            subplots[jx][jy].contour(H.transpose(),
                                    levels=sigmalevels[::-1],
                                    extent=hrange.flatten(), colors=mcor,
                                    linewidths=0.5, linestyles=['solid',
                                        'solid'])

                    if kde:
                        for il in range(len(kde_sigmalevels)):
                            subplots[jx][jy].contourf(kde_H.transpose(),
                                    levels=np.concatenate([kde_sigmalevels[::-1][-(il+1):],[np.inf]]),
                                    extent=kde_hrange.flatten(),
                                    colors=mcor, alpha=alphas[il]) 
                        if show_hist:
                            subplots[jx][jy].contour(H.transpose(),
                                    levels=sigmalevels[::-1],
                                    extent=hrange.flatten(), colors='k',
                                    linewidths=0.5, linestyles=['dotted',
                                        'dotted']) 
                    else:
                        for il in range(len(sigmalevels)):
                            subplots[jx][jy].contourf(H.transpose(),
                                    levels=np.concatenate([sigmalevels[::-1][-(il+1):],[np.inf]]),
                                    extent=hrange.flatten(), colors=mcor,
                                    alpha=alphas[il]) # fill onesigma

                    if show_gaussian_fit:
                        corr_xy = float(load_txt_from('corr_xy', loc, sim,
                            jx, jy))
                        mux, sx = sim.fits[sim.analysis.parameters[jx].label]
                        muy, sy = sim.fits[sim.analysis.parameters[jy].label]
                        sigxy2 = corr_xy * sx * sy
                        IF = np.array([[sx**2, sigxy2], [sigxy2, sy**2]])
                        for level in levels:
                            thx, thy = draw_ellipse(IF, (mux, muy), CLsigma=level)
                            subplots[jx][jy].plot(thy, thx, ls='-',
                                    color=plt.rcParams['axes.labelcolor'],
                                    lw=0.3)
                except (IOError, ValueError, IndexError):
                    pass

                if mark_best_fit:
                    try:
                        bfx, bfy = hist_properties[sim.analysis.parameters[jy].label].bestfit, \
                                hist_properties[sim.analysis.parameters[jx].label].bestfit
                        bfmark_color = mcor if len(list_of_sims) > 1 \
                                else (0.6, 0.6, 0.6)
                        subplots[jx][jy].plot(bfx, bfy, markersize=5, marker='+',
                                markeredgecolor=plt.rcParams['figure.facecolor'],
                                mfc=plt.rcParams['figure.facecolor'],
                                markeredgewidth=0.5) # mcor
                        subplots[jx][jy].axhline(bfy, linestyle='-', lw=0.3, color=bfmark_color)
                        subplots[jx][jy].axvline(bfx, linestyle='-', lw=0.3, color=bfmark_color)
                    except (KeyError, IndexError):
                        pass

            subplots[jx][jy].tick_params(size=3)

            try:
                par_jx = sim.analysis.parameters[jx].label
                par_jy = sim.analysis.parameters[jy].label
            except IndexError:
                par_jx = list_of_sims[0].analysis.parameters[jx].label
                par_jy = list_of_sims[0].analysis.parameters[jy].label

            x_lim, x_ticks, tlabels, ax_label = process_ticks(customrange,
                    customfactors, units, list_of_sims[0].analysis.parameters[jy])
            ticklabels[par_jy] = tlabels
            axis_label[par_jy] = ax_label
            subplots[jx][jy].set_xlim(x_lim)
            subplots[jx][jy].set_xticks(x_ticks)
            
            if par_jy in customticks:
                subplots[jx][jy].set_xticks(customticks[par_jy])
                    
            y_lim, y_ticks, tlabels, ax_label = process_ticks(customrange,
                    customfactors, units, list_of_sims[0].analysis.parameters[jx])
            ticklabels[par_jx] = tlabels
            axis_label[par_jx] = ax_label
            subplots[jx][jy].set_ylim(y_lim)
            subplots[jx][jy].set_yticks(y_ticks)

            if par_jx in customticks:
                subplots[jx][jy].set_yticks(customticks[par_jx])

        elif jx < jy:
            if not isinstance(grid, list):
                grid.delaxes(subplots[jx][jy])
        else: # jx == jy
            comboH, combob, combow = {}, {}, {}
            notallwdir = []
            for sim in list_of_sims:
                loc = sim.plot_location(stop_at=stop_at)
                try:
                    comboH[loc] = np.loadtxt(os.path.join(loc, 'combo_count_%s.txt' % sim.analysis.parameters[jx].label))
                    combob[loc] = np.loadtxt(os.path.join(loc, 'combo_seps_%s.txt' % sim.analysis.parameters[jx].label))
                    combow[loc] = np.loadtxt(os.path.join(loc, 'combo_widths_%s.txt' % sim.analysis.parameters[jx].label))
                    notallwdir.append(loc)
                except (IOError, IndexError):
                    pass
            sim = list_of_sims[0]
            if kde:
                mhist = 1.15*max([np.loadtxt(os.path.join(loc, 'kde', 'kdensity_%s.txt' % sim.analysis.parameters[jx].label)).max() for loc in notallwdir])
            else:
                mhist = 1.15*max([comboH[loc].max() for loc in notallwdir])
            #print(len(notallwdir), len(list_hist_properties))
            #assert len(notallwdir) == len(list_hist_properties)
            for loc, hist_properties in zip(notallwdir, list_hist_properties):
                pmin, pmax = sim.analysis.parameters[jx].prior.vmin, \
                        sim.analysis.parameters[jx].prior.vmax
                x, y, hx, hy = preparehistogram(loc, comboH[loc], combob[loc],
                        combow[loc], pmin, pmax,
                        sim.analysis.parameters[jx].label, mhist,
                        customrange and sim.analysis.parameters[jx].label in customrange \
                                and customrange[sim.analysis.parameters[jx].label],
                                kde=kde and loc)
                fy = (x, y) if kde else False

                if len(list_of_sims) > 1:
                    if kde:
                        subplots[jx][jy].plot(x, y, lw=1., ls='-',
                                color=hist_properties[sim.analysis.parameters[jx].label].color)
                        if show_hist:
                            subplots[jx][jy].plot(hx, hy, lw=0.3, ls='-',
                                    color=hist_properties[sim.analysis.parameters[jx].label].color)
                    else:
                        subplots[jx][jy].plot(hx, hy, lw=1, ls='-',
                                color=hist_properties[sim.analysis.parameters[jx].label].color)
                else:
                    if kde:
                        subplots[jx][jy].plot(x, y, lw=1.5, ls='-', color=plt.rcParams['axes.labelcolor'])#hist_properties[sim.analysis.parameters[jx].label].color)
                        if show_hist:
                            subplots[jx][jy].plot(hx, hy, lw=0.3, ls='-', color=plt.rcParams['axes.labelcolor'])#hist_properties[sim.analysis.parameters[jx].label].color)
                    else:
                        subplots[jx][jy].plot(hx, hy, lw=1.5, ls='-', color=plt.rcParams['axes.labelcolor'])#hist_properties[sim.analysis.parameters[jx].label].color)

                if show_gaussian_fit:
                    X = np.linspace(hx[0], hx[-1], num=300)
                    newlims = customrange.get(sim.analysis.parameters[jx].label,
                            (
                                sim.analysis.parameters[jx].prior.vmin,
                                sim.analysis.parameters[jx].prior.vmax)
                            )
                    normalized_fit_curve = mark_sigmas(subplots[jx][jy], sim.fits[sim.analysis.parameters[jx].label], X, mhist, newlims, levels=levels)
                    subplots[jx][jy].plot(X, normalized_fit_curve, lw=0.8, color='b')

                draw_on_axes(len(list_of_sims),
                        customfactors, subplots[jx][jy], kde and fy,
                        hist_properties[sim.analysis.parameters[jx].label],
                        title_above=not isinstance(grid, list), MHIST=mhist,
                        CRANGE=customrange and \
                                customrange.get(sim.analysis.parameters[jx].label,
                                    False), levels=levels,
                        args=args)
            #subplots[jx][jy].tick_params(size=3)

    sim = list_of_sims[0]

    for j in range(nparams):
        if isinstance(grid, list) or j == nparams-1:
            lastrowpar = sim.analysis.parameters[j]
            x_lim, x_ticks, tlabels, ax_label = process_ticks(customrange,
                    customfactors, units, lastrowpar)
            ticklabels[lastrowpar.label] = tlabels
            axis_label[lastrowpar.label] = ax_label
            subplots[j][j].set_xlim(x_lim)
            subplots[j][j].set_xticks(x_ticks)

            if lastrowpar.label in customticks:
                subplots[j][j].set_xticks(customticks[lastrowpar.label])

    for j in range(nparams):
        if isinstance(grid, list) or j == 0:
            firstcolumnpar = sim.analysis.parameters[j]
            if customrange and firstcolumnpar.label in customrange:
                subplots[j][j].set_ylim(customrange[firstcolumnpar.label])
            else:
                subplots[j][j].set_ylim(
                        firstcolumnpar.prior.vmin,
                        firstcolumnpar.prior.vmax)

    for i in range(nparams*nparams):
        jx, jy = divmod(i, nparams)
        par = sim.analysis.parameters[jy]
        if jx >= jy and (isinstance(grid, list) or jx == nparams-1):
            subplots[jx][jy].set_xticklabels(ticklabels[par.label])
            subplots[jx][jy].set_xlabel(axis_label[par.label])
            
    # different range from above
    for i in range(0,nparams*nparams):
        jx, jy = divmod(i, nparams)
        par = sim.analysis.parameters[jx]
        if jx > jy and (isinstance(grid, list) or jy == 0):
            subplots[jx][jy].set_yticklabels(ticklabels[par.label])
            subplots[jx][jy].set_ylabel(axis_label[par.label])

    for i in range(nparams):
        if isinstance(grid, list) or i == 0:
            subplots[i][i].set_yticklabels('')

    if len(list_of_sims) > 1 and not isinstance(grid, list):
        mcolor = itertools.cycle(color_scheme)
        legs = []
        for sim in list_of_sims:
            lbl = sim.analysis.get_label()
            legs.append(mpatches.Patch(color=next(mcolor), alpha=superposalpha,
                linewidth=1, label=lbl))
        grid.legend(title=sim.analysis.model.model, handles=legs,
                frameon=False, borderaxespad=0.5, handletextpad=0.8,
                loc='upper right')

    sim = list_of_sims[0]
    loc = sim.plot_location(stop_at=stop_at)
    if isinstance(grid, list):
        if len(list_of_sims) > 1 and not gname:
            while not gname:
                gname = input('Custom common prefix for separated pdf files: ')

        if not gname:
            gname = 'grids2s'

        for i in range(nparams*nparams):
            jx, jy = divmod(i, nparams)
            if jx >= jy:
                grid[jx][jy].set_size_inches(2. if jx > jy else 1.8, 2.)
                grid[jx][jy].tight_layout()

                grid[jx][jy].savefig(os.path.join(loc, 
                    gname + '-' + '-'.join([sim.analysis.parameters[jx].label,
                        sim.analysis.parameters[jy].label])+ '.pdf'))
                if png:
                    grid[jx][jy].savefig(os.path.join(loc,
                        gname + '-' + '-'.join([sim.analysis.parameters[jx].label,
                            sim.analysis.parameters[jy].label])+ '.png'), dpi=360)
            else:
                pass

    else:
        grid.set_size_inches(nparams*1.6, nparams*1.6)
        grid.tight_layout()

        #grid.subplots_adjust(top=toppos)
        #grid.subplots_adjust(left=lateral)
        #grid.subplots_adjust(right=1-lateral)
        grid.subplots_adjust(hspace=0)
        grid.subplots_adjust(wspace=0)
        grid.align_labels()

        if len(list_of_sims) > 1 and not gname:
            while not gname:
                gname = input('Custom name for pdf file: ')

        if not gname:
            gname = 'grids2s'

        grid.savefig(os.path.join(loc, '%s.pdf' % gname))
        if png:
            grid.savefig(os.path.join(loc, '%s.png' % gname), dpi=360)

    args.title_above = False
    plt.rcParams['figure.max_open_warning'] = len(sim.derived_distributions) + sim.analysis.nparams**2
    for par in sim.derived_distributions.values():
        for label, tex in zip(par.label, par.tex):
            fig, ax = plt.subplots()
            comboH, combob, combow = {}, {}, {}
            notallwdir = []
            for sim in list_of_sims:
                loc = sim.plot_location(stop_at=stop_at)
                try:
                    comboH[loc] = np.loadtxt(os.path.join(loc, 'combo_count_%s.txt' % label))
                    combob[loc] = np.loadtxt(os.path.join(loc, 'combo_seps_%s.txt' % label))
                    combow[loc] = np.loadtxt(os.path.join(loc, 'combo_widths_%s.txt' % label))
                    notallwdir.append(loc)
                except (IOError, IndexError):
                    pass

            sim = list_of_sims[0]
            if kde:
                mhist = 1.15*max([np.loadtxt(os.path.join(loc, 'kde', 'kdensity_%s.txt' % label)).max() for loc in notallwdir])
            else:
                mhist = 1.15*max([comboH[loc].max() for loc in notallwdir])

            pmin = min([combob[loc][0] - 0.15*(combob[loc][-1] - combob[loc][0]) for loc in notallwdir])
            pmax = max([combob[loc][-1] + 0.15*(combob[loc][-1] - combob[loc][0]) for loc in notallwdir])
            if label in customrange:
                xyvmin, xyvmax = customrange[label]
            else:
                xyvmin, xyvmax = pmin, pmax
            for loc, hist_properties in zip(notallwdir, list_hist_properties):
                x, y, hx, hy = preparehistogram(loc, comboH[loc], combob[loc],
                        combow[loc], xyvmin, xyvmax, label, mhist,
                        customrange and customrange.get(label, False),
                        kde=kde and loc)
                fy = (x, y) if kde else False
                hist_properties[label].pmin = pmin
                hist_properties[label].pmax = pmax

                if len(list_of_sims) > 1:
                    if kde:
                        ax.plot(x, y, lw=1., ls='-',
                                color=hist_properties[label].color)
                        if show_hist:
                            ax.plot(hx, hy, lw=0.3, ls='-', 
                                    color=hist_properties[label].color)
                    else:
                        ax.plot(hx, hy, lw=1, ls='-',
                                color=hist_properties[label].color)
                else:
                    if kde:
                        ax.plot(x, y, lw=1.5, ls='-', color=plt.rcParams['axes.labelcolor'])
                        if show_hist:
                            ax.plot(hx, hy, lw=0.3, ls='-', color=plt.rcParams['axes.labelcolor'])
                    else:
                        ax.plot(hx, hy, lw=1.5, ls='-', color=plt.rcParams['axes.labelcolor'])

                if show_gaussian_fit:
                    X = np.linspace(hx[0], hx[-1], num=300)
                    newlims = customrange.get(label, (xyvmin, xyvmax))
                    normalized_fit_curve = mark_sigmas(ax,
                            sim.derived_fits[label],
                            X, mhist, newlims, levels=levels)
                    ax.plot(X, normalized_fit_curve, lw=0.8, color='b')

                draw_on_axes(len(list_of_sims), customfactors, ax, 
                        kde and fy, hist_properties[label], MHIST=mhist,
                        CRANGE=(xyvmin, xyvmax), levels=levels,
                        args=args)

                lims, ticks, tlabels, ax_label = process_ticks(customrange,
                        customfactors, units, (label, tex), lim=[xyvmin, xyvmax])
                ax.set_xlim(*lims)
                ax.set_xticks(ticks)
                ax.set_xticklabels(tlabels)
                ax.set_xlabel(ax_label)

                if label in customticks:
                    ax.set_xticks(customticks[label])

                ax.set_ylim(*lims)
                ax.set_yticklabels('')

            loc = notallwdir[0]
            fig.set_size_inches(2, 2)
            fig.tight_layout()
            fig.savefig(os.path.join(loc, 'dist_%s.pdf' % label))
            if png:
                fig.savefig(os.path.join(loc, 'dist_%s.png' % label), dpi=360)
            plt.close(fig)


def draw_on_axes(len_list_analyses, customfactors, ax, kde,
        hist_properties, title_above=True, MHIST=None, CRANGE=False,
        levels=[1, 2], mark_best_fit=True, title_pos='upper right',
        font_size=8, args=None):

    title_above = getattr(args, 'title_above', title_above)
    title_pos = getattr(args, 'title_pos', title_pos)
    mark_best_fit = getattr(args, 'mark_best_fit', mark_best_fit)
    font_size = getattr(args, 'font_size', font_size)
    levels = getattr(args, 'levels', levels)

    try:
        vmin = hist_properties.par.prior.vmin
        vmax = hist_properties.par.prior.vmax
    except AttributeError:
        vmin = hist_properties.pmin
        vmax = hist_properties.pmax

    fcolor = hist_properties.color
    xalpha = np.linspace(1, 3, max(3, len(levels)))
    alphas = al_fit(xalpha) if len_list_analyses > 1 else ad_fit(xalpha)
    nrange = CRANGE or (vmin, vmax)
    dx = (hist_properties.separators[-1] - hist_properties.separators[0]) \
            / (hist_properties.separators.size-1)

    def HIST(X, mhist):
        d, m = divmod(X - hist_properties.separators[0], dx)
        i = int(round(d))
        try:
            c = hist_properties.count[i]/hist_properties.norm
        except IndexError:
            assert i == len(hist_properties.count)
            c = hist_properties.count[i-1]/hist_properties.norm
        if not mhist:
            mhist = max(hist_properties.count)*1.15
        return normalize(c, (0, mhist), newlims=nrange)
        
    if len_list_analyses == 1:
        if kde:
            x, Hx = kde
        else:
            x = np.linspace(hist_properties.separators[0],
                    hist_properties.separators[-1], num=400)
            Hx = np.array([HIST(X,MHIST) for X in x])

        for sigma_up, alpha in zip(hist_properties.sigma_up, alphas):
            sigma_lim = normalize(sigma_up/hist_properties.norm, (0, MHIST),
                    newlims=nrange)
            shadedregion = np.where(Hx > sigma_lim, True, False)
            ax.fill_between(x, vmin, Hx,
                    where=shadedregion, facecolor=fcolor, linewidth=0.0,
                    alpha=alpha) # 0 -> hist_properties.vmin

        if mark_best_fit:
            h1 = ax.axvline(hist_properties.bestfit, linestyle='-', lw=0.3, color=(0.6, 0.6, 0.6))
        ax.set_xlim(vmin, vmax) 
        ax.set_xticks(np.linspace(vmin, vmax, num=4))
    else:
        if mark_best_fit:
            h1 = ax.axvline(hist_properties.bestfit, linestyle='-', lw=0.3,
                    color=fcolor)
        else:
            pass

    #ym, yM = ax.get_ylim()
    #ax.set_yticks(np.linspace(ym,yM, num=5))
    ax.tick_params(left=False, right=False)

    formatted_title = format_title(hist_properties.par, customfactors)
    if title_above:
        ax.set_title(formatted_title, fontdict={'fontsize': font_size},
                color=plt.rcParams['axes.labelcolor'])
    else:
        # title inside
        invisible_handle = mpatches.Patch(linewidth=0, label=formatted_title)
        ax.legend(loc=title_pos, handles=[invisible_handle,], frameon=False,
                borderaxespad=0.5, handlelength=0, handletextpad=0)

def generate_data_view_1D(list_of_sims, kde=False, fmt=5, levels=[1, 2],
        single_color='C0', color_scheme='tableau', detect=None,
        no_auto_factors=False, stop_at=None, args=None):

    class DerPar(object):
        def __init__(self, label, tex):
            self.label = label
            self.tex = tex

    levels = getattr(args, 'levels', levels)
    kde = getattr(args, 'kde', kde)
    fmt = getattr(args, 'fmt', fmt)
    single_color = [getattr(args, 'color', single_color),]
    color_scheme = getattr(args, 'color_scheme', color_scheme)
    color_scheme = get_color_names(color_scheme)
    no_auto_factors = getattr(args, 'no_auto_factors', no_auto_factors)
    stop_at = getattr(args, 'stop_at', stop_at)
    if not isinstance(list_of_sims, list):
        list_of_sims = [list_of_sims,]
    detect = getattr(args, 'detect', detect)
    detect = {} if detect is None else {detect: 0}
    
    list_hist_properties = []
    ini = configparser.ConfigParser()

    mcolors = itertools.cycle(color_scheme if len(list_of_sims) > 1 \
            else single_color)

    for sim in list_of_sims:
        loc = sim.plot_location(stop_at=stop_at)
        sim.read_conf()
        if not hasattr(sim, 'fits'):
            sim.fits = eval(sim.conf['status'].get('parameter fits', '{}'))
        if not hasattr(sim, 'derived_fits'):
            sim.derived_fits = eval(sim.conf['status'].get('derived parameter fits', '{}'))
        bestfit = eval(sim.conf['status'].get('best fit', '{}'))
        derived_bestfit = eval(sim.conf['status'].get('derived best fit', '{}'))
        bestfit = OrderedDict({**bestfit, **derived_bestfit})
        results_hist_table = io_tools.create_tex_table(os.path.join(loc,
            'hist_table.tex'), len_levels=len(levels))
        io_tools.table_headings(results_hist_table, levels=levels)
        if kde:
            results_kde_table = io_tools.create_tex_table(os.path.join(loc,
                'kde', 'kde_table.tex'), len_levels=len(levels))
            io_tools.table_headings(results_kde_table, levels=levels)
        normal_kde = eval(sim.conf['status'].get('gaussian parameters', '[]'))
        ini.read(sim.analysis.ini_file)
        hist_properties = {}
        mcor = next(mcolors)

        derived_parameters = []
        if not hasattr(sim, 'derived_distributions'):
            with open(os.path.join(loc, 'derived_parameters.p'), 'rb') as dd_file:
                sim.derived_distributions = pickle.load(dd_file)

        customfactors = eval(ini['simulation'].get('custom factors', 'None'))
        if customfactors is None:
            customfactors = {} if no_auto_factors \
                    else get_auto_factors(sim)

        for par in sim.derived_distributions.values():
            for label, tex in zip(par.label, par.tex):
                derived_parameters.append(DerPar(label, tex))

        for par in sim.analysis.parameters + derived_parameters:
            count = np.loadtxt(os.path.join(loc,
                'doacount_{0}.txt'.format(par.label)))
            seps = np.loadtxt(os.path.join(loc,
                'seps_{0}.txt'.format(par.label)))
            normalization = float(np.loadtxt(os.path.join(loc,
                'normalization_{0}.txt'.format(par.label))))
            factor = 10**customfactors.get(par.label, 0)
            sigmasCL, sigma_up = data_tools.get_1D_confidence_regions(count,
                    seps, parfit=sim.fits.get(par.label,
                        sim.derived_fits.get(par.label)), fmt=fmt,
                    factor=factor, levels=levels,
                    normal=par.label in normal_kde)
            try:
                prior = [par.prior.vmin, par.prior.vmax] # or '' when derived
            except AttributeError:
                prior = '' 
            io_tools.append_distribution_parameters_to_tex(results_hist_table,
                    par.tex, bestfit[par.label], sigmasCL, prior=prior,
                    factor=factor, fmt=fmt)

            if kde:
                ksupport = np.loadtxt(os.path.join(loc, 'kde',
                    'ksupport_{0}.txt'.format(par.label)))
                kdensity = np.loadtxt(os.path.join(loc, 'kde',
                    'kdensity_{0}.txt'.format(par.label)))
                if par.label in detect:
                    sigmas_detection = CL_excluding_value_kde(ksupport,
                            kdensity, exclude=0)
                    print("%s: %.2f-sigma detection" % (par.label,
                        sigmas_detection))
                    sim.read_conf()
                    if 'detection' in sim.conf.sections():
                        sim.conf.set('detection', par.label, 
                            "%.2f-sigma detection" % sigmas_detection)
                    else:
                        sim.conf['detection'] = {par.label: \
                                "%.2f-sigma detection" % sigmas_detection}
                    sim.conf_write_to_file()
                kde_sigmasCL, sigma_up = data_tools.get_1D_confidence_regions(
                        kdensity, ksupport, parfit=sim.fits.get(par.label,
                            sim.derived_fits.get(par.label)), fmt=fmt,
                        factor=factor, levels=levels, 
                        normal=par.label in normal_kde)
                sigma_up *= normalization
                io_tools.append_distribution_parameters_to_tex(results_kde_table,
                        par.tex, bestfit[par.label], kde_sigmasCL, prior=prior,
                        factor=factor, fmt=fmt)

            try:
                xvmin = par.prior.vmin
                xvmax = par.prior.vmax 
            except AttributeError: # not derived
                xvmin = seps[0] - 0.15*(seps[-1] - seps[0])
                xvmax = seps[-1] + 0.15*(seps[-1] - seps[0])

            hist_properties[par.label] = Histogram(par, mcor, count, seps,
                    normalization, bestfit[par.label], sigma_up)

        io_tools.close_tex(results_hist_table)
        if kde:
            io_tools.close_tex(results_kde_table)
        list_hist_properties.append(hist_properties)

    return list_hist_properties

def get_color_names(color_scheme):
    if color_scheme == 'tableau':
        colors = []
        for v in plt.rcParams['axes.prop_cycle']:
            colors.append(v['color'])
        return colors
    if color_scheme == 'base':
        option = None
        colors = OrderedDict(zip(
            ('b', 'orange', 'g', 'r', 'c', 'm', 'y', 'k'),
            ('b', 'orange', 'g', 'r', 'c', 'm', 'y', 'k')
            ))
    else:
        color_scheme = color_scheme.split('-')
        color_scheme, option = color_scheme if len(color_scheme) > 1 else (color_scheme[0], None)
        color_scheme = '{0}_colors'.format(color_scheme).upper()
        colors = getattr(matplotlib._color_data, color_scheme)
    if option:
        colors = dict([(key, color) for key, color in colors.items() \
                if option in key and 'lime' not in key])
    return colors.values()

def format_title(par, customfactors):
    par_tex, _ = format_factor_parameter(par.label, par.tex, customfactors)
    return r'$P(%s \mid D)$' % par_tex

def format_factor_parameter(label, tex, customfactors, units=None):
    log10factor = None
    if units and (label in units):
        tex = tex + r'\,' + '[%s]' % units[label]
    if customfactors and (label in customfactors):
        log10factor = customfactors[label]
        if log10factor == 0:
            return tex, log10factor
        if log10factor > 2 or log10factor < 0:
            return '10^{%i} \, %s' % (log10factor, tex), log10factor
        return '%i \, %s' % (10**log10factor, tex), log10factor
    return tex, log10factor

