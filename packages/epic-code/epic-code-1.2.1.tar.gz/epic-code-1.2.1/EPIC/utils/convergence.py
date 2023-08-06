import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from EPIC.utils import io_tools

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

def monitor_each_parameter(analysis, use_tex=False, png=False):

    yaxis1_color = 'C0'
    yaxis2_color = 'C4'
    
    wdirn = analysis.plot_location()

    list_of_k = np.loadtxt(os.path.join(wdirn, 'monitor_convergence.txt'),
            unpack=True)[0]
    hatR_V_W_pars = [np.loadtxt(os.path.join(wdirn, 'monitor_par%i.txt' % i),
        unpack=True) for i in range(analysis.nparams)]

    fig, axes = plt.subplots(analysis.nparams, 1, sharex='col')
    if analysis.nparams == 1:
        axes = [axes,]
    fig.set_size_inches(4, analysis.nparams)
    for i, par in enumerate(analysis.parameters):
        axes[i].plot(list_of_k, hatR_V_W_pars[i][0,:] - 1, lw=1.0, ls='-',
                label=r'$' + par.tex + '$', color=yaxis1_color)
        #axes[i].set_ylabel(r'$\hat{R}^{' + tex[par] + '}(k)-1$')
        axes[i].legend(loc='upper right', frameon=False, handlelength=0)
        sec_axis = axes[i].twinx()
        sec_axis.plot(list_of_k, hatR_V_W_pars[i][1,:], lw=0.5, ls='-', color=yaxis2_color)
        sec_axis.plot(list_of_k, hatR_V_W_pars[i][2,:], lw=0.5, ls=':', color=yaxis2_color)
        sec_axis.set_yscale('log')
        axes[i].set_yscale('log')
        # set color of yaxes 
        plt.setp(sec_axis.spines['right'], color=yaxis2_color)
        plt.setp(sec_axis.yaxis.get_majorticklines(), color=yaxis2_color)
        plt.setp(sec_axis.yaxis.get_minorticklines(), color=yaxis2_color)
        plt.setp(sec_axis.spines['left'], color=yaxis1_color) # (sec_axis is drawn above ax_R[i])
        plt.setp(axes[i].yaxis.get_majorticklines(), color=yaxis1_color)
        plt.setp(axes[i].yaxis.get_minorticklines(), color=yaxis1_color)
    axes[-1].set_xlabel(r'$k$')
    if use_tex:
        axes[0].set_xlabel(r'$\hat{R}^p-1$ \qquad \qquad \qquad \qquad \quad $|\hat{V}(k)|$, $|W(k)|$')
    else:
        axes[0].set_xlabel(r'$\hat{R}^p-1$' + 46 * ' ' + r'$|\hat{V}(k)|$, $|W(k)|$')
    axes[0].xaxis.set_label_position('top')
    fig.tight_layout()
    fig.subplots_adjust(hspace=0)
    fig.savefig(os.path.join(wdirn, 'monitor_each_parameter_%i.pdf' % list_of_k[-1]))
    if png:
        fig.savefig(os.path.join(wdirn, 'monitor_each_parameter_%i.png' % list_of_k[-1]), dpi=360)

#===============================================================================

def plot_monitor_convergence(list_of_analyses, use_tex=False, png=False):

    fig, ax_R = plt.subplots(len(list_of_analyses), 1, sharex='col')
    if len(list_of_analyses) == 1:
        ax_R = [ax_R,]
    fig.set_size_inches(0.8*5, 0.8*2*len(list_of_analyses))

    yaxis1_color = 'C0'
    yaxis2_color = 'C4'

    for i, analysis in enumerate(list_of_analyses):
        wdirn = analysis.plot_location()
        list_of_k, hatRp_of_k, V_of_k, W_of_k = np.loadtxt(os.path.join(wdirn,
            'monitor_convergence.txt'), unpack=True)
        ax_R[i].plot(list_of_k, hatRp_of_k-1, lw=1.0, color=yaxis1_color, label=analysis.model.model)
        ax_VW = ax_R[i].twinx()
        ax_VW.plot(list_of_k, V_of_k, lw=0.5, ls='-', color=yaxis2_color)#, label=r'$|\hat{V}(k)|$')
        ax_VW.plot(list_of_k, W_of_k, lw=0.5, ls=':', color=yaxis2_color)#, label=r'$|W(k)|$')
        ax_VW.set_yscale('log')
        ax_R[i].set_yscale('log')
        #plt.setp(ax_VW.get_yticklines(), color=yaxis2_color)
        # set color of yaxes 
        plt.setp(ax_VW.spines['right'], color=yaxis2_color)
        plt.setp(ax_VW.yaxis.get_majorticklines(), color=yaxis2_color)
        plt.setp(ax_VW.yaxis.get_minorticklines(), color=yaxis2_color)
        plt.setp(ax_VW.spines['left'], color=yaxis1_color) # (ax_VW is drawn above ax_R[i])
        plt.setp(ax_R[i].yaxis.get_majorticklines(), color=yaxis1_color)
        plt.setp(ax_R[i].yaxis.get_minorticklines(), color=yaxis1_color)
        ax_R[i].legend(loc="upper right", frameon=False, borderaxespad=0.5, handlelength=0)

    if use_tex:
        ax_R[0].set_xlabel(r'$\hat{R}^p(k)-1$ \qquad \qquad \qquad \qquad \quad $|\hat{V}(k)|$, $|W(k)|$',
                fontsize=12)
    else:
        ax_R[0].set_xlabel(r'$\hat{R}^p(k)-1$' + 37 * ' ' + r'$|\hat{V}(k)|$, $|W(k)|$', 
                fontsize=12)
    ax_R[0].xaxis.set_label_position('top')
    ax_R[-1].set_xlabel(r'$k$')

    fig.tight_layout()
    # uses the last list_of_k and wdirn from loop above 
    fig.subplots_adjust(hspace=0)
    fig.savefig(os.path.join(wdirn, 'monitor_convergence_%i.pdf' % list_of_k[-1]))
    if png:
        fig.savefig(os.path.join(wdirn, 'monitor_convergence_%i.png' % list_of_k[-1]), dpi=360)

def monitor(list_of_analyses, args):
    if args.use_tex:
        plt.rc('text', usetex=True)

    for analysis in list_of_analyses:
        monitor_each_parameter(analysis, use_tex=args.use_tex, png=args.png)

    plot_monitor_convergence(list_of_analyses, use_tex=args.use_tex, png=args.png)

