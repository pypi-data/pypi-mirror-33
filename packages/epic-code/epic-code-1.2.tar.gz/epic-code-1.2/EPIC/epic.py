import os
from EPIC import gui, pyplot_grid_styles, color_options
from EPIC.utils import io_tools, plots, convergence

def analyze(sim, args):
    if args.convergence: #and if GelmanRubin
        setattr(args, 'burn_in', None)
    sim.analyze_chains(args, stop_at=args.stop_at)
    if args.convergence:
        _, hatRp = sim.Gelman_Rubin(args)
        from pprint import pprint
        pprint(hatRp-1)
    if args.plot:
        #setattr(args, 'kde', True)
        plots.make_plots([sim], args=args)

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(
            description='''This program allows parameter inference based on
                    Bayesian Analysis for models in Cosmology.'''
                    )
    subparsers = parser.add_subparsers()

    # launch gui
    parser_gui = subparsers.add_parser('gui', help='''Command for launching
            EPIC graphical user interface.''')

    parser_gui.add_argument('--theme', default='clam', choices=['alt', 'clam',
        'classic', 'default'], help='''Theme option for ttk widgets.''')

    parser_gui.set_defaults(func=gui.launch_gui)

    # run command
    parser_run = subparsers.add_parser('run', help='''Main command for running
            MCMC simulations.''')

    parser_run.add_argument('ini', help='''A .ini file or the path for the
            simulation you want to resume.''')

    parser_run.add_argument('chains', nargs='?', type=int, help='''The number
            of chains to be used in a new simulation.''')

    parser_run.add_argument('steps', type=int, help='''An integer number of steps
            for each MCMC loop.''')

    parser_run.add_argument('-m', '--mode', default='MCMC', choices=['MCMC',],# 'PT'],
            help='''Choose standard MCMC or Parallel Tempering algorithm
            (absent in this version).''')
    
    parser_run.add_argument('-c', '--check-interval', action=io_tools.TimeString,
            default=7200, help='''Option for MCMC mode only. The time interval
            after which the chains should be checked for convergence. Accepts
            the formats 1h, 180min, etc.  Default is two hours.''')
    
    parser_run.add_argument('--tolerance', type=float, default=1e-2, help='''Option
            for MCMC mode only. The tolerance below which the chains will be
            considered converged and the simulation will stop.''')

    parser_run.add_argument('--GR-steps', type=int, default=20, 
            metavar='STEPS', help='''Number of steps along the chain
            for the Gelman-Rubin evaluation.''')
    
    parser_run.add_argument('--GR-last', type=int, default=3, help='''Option
            for how many of the last steps of the Gelman Rubin evaluation
            should be considered on check during run.''')

    parser_run.add_argument('-b', '--bins', type=int, default=20,
            help='''Number of bins for histograms (when not using kde).''')

    parser_run.add_argument('--limit', type=int, default=None, help='''Option
            intended for PT mode (not present in this version of the code),
            which does not check convergence periodically, but can be used with
            MCMC mode. The simulation will stop by itself after reaching this
            many steps. If not specified, it can only be terminated by the
            user.''') 

    #parser_run.add_argument('-s', '--swap', type=int, default=30,
    #        help='''Option for PT mode. The average number of steps after which
    #        a swap proposal should be made. Actual proposal rate will be random
    #        about this value.''')

    parser_run.add_argument('--proposal-covariance', default=None,
            help='''Option to start new simulation with a custom covariance in
            the proposal distribution.''')

    #parser_run.add_argument('--beta-scale', default='log', choices=['log', 'linear'],
    #        help='''Option for PT mode. The scale of the temperatures ladder
    #        for the parallel chains.''')

    #parser_run.add_argument('--beta-max', default=10, type=float, help='''Option for
    #        PT mode. The log_2 of the maximum temperature in the ladder.''')

    parser_run.add_argument('--sim-full-name', help='''Option for new simulations.
            Appends this given name rather than the date and time to the mode
            in the folder name.''')

    parser_run.add_argument('--sim-tag', help='''Option for new simulations.
            Preppends this given tag or label to the beginning of the folder
            name.''')

    parser_run.add_argument('--alt-dir', help='''Custom path for saving simulation
            results. Overrides the default in altdir.txt''')

    parser_run.add_argument('--multi-start', action='store_true', 
            help='''Option to start chains not from random
            points but from default parameter values.''')

    parser_run.add_argument('--burn-in', type=int, help='''Optional burn-in
            size.''')
    
    parser_run.add_argument('--starting-point', nargs='*', type=float, help='''A
            common starting point for all chains can be given instead of
            sampling from the priors. May be useful for testing and debugging.
            Use one parameter value per argument.''')

    parser_run.add_argument('--adapt', nargs='+', type=int, 
            default=0, help='''Option for adaptation of chains. Receives up to
            three numbers: the first is the number of free random walk loops
            before adapting (FREE, default 0), the second is the number of
            loops for adaptation of the covariance matrix of the proposal
            distribution (ADAPT, default is the same as FREE) and the number of
            STEPS in adaptive loops (default will be the same number of steps
            in regular loops.''')

    parser_run.add_argument('--acceptance-limits', nargs=2, type=float,
            default=(0.1, 0.5), metavar=('MIN', 'MAX'), help='''Defines the
            acceptable range for the values of acceptance rates. Any chains
            presenting acceptance rate outside this range will be discarded
            prior to checking convergence.''')

    parser_run.add_argument('--chi2', action='store_true', help='''Option for
            evaluating likelihoods as log L = - chi^2/2 only or using all
            factors from the complete Gaussian distribution, including
            determinant of covariance matrix.''')

    parser_run.add_argument('--accepts-default', action='store_true',
            help='''Option for allowing no specification of parameter space
            point and predictions and likelihood evaluation with default
            values.''')

    # analyze command
    parser_analyze = subparsers.add_parser('analyze', help='''This module loads
            the chains for viewing and possibly checking convergence.''')

    parser_analyze.add_argument('ini', help='''The directory with the
            simulation to be analyzed.''')

    parser_analyze.add_argument('-s', '--stop-at', type=int, help='''Option for
            analyzing a chain until a certain size.''')

    parser_analyze.add_argument('--burn-in', type=int, help='''Optional burn-in
            size.''')
    
    parser_analyze.add_argument('--GR-steps', type=int, default=20, 
            metavar='STEPS', help='''Number of steps along the chain
            for the Gelman-Rubin evaluation.''')
    
    parser_analyze.add_argument('--kde', action='store_true', help='''Option for
            producing smoothed visualizations of the data distribution with
            kernel density estimation rather than histograms.''')

    parser_analyze.add_argument('--dont-redo-kde', action='store_false',
            dest='redo_kde', default=True, help='''This options helps avoiding
            repetition of kernel density estimation for all parameters when you
            only need some (for example, to complete some previous run that
            failed).''')

    parser_analyze.add_argument('-c', '--convergence', action='store_true',
            help='''Flag to perform calculation of convergence along the entire
            chains with all the GR_steps.''')

    parser_analyze.add_argument('--sequences', action='store_true',
            help='''Option to generate sequence plots.''')

    parser_analyze.add_argument('--correlation-function', action='store_true',
            help='''Option to calculate chains correlations.''')

    parser_analyze.add_argument('--use-tex', action='store_true',
            help='''Option to use LaTeX in sequence and correlation function
            plots.''')

    parser_analyze.add_argument('-b', '--bins', type=int, default=20,
            help='''Number of bins for histograms (when not using kde).''')

    parser_analyze.add_argument('--thin', type=int, help='''Thinning factor for
            kernel density estimates. By default is None and the code
            evaluates the factor according to the sample size.''')

    parser_analyze.add_argument('--kde-shuffle', action='store_true',
            help='''Whether or not to shuffle the sample before applying the
            thinning factor if kernel density estimates.''')

    parser_analyze.add_argument('--dont-plot', action='store_false',
            dest='plot', default=True, help='''Turns off automatic call of plot
            after analyze.''')

    #parser_analyze.add_argument('--interpolate-evidence', action='store_true',
    #        help='''Option to interpolate in the evaluation of the log of the
    #        evidence in PT simulations.''')

    parser_analyze.set_defaults(func=analyze)

    # plot command
    parser_plot = subparsers.add_parser('plot', help='''Utility for producing
            plots with the results of analyze. This is called by analyze by
            default but can be run independently.''')

    parser_plot.add_argument('ini', nargs='+', help='''The directory with the
            analysis results to be plotted.''')

    parser_plot.add_argument('-s', '--stop-at', type=int, help='''Option for
            ploting a chain until a certain size.''')

    parser_plot.add_argument('--fmt', type=int, default=5, help='''Number of
            decimal places for displaying numerical results.''')

    parser_plot.add_argument('--kde', action='store_true', help='''Option for
            producing smoothed visualizations of the data distribution with
            kernel density estimation rather than histograms.''')

    parser_plot.add_argument('--use-tex', action='store_true', help='''Option
            to make nice plots using LaTeX.''')

    parser_plot.add_argument('--font-size', type=int, default=8, help='''Font
            size for plots.''')

    parser_plot.add_argument('--levels', nargs='+', type=int, default=(1, 2),
            choices=[1, 2, 3, 4, 5], help='''Sigma confidence
            levels to show in plots.''')

    parser_plot.add_argument('--exclude', nargs='+', help='''Option to exclude
            any parameter from triangle plots. Use "nuisance" to exclude all
            nuisance parameters.''')

    parser_plot.add_argument('--show-hist', action='store_true', help='''Option
            to show histograms together with kde when using kde.''')

    parser_plot.add_argument('--show-gaussian-fits', action='store_true',
            help='''Option to show gaussian fits together with histograms or
            kde curves.''')

    parser_plot.add_argument('--no-best-fit-marks', action='store_false',
            dest='mark_best_fit', default=True, help='''Option to suppress plot
            of best fit points.''')

    parser_plot.add_argument('--png', action='store_true', help='''Option to
            save plots in png besides pdf (always saved).''')

    parser_plot.add_argument('--group-name', help='''Name of pdf files when
            plotting multiple analyses together.''')

    parser_plot.add_argument('--font', default='Computer Modern', 
            choices=list(io_tools.pdf_fonts.keys()),
            help='''Option to choose font for plot with tex.''')

    parser_plot.add_argument('--detect', default=None, help='''Option to
            calculate how many sigmas of detection (from zero) of a given
            parameter.''')

    parser_plot.add_argument('--no-auto-factors', action='store_true',
            help='''Option to not detect scales and set factors (power of 10)
            automatically in plots.''')

    parser_plot.add_argument('--no-custom-ticks', action='store_true',
            default=False, help='''Option to disable use of custom ticks 
            from ini file.''')
    
    parser_plot.add_argument('--no-auto-range', action='store_true',
            default=False, help='''Option to disable use of automatic ranges
            from final distributions. If disabled, will use priors.''')

    parser_plot.add_argument('--no-units', action='store_true',
            default=False, help='''Option to omit units in the plot axes labels
            when they are given in the .ini file.''')

    parser_plot.add_argument('--no-title-above', action='store_false',
            default=True, dest='title_above', help='''Option to print plot name
            inside frame rather than above.''') 

    parser_plot.add_argument('--title-pos', default='upper right',
            help='''Alignement of title inside frame when --no-title-above is
            used.''')

    parser_plot.add_argument('--color', default='C0', help='''Main color
            option for plots of a single analysis. Use any matpotlib color.''')

    parser_plot.add_argument('--color-scheme', choices=color_options,
        default='tableau', help='''Color palette option for plots with multiple
        analysis. Options are from matplotlib._color_data.  XKCD_COLORS and
        CSS4_COLORS are dictionaries containing 949 and 148 colors each one,
        respectively. Because they are not ordered dictionaries, each time you
        plot using them you will get a different color scheme with random
        colors, so have fun! The schemes with -light, -dark, etc, just filter
        the lists returning only the colors that have that characteristic in their
        names.''')

    parser_plot.add_argument('--style', choices=pyplot_grid_styles,
            default='default', help='''Matplotlib style option for plots.''')
    
    parser_plot.set_defaults(func=plots.make_plots)

    parser_monitor = subparsers.add_parser('monitor', help='''Utility for
            visualizing graphics for monitoring convergence.''')

    parser_monitor.add_argument('ini', nargs='+', help='''The existing
            simulation(s) directory.''')

    parser_monitor.add_argument('--use-tex', action='store_true',
            help='''Option to use LaTeX in plots.''')

    parser_monitor.add_argument('--png', action='store_true', help='''Option to
            save plots to png besides pdf.''')

    parser_monitor.set_defaults(func=convergence.monitor)

    #parser.add_argument('rargs', nargs=argparse.REMAINDER, help='''Collect
    #        argments for analyze after running MCMC.''')
    

    args = parser.parse_args()
    #from pprint import pprint
    #pprint(vars(args))

    if hasattr(args, 'func'):
        if hasattr(args, 'ini'):
            from EPIC import sim_objects
            if isinstance(args.ini, list):
                sim = [sim_objects.load_existing_simulation(each_ini, 
                    print_info=False) for each_ini in args.ini]
                for simulation in sim:
                    print(simulation.working_dir)
            else:
                sim = sim_objects.load_existing_simulation(args.ini, 
                        print_info=False)
            args.func(sim, args)
        else:
            args.func(args)
    else:
        assert not isinstance(args.ini, list)
        from EPIC import sim_objects
        # in which case we would 
        # return [sim_objects.load_existing_simulation(each_ini) for each_ini
        # in args.ini]
        # but only analyze and plot commands should use lists, and they both
        # have attribute 'func'

        if os.path.isfile(args.ini):
            working_dir, analysis = sim_objects.create_new_simulation(args)
            sim = sim_objects.load_existing_simulation(working_dir, analysis)
        else:
            sim = sim_objects.load_existing_simulation(args.ini)

        sim.start(args)
        rargs = parser_analyze.parse_args(
                [sim.working_dir, '--convergence', '--kde']
                )
        analyze(sim, rargs)

