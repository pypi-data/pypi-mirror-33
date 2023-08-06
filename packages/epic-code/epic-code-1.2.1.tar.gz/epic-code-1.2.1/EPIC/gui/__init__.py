import multiprocessing
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import messagebox, ttk
import configparser
from collections import OrderedDict
from EPIC import root, pyplot_available_styles
from EPIC.cosmology import cosmic_objects as cosmo
from EPIC.utils.io_tools import parse_unit, split_last, tex_packages, \
        available_fonts
from EPIC.utils.numbers import speedoflight
from EPIC.gui import custom_widgets as EPIC_widgets
import os
from numpy import ceil, logspace, linspace, log10
import platform

class Application(object):

    WIDTH = 1257
    MINHEIGHT = 731
    HEIGHT = 781
    LEFT_FRAME_WIDTH = 476
    CORNER_WIDTH = 160
    #BOTTOM_CENTER_FRAME_WIDTH = 182
    BOTTOM_RIGHT_FRAME_HEIGHT = 150
    STATUS_BAR_HEIGHT = 56

    PADX = 10
    PADY = 10
    RIGHT_FRAME_WIDTH = WIDTH-2*PADX-LEFT_FRAME_WIDTH

    IPADX = 4
    IPADY = 4
    default_padding = {'padx': PADX, 'pady': PADY}
    default_xpadding = {'padx': PADX}
    default_ypadding = {'pady': PADY}
    default_ipadding = {'ipadx': IPADX, 'ipady': IPADY}
    default_ixpadding = {'ipadx': PADX}
    default_iypadding = {'ipady': PADY}

    list_of_solved_models = []
    please_select_model = '(Select a model...)'
    please_select_species = '(Select...)'
    please_select_style = 'Plot style'
    models_list_notice = \
            '\n'.join([
                'Models will be added to the',
                'list on the right if you include',
                'Distances. You can double',
                'click any entry to rename it.',
                ])

    distances_to_compare = [
            'Comoving distance $\chi(z)$',
            'Angular diameter $d_A(z)$',
            #'Volume averaged $d_V(z)$',
            'Hubble $d_H(z)$', 
            'Lookback time $c\,t(z)$',
            'Luminosity $d_L(z)$',
        ]

    styles_list = [style.replace('_', ' ') for style \
                    in pyplot_available_styles]

    tex_options = ['Do not use TeX']
    texprefix = 'TeX with'

    for font in available_fonts.keys():
        tex_options.append(' '.join([texprefix, font]))

    matplotlib_fonts = dict(zip(tex_options, [None, 'Computer Modern Roman',
        'Times New Roman', 'Charter', 'Palatino']))

    def __init__(self, master=None, theme='clam'):
        self.rccustom()
        self.master = master
        self.master.title("EPIC's Cosmology Calculator")
        #self.master.minsize(height=self.MINHEIGHT)
        icon = tk.Image("photo", file=os.path.join(root, 'gui_files',
            'iconepic.gif'))
        self.master.tk.call('wm', 'iconphoto', self.master._w, icon)
        self.frame_bg, self.foreground_text = EPIC_widgets.configure_ttk(
                theme=theme)
        self.master.config(background=self.frame_bg)
        self.create_widgets()

    def rccustom(self):
        try:
            fsize = self.fontsize_choice.get()
        except AttributeError:
            fsize = 12

        plt.rcParams.update({
            'grid.linewidth': 0.5,
            'grid.linestyle': '-',
            'font.size': fsize or 12,
        #    'legend.handlelength': 2.2,
        #    'legend.framealpha': 1.0,
        })

    def set_tex_option(self):
        option = self.tex_options[self.tex_choice.get()]
        if self.texprefix in option:
            plt.rcParams.update({'text.usetex': True})
            font_preamble = tex_packages(
                    available_fonts[option[len(self.texprefix)+1:]]
                    )
            plt.rcParams.update({
                'text.latex.preamble': font_preamble,
                'text.latex.unicode' : True,
                'text.latex.preview' : True,
                'font.size': self.fontsize_choice.get() or 14,
                'font.family': 'serif',
                'font.serif': self.matplotlib_fonts[option]
                })
            self.remake_plots()
        else:
            # this guarantees tex will be reset to False, since plot_style
            # selection preserves it
            plt.rcdefaults()
            if self.style_choice.get() == 0:
                self.rccustom()
                self.remake_plots()
            else:
                self.current_style = -1 #to force remake plots next
                # this will preserve selected style
                self.set_chosen_plot_style()

    def create_widgets(self):
        self.available_models = configparser.ConfigParser()
        self.available_models.read([
            os.path.join(root, 'cosmology', 'model_recipes.ini'),
            os.path.join(root, 'modifications', 'cosmology',
                'model_recipes.ini'),
            ])
        self.available_species = configparser.ConfigParser()
        self.available_species.read([
            os.path.join(root, 'cosmology', 'available_species.ini'),
            os.path.join(root, 'modifications', 'cosmology',
                'available_species.ini'),
            ])
        self.models = self.available_models.sections()
        self.models = OrderedDict((model, self.available_models[model]['name']) \
                for model in self.models if 'name' in self.available_models[model])

        # map models label and name
        self.map_model = {self.please_select_model: self.please_select_model}
        for model in self.models:
            if 'name' in self.available_models[model]:
                self.map_model[model] = self.available_models[model]['name'].replace(
                        r'$\Lambda$', 'Λ').replace('$w$CDM', 'wCDM') 
        remap(self.map_model)

        # map parameters label and tex
        self.map_parameters = {'h': 'h', 'H0': 'H_0', 'xi': r'\xi'}
        for section in ['density parameter', 'physical density parameter']:
            for key, par_label in self.available_species[section].items():
                self.map_parameters[par_label] = self.available_species['tex '+ section][key]
        for key, lparams in self.available_species['EoS parameters'].items():
            for par, tex in zip(eval(lparams), eval(self.available_species['tex EoS parameters'][key])):
                self.map_parameters[par] = tex

        # Status bar
        self.status_bar = tk.Label(self.master, bg=self.foreground_text,
                fg='white', anchor=tk.W, relief=tk.FLAT,
                **self.default_padding) 
        self.status_bar.config(text="Welcome to the EPIC's Cosmology Calculator. " \
                + "Choose a model to start, then specify the parameters " \
                + "and make some plots.")
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # bottom ttk Notebook
        parameters_setup_notebook = ttk.Notebook(self.master,
                height=self.BOTTOM_RIGHT_FRAME_HEIGHT-self.PADY)
        parameters_setup_notebook.pack(side=tk.BOTTOM, fill=tk.X, #expand=1,
                **self.default_iypadding, **self.default_padding)

        parameter_space_frame = ttk.Frame(parameters_setup_notebook)
        parameters_setup_notebook.add(parameter_space_frame,
                text='Specify parameters')
        #constrain_parameters_frame = ttk.Frame(parameters_setup_notebook)
        #parameters_setup_notebook.add(constrain_parameters_frame,
        #        text='Constrain with MCMC')

        parameters_setup_notebook.pack_propagate(False)

        left_frame = ttk.Frame(parameter_space_frame,
                width=self.LEFT_FRAME_WIDTH)
        left_frame.pack(side=tk.LEFT, fill=tk.Y)#, **self.default_xpadding)#, expand=1)
        left_frame.pack_propagate(False)

        self.parameter_values = ttk.Frame(left_frame)
        self.parameter_values.pack(fill=tk.BOTH, expand=1)

        right_frame = ttk.Frame(parameter_space_frame,
                width=self.RIGHT_FRAME_WIDTH)
        right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)
        right_frame.pack_propagate(False)
        
        model_setup_notebook = ttk.Notebook(self.master)
        model_setup_LF = ttk.Frame(model_setup_notebook)
        model_setup_notebook.add(model_setup_LF, text='Cosmology')
        model_setup_notebook.pack(side=tk.LEFT, fill=tk.Y, 
                **self.default_padding)
        model_setup_notebook.pack_propagate(False)

        self.plots_notebook = ttk.Notebook(self.master, style='Plot.TNotebook')
        self.model_solution_tabs_dict = OrderedDict()
        for plot, xlabel, ylabel, xscale, yscale, xtoggle, ytoggle in [
                ('Density parameters', r'$a$', r'$\Omega$', 'log', 'linear',
                    True, False),
                ('Energy densities', r'$a$', r'$\rho \, [\rm{kg}/\rm{m}^3]$',
                    'log', 'log', True, False),
                #('Comoving distances', r'$z$', r'$d(z) \, [\rm{Mpc}]$', 'log',
                #    'log', True, True),
                ('Distances', r'$z$', r'$d(z) \, [\rm{Mpc}]$', 'log',
                    'log', True, True),
                #('Adimensional distances', r'$z$', r'$d(z)/d_H(z)$', 'log',
                #    'log', True, True),
                ('Lookback time', r'$z$', r'$t(z) \, [\rm{Gyr}]$', 'log',
                    'linear', True, True),
                ('Equation of state', r'$a$', r'$w(a)$', 'log', 'linear',
                    False, False),
                ]:
            self.model_solution_tabs_dict[plot] = EPIC_widgets.FigureFrame(
                    self.plots_notebook, plot_name=plot, xlabel=xlabel,
                    ylabel=ylabel, yscale=yscale,
                    xscale_toggle=xtoggle, yscale_toggle=ytoggle,
                    difference_toggle=False, bg=self.frame_bg
                    )
            self.plots_notebook.add(self.model_solution_tabs_dict[plot],
                    text=plot)

        self.distance_comparison_tabs_dict = OrderedDict(
                ((name, EPIC_widgets.FigureFrame(
                    self.plots_notebook, plot_name=name, xlabel=r'$z$', 
                    ylabel=split_last(name)[1].rstrip('$') + r'\, [\rm{Mpc}]$',
                    yscale='log', difference_toggle=True,
                    xscale_toggle=True, yscale_toggle=True,
                    #name == 'Lookback time',
                    bg=self.frame_bg,
                    )) for name in self.distances_to_compare)
            )
        for name in self.distances_to_compare:
            self.plots_notebook.add(self.distance_comparison_tabs_dict[name],
                    text=split_last(name)[0])

        for tab in self.plots_notebook.tabs():
            self.plots_notebook.hide(tab)
        self.plots_notebook.pack(side=tk.RIGHT, fill=tk.BOTH, expand=1, **self.default_padding)

        include_plots_frame = ttk.Frame(right_frame)
        include_plots_frame.pack(side=tk.LEFT, anchor=tk.NW, fill=tk.Y,
                expand=1)

        include_plots_LF = ttk.LabelFrame(include_plots_frame, relief=tk.FLAT,
                #width=(self.RIGHT_FRAME_WIDTH-8*self.PADX)//4,
                text='Include plots of:')
        include_plots_LF.pack(anchor=tk.NW, fill=tk.Y, expand=1,
                **self.default_padding)
        #include_plots_LF.pack_propagate(False)

        corner_frame = ttk.Frame(right_frame, 
                width=(self.RIGHT_FRAME_WIDTH-0*self.PADX)//4)
        corner_frame.pack(side=tk.LEFT, fill=tk.Y, expand=1,
                **self.default_padding)
        corner_frame.pack_propagate(False)

        self.corner_frame_buttons = ttk.Frame(corner_frame)
        self.corner_frame_buttons.pack(fill=tk.X, expand=1, anchor=tk.NW)

        self.solve_button = ttk.Button(self.corner_frame_buttons, state=tk.DISABLED,
                text='Solve background\ncosmology',# height=5,
                command=self.get_cosmo_solution)
        self.solve_button.grid(row=0, column=0, columnspan=3, sticky=tk.W+tk.E)
        #self.solve_button.grid_propagate(False)

        calc_at_z_btn = ttk.Button(self.corner_frame_buttons, #padding='2 3 2 3',
                text='Calculate at:', state=tk.DISABLED,
                command=self.calculate_at_z)
        calc_at_z_btn.grid(row=1, column=0, sticky=tk.NW+tk.SW)
        EPIC_widgets.MyTextLabel(self.corner_frame_buttons, 'z', width=4,
                background=self.frame_bg).grid(row=1, column=1, sticky=tk.W+tk.E,
                        **self.default_xpadding)
        self.z_var = tk.DoubleVar()
        self.z_var.set(1.0)
        at_z_entry = ttk.Entry(self.corner_frame_buttons, width=4, font=('Times',
            14-EPIC_widgets.platform_reduce_font_parameter), state=tk.DISABLED,
            textvariable=self.z_var)
        at_z_entry.grid(row=1, column=2, sticky=tk.NW+tk.SE)

        self.age_label = ttk.Label(corner_frame, justify=tk.LEFT, anchor=tk.SW,
                text='')
        self.age_label.pack(anchor=tk.SW, expand=1)

        self.saved_models_frame = ttk.Frame(right_frame)
        #width=(self.RIGHT_FRAME_WIDTH-8*self.PADX)//4)
        self.saved_models_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=1,
                **self.default_padding)

        select_buttons_frame = ttk.Frame(self.saved_models_frame)
        select_buttons_frame.pack(side=tk.TOP, fill=tk.X, expand=1)

        n_select_btns = 5
        columns_iter = iter(range(n_select_btns))
        ttk.Button(select_buttons_frame, style='Flat.TButton',
                command=self.rename_active, text='Rename').grid(row=0,
                        column=next(columns_iter), sticky=tk.NW+tk.SE)
        ttk.Label(select_buttons_frame, text='Select:', anchor=tk.E).grid(
                row=0, column=next(columns_iter), sticky=tk.NW+tk.SE)
        ttk.Button(select_buttons_frame, text='All', width=4,
                command=self.comparison_select_all,
                style='Flat.TButton').grid(row=0, column=next(columns_iter),
                        sticky=tk.NW+tk.SE)
        ttk.Button(select_buttons_frame, width=4,
                command=self.comparison_clear_selection, style='Flat.TButton',
                text='None').grid(row=0, column=next(columns_iter),
                        sticky=tk.NW+tk.SE)
        ttk.Button(select_buttons_frame, width=4,
                command=self.comparison_invert_selection, style='Flat.TButton',
                text='Invert').grid(row=0, column=next(columns_iter),
                        sticky=tk.NW+tk.SE)
        ttk.Button(self.saved_models_frame, text='Compare distances',
                command=self.new_comparison).pack(side=tk.BOTTOM, fill=tk.BOTH,
                        expand=1)

        for i in range(n_select_btns):
            select_buttons_frame.columnconfigure(i, weight=1)
        select_buttons_frame.pack_propagate(False)

        listbox_frame = ttk.Frame(self.saved_models_frame)
        listbox_frame.pack(fill=tk.BOTH, expand=1)
        listbox_frame.pack_propagate(False)

        self.saved_models_listbox = EPIC_widgets.ListboxEditable(
                listbox_frame, selectmode=tk.EXTENDED)
        self.saved_models_listbox.grid(row=0, column=0, sticky=tk.NW+tk.SE)
        saved_scroll = ttk.Scrollbar(listbox_frame, orient=tk.VERTICAL)
        saved_scroll.grid(row=0, column=1, sticky=tk.N+tk.S)
        listbox_frame.columnconfigure(0, weight=1)
        listbox_frame.rowconfigure(0, weight=1)
        self.saved_models_listbox.config(yscrollcommand=saved_scroll.set)
        saved_scroll.config(command=self.saved_models_listbox.yview)

        config_all_widgets(self.saved_models_frame, state=tk.DISABLED)

        self.model_results_tabs_states = OrderedDict([
                ('Density parameters', 1),
                ('Energy densities', 1),
                ('Distances', 0),
                ('Equation of state', 0)
                ])

        self.model_results_checkbuttons_dict = {}
        self.model_results_checkbuttons_var = {}

        for i, tab in enumerate(self.model_results_tabs_states.keys()):
            self.model_results_checkbuttons_var[tab] = tk.IntVar()
            self.model_results_checkbuttons_dict[tab] = ttk.Checkbutton(include_plots_LF,
                    text=tab, variable=self.model_results_checkbuttons_var[tab],
                    command=getattr(self, 'show_hide_%s' % tab.replace(' ', '_'))
                    ) #borderwidth=0, highlightthickness=0, 
            self.model_results_checkbuttons_dict[tab].grid(row=i, column=0,
                    columnspan=1 if i == 2 else 4, sticky=tk.NW+tk.SW)
            #pack(anchor=tk.W, fill=tk.Y, expand=1)

        ttk.Label(include_plots_LF, text='(z max:').grid(row=2, column=1, sticky=tk.E)
        self.zrange_combobox = EPIC_widgets.ReadonlyCombobox(include_plots_LF,
                values=['5', '100', '10³', '10\u2074'], width=3, state=tk.DISABLED)
        self.zrange_combobox.current(3)
        self.zrange_combobox.grid(row=2, column=2, sticky=tk.W+tk.E) 
        ttk.Label(include_plots_LF, text=')').grid(row=2, column=3,
                sticky=tk.W)

        for tab, state in self.model_results_tabs_states.items():
            self.model_results_checkbuttons_var[tab].set(1-state)
            self.model_results_checkbuttons_dict[tab].invoke()

        self.model_results_checkbuttons_dict['Equation of state'].config(state=tk.DISABLED)

        textcfg = ttk.Frame(include_plots_frame)
        textcfg.pack(anchor=tk.SW, fill=tk.Y, expand=1, **self.default_xpadding)

        self.style_choice = tk.IntVar()
        plot_style_btn = ttk.Menubutton(textcfg, direction='above', width=0,
                padding=3, text=self.please_select_style)
        stylemenu = tk.Menu(plot_style_btn, title=self.please_select_style)
        self.style_choice.set(0)
        self.current_style = 0
        for i, option in enumerate(self.styles_list):
            stylemenu.add_radiobutton(label=option, value=i,
                    variable=self.style_choice,
                    command=self.set_chosen_plot_style)
        plot_style_btn.config(menu=stylemenu)

        self.tex_choice = tk.IntVar()
        bw=28
        ext = 'png' if tk.TkVersion >= 8.6 else 'gif'
        im = tk.PhotoImage(file=os.path.join(root, 'gui_files', 'images',
            'menu-tex.' + ext))
        tex_menubtn = ttk.Menubutton(textcfg, direction='above', width=0,
                padding=3, image=im)
        tex_menubtn.image = im
        texmenu = tk.Menu(tex_menubtn, title='TeX options') #, tearoff=0)
        self.tex_choice.set(0)
        for i, option in enumerate(self.tex_options):
            texmenu.add_radiobutton(label=option, value=i,
                    variable=self.tex_choice, command=self.set_tex_option)
        tex_menubtn.config(menu=texmenu)

        self.fontsize_choice = tk.IntVar()
        im = tk.PhotoImage(file=os.path.join(root, 'gui_files', 'images',
            'fontsize.' + ext))
        fontsize_btn = ttk.Menubutton(textcfg, direction='above', width=0,
                padding=3, image=im)
        fontsize_btn.image = im
        fontsize_menu = tk.Menu(fontsize_btn, title='Font size')#, tearoff=0)
        self.fontsize_choice.set(0)
        for i in range(10, 20, 2):
            fontsize_menu.add_radiobutton(label=str(i), value=i,
                    variable=self.fontsize_choice, command=self.set_font_size)
        fontsize_btn.config(menu=fontsize_menu)

        tex_menubtn.grid(row=0, column=0, sticky='nws')
        fontsize_btn.grid(row=0, column=1, sticky='nws')
        plot_style_btn.grid(row=0, column=2, sticky='nws')

        self.BUTTONS = [plot_style_btn, tex_menubtn, fontsize_btn]

        for i in range(2):
            fontsize_btn.columnconfigure(i, weight=0)

        iter_rows = iter(range(7))

        cb_model_values = [self.please_select_model,] \
                + [self.map_model[model] for model in self.models.keys()]
        self.model_options_combobox = EPIC_widgets.ReadonlyCombobox(model_setup_LF, 
                width=round(210/EPIC_widgets.pixels_to_char_size),
                values=cb_model_values)
        self.model_options_combobox.current(0)

        next_row = next(iter_rows)
        ttk.Label(model_setup_LF, text='Model:').grid(row=next_row, column=0,
                sticky=tk.E, **self.default_padding)
        self.model_options_combobox.grid(row=next_row, column=1, sticky=tk.W,
                **self.default_padding)
        self.model_options_combobox.bind("<<ComboboxSelected>>",
                func=self.show_optional_species, add='+')

        next_row = next(iter_rows)
        ttk.Label(model_setup_LF, text='Mandatory species:').grid(row=next_row,
                column=0, sticky=tk.E, **self.default_padding)
        self.mandatory_msg = ttk.Label(model_setup_LF,
                width=round(230/EPIC_widgets.pixels_to_char_size),
                text=self.please_select_model+'\n', padding=self.PADX)
        self.mandatory_msg.grid(row=next_row, column=1, sticky=tk.W,
                **self.default_ypadding)

        next_row = next(iter_rows)
        self.optional_species_listbox = tk.Listbox(model_setup_LF,
                selectmode=tk.MULTIPLE, height=2)
        ttk.Label(model_setup_LF, text='Add optional species:').grid(
                row=next_row, column=0, sticky=tk.E, **self.default_padding)
        self.optional_species_listbox.grid(row=next_row, column=1, 
                sticky=tk.W, **self.default_padding)

        cb_frame = ttk.Frame(model_setup_LF)
        cb_frame.grid(row=next(iter_rows), column=0, columnspan=2, sticky=tk.NW+tk.SE)

        self.combined_var = tk.IntVar()
        self.combined_var.set(0)
        self.combined_option = ttk.Checkbutton(cb_frame,
                variable=self.combined_var, state=tk.DISABLED,
                text='Use combined matter\nfluid (cdm+baryons)'
                )
        self.combined_option.pack(side=tk.LEFT, expand=1,
                anchor=tk.CENTER, **self.default_padding)

        self.physical_var = tk.IntVar()
        self.physical_var.set(1)
        ttk.Checkbutton(cb_frame, text='Use physical\ndensities',
                variable=self.physical_var).pack(side=tk.LEFT, expand=1,
                        anchor=tk.CENTER, **self.default_padding)

        next_row = next(iter_rows)
        self.derived_lbl = ttk.Label(model_setup_LF, justify=tk.RIGHT,
                state=tk.DISABLED,
                text='Use density of this fluid\nas derived parameter:')
        self.derived_lbl.grid(row=next_row, column=0, sticky=tk.E,
                **self.default_padding)
        self.derived_combobox = EPIC_widgets.ReadonlyCombobox(model_setup_LF,
                state=tk.DISABLED, values=[self.please_select_species,],
                width=8)
        self.derived_combobox.current(0)
        self.derived_combobox.grid(row=next_row, column=1, sticky=tk.W,
                **self.default_padding)

        next_row = next(iter_rows)
        self.int_frame = ttk.Frame(model_setup_LF)
        self.int_frame.grid(row=next_row, column=1, sticky=tk.W+tk.E)
        self.interaction_propto_options = EPIC_widgets.ReadonlyCombobox(
                self.int_frame, width=8, values=[self.please_select_species,])
        self.int_propto_label = ttk.Label(model_setup_LF, justify=tk.RIGHT,
                text='Interaction setup -\nProportional to density of:', state=tk.DISABLED)
        self.int_propto_label.grid(row=next_row, column=0, sticky=tk.E,
                **self.default_padding)
        self.interaction_propto_options.current(0)
        self.interaction_propto_options.pack(side=tk.LEFT, anchor=tk.W,
                **self.default_padding)

        self.int_sign_combobox = EPIC_widgets.ReadonlyCombobox(self.int_frame,
                width=5, values=['(sign)', '+1', '-1'])
        self.int_sign_combobox.current(1)
        self.int_sign_combobox.pack(side=tk.LEFT, anchor=tk.CENTER,
                **self.default_padding)

        ttk.Button(self.int_frame, style='Flat.TButton', text='Set', width=5,
                command=self.set_and_update_gif).pack(side=tk.LEFT,
                        anchor=tk.W, **self.default_padding)

        config_all_widgets(self.int_frame, state=tk.DISABLED)

        self.darksector_and_build_frame = ttk.Frame(model_setup_LF)
        self.darksector_and_build_frame.grid(row=next(iter_rows), column=0,
                columnspan=2)

        img = tk.PhotoImage(file=os.path.join(root, 'gui_files', 'blank.gif'))
        img_lbl_text = ttk.LabelFrame(self.darksector_and_build_frame,
                text='Dark sector:')
        img_lbl_text.pack(side=tk.LEFT, **self.default_padding)

        self.img_lbl = ttk.Label(img_lbl_text, style='Image.TLabel', image=img)
        self.img_lbl.image = img
        self.img_lbl.pack() 

        ttk.Button(self.darksector_and_build_frame, text='Build\nnew\nmodel',
                width=5, command=self.build_model).pack(side=tk.RIGHT, expand=1,
                        anchor=tk.S, **self.default_ipadding,
                        **self.default_padding)

        config_all_widgets(self.darksector_and_build_frame, state=tk.DISABLED)

        for x in range(8):
            model_setup_LF.rowconfigure(x, weight=1)
        for y in range(2):
            model_setup_LF.columnconfigure(y, weight=0)

    def set_font_size(self):
        current_size = plt.rcParams['font.size'] 
        new_size = self.fontsize_choice.get()
        if new_size != current_size:
            plt.rcParams['font.size'] = new_size
            self.remake_plots()

    def comparison_select_all(self, func='selection_set'):
        getattr(self.saved_models_listbox, func)(0, last=tk.END)

    def comparison_clear_selection(self):
        self.comparison_select_all(func='selection_clear')

    def comparison_invert_selection(self):
        for i in range(self.saved_models_listbox.size()):
            if self.saved_models_listbox.selection_includes(i):
                self.saved_models_listbox.selection_clear(i)
            else:
                self.saved_models_listbox.selection_set(i)

    def rename_active(self):
        if len(self.saved_models_listbox.curselection()) != 1:
            self.saved_models_listbox.selection_set(tk.ACTIVE)
        self.saved_models_listbox.edit()

    def show_hide_tabs(self, which_tabs):
        show = self.model_results_checkbuttons_var[which_tabs].get()
        if which_tabs == 'Distances':
            which_tabs = [
                    #'Comoving distances', 
                    'Distances', 
                    'Lookback time'
                    ]
            self.zrange_combobox.config(state='readonly' if show else tk.DISABLED)
        else:
            which_tabs = [which_tabs,]
        set_of_tabs = self.model_solution_tabs_dict
        for tab in which_tabs:
            if show:
                #self.hide_distance_comparison_tabs()
                self.plots_notebook.add(set_of_tabs[tab])
                #, text=tab,
            else:
                current = self.plots_notebook.select()
                try:
                    tabid = set_of_tabs[tab].winfo_pathname(set_of_tabs[tab].winfo_id())
                    self.plots_notebook.hide(tabid)
                except tk.TclError:
                    pass
                if current not in self.plots_notebook.tabs():
                    select_first_visible(self.plots_notebook)

        self.determine_solve_btn_state()

    def determine_solve_btn_state(self):
        if hasattr(self, 'cosmo_model') and any([check.get() \
                for check in self.model_results_checkbuttons_var.values()]):
            state = tk.NORMAL
        else:
            state = tk.DISABLED
        self.solve_button.config(state=state)

    def show_hide_Distances(self):
        return self.show_hide_tabs('Distances')

    def show_hide_Density_parameters(self):
        return self.show_hide_tabs('Density parameters')

    def show_hide_Energy_densities(self):
        return self.show_hide_tabs('Energy densities')

    def show_hide_Equation_of_state(self):
        return self.show_hide_tabs('Equation of state')

    def new_comparison(self):
        if len(self.saved_models_listbox.curselection()) < 1:
            messagebox.showerror('Error', 'At least one model must be selected.')
            return None

        self.master.config(cursor='exchange')
        self.master.update()
        self.compare_distances()
        self.master.config(cursor='left_ptr')

    def compare_distances(self, models=None, labels=None):

        if models is None:
            models = [self.list_of_solved_models[i] \
                    for i in self.saved_models_listbox.curselection()] 
        if labels is None:
            labels = self.saved_models_listbox.get(0, tk.END)
            labels = [labels[i].replace('Λ', r'$\Lambda$').replace('wCDM',
                r'$w$CDM') for i in self.saved_models_listbox.curselection()]

        self.status_bar.config(text='Plotting...')
        self.status_bar.update()

        if self.viewing != 'dist':
            for key, cb in self.model_results_checkbuttons_dict.items():
                if self.model_results_checkbuttons_var[key].get():
                    cb.invoke()

        for plot_name in self.distances_to_compare:
            instructions = [model.results['Distances'] \
                    for model in models]
            self.distance_comparison_tabs_dict[plot_name].add_distance_comparison_to_widget(
                    plot_name, instructions, labels)

        if self.viewing != 'dist':
            for plot_name in self.distances_to_compare:
                self.plots_notebook.add(self.distance_comparison_tabs_dict[plot_name])
                # text=split_last(plot_name)[0],

        if self.viewing != 'dist':
            select_first_visible(self.plots_notebook)

        self.viewing = 'dist'
        self.all_models = list(models)
        self.all_labels = list(labels)
        self.status_bar.config(text='Done.')

    def visible_tab(self, tab):
        return tab in self.plots_notebook.tabs() \
                and self.plots_notebook.tab(tab)['state'] == 'normal'

    def build_model(self):

        if hasattr(self, 'age_label'):
            self.age_label.config(text=self.models_list_notice)

        modelname = self.map_model[self.model_options_combobox.get()]
        if modelname == self.please_select_model:
            messagebox.showerror('Error', 'Please, select a model first.')
            return None
        #print('model', modelname)
        optional = self.optional_species_listbox.curselection()
        optional = [self.optional_species[i] for i in optional]
        #print('optional', optional)
        if 'cde' in modelname:
            if self.interaction_propto_options.get() == self.please_select_species \
                    or self.int_sign_combobox.get() == '(sign)':
                messagebox.showerror('Error', 'Please, make sure to set up correctly the interaction.')
                return None
            propto = self.map_species_abbrv[self.interaction_propto_options.get()]
            dependent_on_other = list(self.mandatory_species)
            dependent_on_other.remove(propto)
            propto_other = {dependent_on_other[0]: propto}
            sign = int(self.int_sign_combobox.get())
            int_setup = {
                'species': self.mandatory_species[:2],
                'propto_other': propto_other,
                'parameter': {propto: 'xi'},
                'tex': r'\xi',
                'sign': dict(zip(self.mandatory_species[:2], [sign, -sign]))
                }
            combined = []
        else:
            int_setup = {}
            combined = ['matter',] if self.combined_var.get() else []
        #print('combined species', combined)

        #print('interaction setup', int_setup)
        self.cosmo_model = cosmo.CosmologicalSetup(
                modelname, 
                optional_species=optional,
                combined_species=combined,
                interaction_setup=int_setup,
                physical=bool(self.physical_var.get()),
                derived=self.map_species_abbrv[self.derived_combobox.get()],
                a0=1
                )

        for widget in self.parameter_values.winfo_children():
            widget.destroy()
        default_units = configparser.ConfigParser()
        default_units.read([
            os.path.join(root, 'cosmology', 'default_parameter_units.ini'),
            os.path.join(root, 'modifications', 'cosmology',
                'default_parameter_units.ini'),
            ])
        self.free_parameters = list(filter(lambda p: isinstance(p, cosmo.FreeParameter), 
            self.cosmo_model.parameters))
        sep = int(ceil(len(self.free_parameters)/2))
        for i, par in enumerate(self.free_parameters):
            col = 0 if i < sep else 2
            EPIC_widgets.MyTextLabel(self.parameter_values,
                    self.map_parameters[par.label], background=self.frame_bg
                    ).grid(row=i % sep, column=col, sticky=tk.E,
                            **self.default_xpadding)
            par.entry_var = tk.DoubleVar()
            par.entry_var.set(par.default)
            par.entry_frame = ttk.Frame(self.parameter_values)
            par.entry_frame.grid(row=i % sep, column=col+1, sticky=tk.W)
            ttk.Entry(par.entry_frame, width=6, font=('Times', 
                16-EPIC_widgets.platform_reduce_font_parameter),
                    textvariable=par.entry_var).pack(side=tk.LEFT, anchor=tk.W)

            if par.label in default_units['DEFAULT']:
                org_unit_lbl = default_units['DEFAULT'][par.label]
                unit_label = parse_unit(org_unit_lbl, latex=True)
                EPIC_widgets.MyTextLabel(par.entry_frame, unit_label,
                        background=self.frame_bg, justify=tk.LEFT,
                        width=round(2 + 1.2*len(
                            org_unit_lbl.replace(' ', '').replace('^', '')
                            ))).pack(side=tk.LEFT, anchor=tk.W,
                                    **self.default_xpadding)

        for x in range(4):
            self.parameter_values.rowconfigure(x, weight=1)
        for y in range(4):
            self.parameter_values.columnconfigure(y, weight=1)

        self.variable_eos = {}
        for key, species in self.cosmo_model.species.items():
            if species.EoS.type == 'woa':
                self.variable_eos[key] = species

        if len(self.variable_eos):
            self.model_results_checkbuttons_dict['Equation of state'].config(
                    state=tk.NORMAL)
        else:
            if self.model_results_checkbuttons_var['Equation of state'].get():
                self.model_results_checkbuttons_dict['Equation of state'].invoke()
            self.model_results_checkbuttons_dict['Equation of state'].config(
                    state=tk.DISABLED)

        config_all_widgets(self.corner_frame_buttons, state=tk.DISABLED)
        self.determine_solve_btn_state()

    def set_chosen_plot_style(self):
        style = self.style_choice.get()
        if style != self.current_style:
            self.current_style = int(style)
            style = self.styles_list[style]
            preserve_tex_options = dict(
                    (key, plt.rcParams[key]) for key in [
                        'text.usetex',
                        'text.latex.preamble',
                        'text.latex.unicode',
                        'text.latex.preview',
                        'font.family',
                        'font.size'
                        ]
                    )
            plt.rcdefaults()
            plt.style.use(style.replace(' ', '_'))
            self.rccustom()
            plt.rcParams.update(preserve_tex_options)

            self.remake_plots()

    def remake_plots(self):
        self.master.config(cursor='exchange')
        self.master.update()

        viewing = getattr(self, 'viewing', None)
        if viewing == 'plots':
            self.show_densities()
        elif viewing == 'dist':
            self.compare_distances(models=self.all_models,
                    labels=self.all_labels)
        else:
            pass

        self.master.config(cursor='left_ptr')

    def hide_distance_comparison_tabs(self):
        for tab in self.distance_comparison_tabs_dict.values():
            try:
                tabid = tab.winfo_pathname(tab.winfo_id())
                if self.visible_tab(tabid):
                    self.plots_notebook.hide(tab)
            except tk.TclError:
                pass
                
    def calculate_at_z(self):
        z = self.z_var.get()
        try:
            parameters = dict((par.label, par.entry_var.get()) \
                for par in self.free_parameters)
        except tk.TclError:
            messagebox.showerror('Error', 'Invalid float value.')
            return None

        da = self.cosmo_model.d_a(z, parameter_space=parameters)
        D_H = self.cosmo_model.D_H(z, parameter_space=parameters)
        Vave = (da**2 * z * D_H)**(1/3)
        age_z = self.cosmo_model.get_age_of_the_universe(z,
                parameter_space=parameters)
        sep = '; '
        self.status_bar.config(
                text=self.map_model[self.cosmo_model.model] \
                        + ' - ' + 'At z = %s: ' % str(z) +
                sep.join([
                    'Age of the universe: %.2f Gyr' % age_z,
                    'Comoving distance: %.2f Mpc' % da,
                    #'Comoving luminosity distance: %.2f Mpc' % (da * (1+z)**2),
                    #'Comoving Hubble distance: %.2f Mpc' % (D_H*(1+z)),
                    #'Comoving volume averaged distance: %.2f Mpc' % (Vave*(1+z)),
                    #'Volume averaged distance: %.2f Mpc' % Vave,
                    'Angular diameter distance: %.2f Mpc' % (da * self.cosmo_model.a0 / (1+z)),
                    'Luminosity distance: %.2f Mpc' % (da * (1+z) / self.cosmo_model.a0),
                    'Hubble distance: %.2f Mpc' % D_H,
                    ]) + '.'
                )

    def get_cosmo_solution(self):
        try:
            parameters = dict((par.label, par.entry_var.get()) \
                for par in self.free_parameters)
        except tk.TclError:
            messagebox.showerror('Error', 'Invalid float value.')
            return None

        self.status_bar.config(text='Calculating...')
        self.master.config(cursor='watch')
        self.master.update()

        self.hide_distance_comparison_tabs()

        # get results
        self.cosmo_model.solve_background(parameter_space=parameters)
        age = self.cosmo_model.get_age_of_the_universe(0,
                parameter_space=parameters)
        if age:
            self.age_label.config(
                    text='Age of the universe today:\n%.3f Gyr.' % age)

        hubble = self.cosmo_model.HubbleParameter.get_value(
                parameter_space=parameters)
        rho_cr0 = cosmo.rho_critical_SI(hubble * \
                (100 if self.cosmo_model.physical_density_parameters else 1)) 
        
        self.cosmo_model.results = OrderedDict()
        self.cosmo_model.model_solution_plots_shown = []
        title = ' '.join([
            self.available_models[self.cosmo_model.model].get('tex',
                self.map_model[self.cosmo_model.model]).replace('text', 'rm'),
            'model'
        ])

        if self.show_tab('Density parameters'):
            self.cosmo_model.results['Density parameters'] = { 
                    'x': self.cosmo_model.a_range,
                    'ydict': self.cosmo_model.background_solution_Omegas,
                    'title': title,
                    'map_species': self.map_species_abbrv,
                    }
            self.cosmo_model.model_solution_plots_shown.append(
                    self.model_solution_tabs_dict['Density parameters'].winfo_name()
                    )

        if self.show_tab('Energy densities'):
            self.cosmo_model.results['Energy densities'] = {
                    'x': self.cosmo_model.a_range,
                    'ydict': self.cosmo_model.background_solution_rhos,
                    'exclude': ['total',],
                    'factor': rho_cr0 * (hubble**-2 \
                            if self.cosmo_model.physical_density_parameters else 1),
                    'title': title,
                    'map_species': self.map_species_abbrv,
                    }
            self.cosmo_model.model_solution_plots_shown.append(
                    self.model_solution_tabs_dict['Energy densities'].winfo_name()
                    )

        man = multiprocessing.Manager()
        distances_mdict = man.dict()
        jobs = []

        if self.show_tab('Distances'):
            self.cosmo_model.model_solution_plots_shown.extend(
                    [self.model_solution_tabs_dict[w].winfo_name() \
                        for w in [
                            #'Comoving distances',
                            'Distances',
                            'Lookback time'
                            ]])
            logzmax = self.zrange_combobox.current()+1
            if logzmax == 1:
                z_range = linspace(0, 5, 500)
            else:
                z_range = logspace(-logzmax, min(logzmax, 
                    log10(cosmo.z_of_a(self.cosmo_model.a_range[0]))), 500)

            for function, key in [
                    (self.cosmo_model.d_a, 'Comoving angular distance'),
                    (self.cosmo_model.D_H, 'Hubble distance'),
                    (self.cosmo_model.get_lookback_time, 'Lookback time'),
                    (self.cosmo_model.get_age_of_various_z, 'Age of the universe'),
                    ]:
                jobs.append(
                        multiprocessing.Process(
                            target=get_function_mp,
                            args=(function, key, distances_mdict, z_range),
                            kwargs={'parameter_space': parameters},
                            )
                        )


        if self.show_tab('Equation of state'):
            self.cosmo_model.model_solution_plots_shown.append(
                    self.model_solution_tabs_dict['Equation of state'].winfo_name()
                    )
            eos_mdict = man.dict()
            for key, species in self.variable_eos.items():
                jobs.append(
                        multiprocessing.Process(
                            target=get_function_mp,
                            args=(species.EoS.w_of_a, key, eos_mdict,
                                self.cosmo_model.a_range),
                            kwargs={'a0': self.cosmo_model.a0,
                                'parameter_space': parameters},
                            )
                        )

        for j in jobs:
            j.start()
        for j in jobs:
            j.join()
                        
        if self.show_tab('Distances'):
            distances_mdict['Comoving luminosity distance'] = \
                    distances_mdict['Comoving angular distance'] * (1+z_range)**2

            #distances_mdict['Volume averaged distance'] = \
            #        (distances_mdict['Comoving angular distance']**2 * z_range \
            #        * distances_mdict['Hubble distance'])**(1/3)

            #distances_mdict['Comoving volume averaged distance'] = \
            #        distances_mdict['Volume averaged distance']*(1+z_range)

            #distances_mdict['Comoving Hubble distance'] = \
            #        distances_mdict['Hubble distance']*(1+z_range)

            #distances_mdict['Comoving lookback time'] = \
            #        distances_mdict['Lookback time']*(1+z_range)


            distances_mdict['Angular distance'] = \
                    distances_mdict['Comoving angular distance']/(1+z_range)

            distances_mdict['Luminosity distance'] = \
                    distances_mdict['Comoving luminosity distance']/(1+z_range)

            #######################

            #H0_distance = self.cosmo_model.HubbleParameter.entry_var.get() \
            #        * (100 if self.cosmo_model.physical_density_parameters else 1)
            #distances_mdict['Adimensional angular distance'] = \
            #        distances_mdict['Angular distance']\
            #        / H0_distance # /distances_mdict['Hubble distance']

            #distances_mdict['Adimensional luminosity distance'] = \
            #        distances_mdict['Luminosity distance'] \
            #        / H0_distance # /distances_mdict['Hubble distance']

            #distances_mdict['Adimensional volume averaged distance'] = \
            #        distances_mdict['Volume averaged distance'] \
            #        / H0_distance # /distances_mdict['Hubble distance']

            #distances_mdict['Adimensional lookback time'] = \
            #        distances_mdict['Lookback time'] \
            #        / H0_distance # /distances_mdict['Hubble distance']

            self.cosmo_model.results.update(
                    OrderedDict([
                        #('Comoving distances', {
                        #    'x' : z_range,
                        #    'ydict': OrderedDict([
                        #        ('Angular diameter $d_A(z)$',
                        #            distances_mdict['Comoving angular distance']),
                        #        #('Volume averaged $d_V(z)$',
                        #        #    distances_mdict['Comoving volume averaged distance']),
                        #        ('Hubble $d_H(z)$',
                        #            distances_mdict['Comoving Hubble distance']),
                        #        (r'Lookback time $c\,t(z)\left(1+z\right)$', 
                        #            distances_mdict['Comoving lookback time']\
                        #                    *speedoflight/1e3/976.480247152),
                        #        ]), 
                        #    'ysecond': OrderedDict([
                        #        ('Luminosity $d_L(z)$',
                        #            distances_mdict['Comoving luminosity distance']),
                        #        ]),
                        #    'title': title,
                        #    'map_species': self.map_species_abbrv,
                        #    'sec_weights': [2, 1],
                        #    }),
                        ('Distances', {
                            'x': z_range,
                            'ydict': OrderedDict([
                                ('Comoving distance $\chi(z)$',
                                    distances_mdict['Comoving angular distance']),
                                ('Angular diameter $d_A(z)$',
                                    distances_mdict['Angular distance']),
                                #('Volume averaged $d_V(z)$',
                                #    distances_mdict['Volume averaged distance']),
                                ('Hubble $d_H(z)$', 
                                    distances_mdict['Hubble distance']),
                                ('Lookback time $c\,t(z)$',
                                    distances_mdict['Lookback time']\
                                            *speedoflight/1e3/976.480247152),
                                ]),
                            'ysecond': OrderedDict([
                                ('Luminosity $d_L(z)$',
                                    distances_mdict['Luminosity distance']),
                                ]),
                            'title': title,
                            'map_species': self.map_species_abbrv,
                            'sec_weights': [2, 1],
                            }),
                        #('Adimensional distances', {
                        #    'x': z_range,
                        #    'ydict': OrderedDict([
                        #        ('Angular diameter $d_A(z)/d_H(z)$',
                        #            distances_mdict['Adimensional angular distance']),
                        #        ('Volume averaged $d_V(z)/d_H(z)$',
                        #            distances_mdict['Adimensional volume averaged distance']),
                        #        (r'Lookback time $c\,t(z)/d_H(z)$',
                        #            distances_mdict['Adimensional lookback time']\
                        #                    *speedoflight/1e3/976.480247152),
                        #        ]),
                        #    'ysecond': OrderedDict([
                        #        ('Luminosity $d_L(z)/d_H(z)$',
                        #            distances_mdict['Adimensional luminosity distance']),
                        #        ]),
                        #    'title': title,
                        #    'map_species': self.map_species_abbrv,
                        #    'sec_weights': [2, 1],
                        #    }),
                        ('Lookback time', {
                            'x': z_range, 
                            'ydict': OrderedDict([
                                ('Lookback time', distances_mdict['Lookback time']),
                                ('Age of the universe', distances_mdict['Age of the universe']),
                                ]),
                            'title': title,
                            }),
                        ])
                    )

        if self.show_tab('Equation of state'):
            self.cosmo_model.results.update(OrderedDict([
                ('Equation of state', {
                    'x': self.cosmo_model.a_range,
                    'ydict': eos_mdict,
                    'title': title,
                    'map_species': self.map_species_abbrv,
                    }),
                ]),
            )

        self.show_densities()
        config_all_widgets(self.corner_frame_buttons, state=tk.NORMAL)
        if self.show_tab('Distances'):
            self.add_model_to_list(self.cosmo_model, parameters)
        self.master.config(cursor='left_ptr')

    def add_model_to_list(self, model, parameter_space):
        model.calculated_point = parameter_space
        model_abbrv = model_abbrevation(self.map_model[model.model])
        if model in self.list_of_solved_models:
            i = self.list_of_solved_models.index(model)
            self.saved_models_listbox.delete(i)
            self.saved_models_listbox.insert(i, model_abbrv)
        else:
            config_all_widgets(self.saved_models_frame, state=tk.NORMAL)
            self.list_of_solved_models.append(model)
            self.saved_models_listbox.insert(tk.END, model_abbrv)

    def set_and_update_gif(self):
        model = self.map_model[self.model_options_combobox.get()]
        species = self.map_species_abbrv[self.interaction_propto_options.get()]
        sign = self.int_sign_combobox.get()
        if species == self.please_select_species or sign == '(sign)':
            img = tk.PhotoImage(file=os.path.join(root, 'gui_files',
                'blank.gif'))
            self.img_lbl.config(image=img)
            self.img_lbl.image = img
            return None
        if species == 'idm':
            if model == 'cde':
                img = tk.PhotoImage(file=os.path.join(root, 'gui_files',
                    'cde_propto_c_%s.gif' % sign))
            else:
                assert model == 'cde lambda'
                img = tk.PhotoImage(file=os.path.join(root, 'gui_files',
                    'ilambda_propto_c_%s.gif' % sign))
        elif species == 'ilambda':
            img = tk.PhotoImage(file=os.path.join(root, 'gui_files',
                'ilambda_propto_de_%s.gif' % sign))
        else:
            assert species == 'ide'
            img = tk.PhotoImage(file=os.path.join(root, 'gui_files',
                'cde_propto_de_%s.gif' % sign))
        self.img_lbl.config(image=img)
        self.img_lbl.image = img

    def show_optional_species(self, event):
        model = event.widget.get()
        model = self.map_model[model]
        self.mandatory_msg.config(text=self.please_select_model+'\n')
        self.optional_species_listbox.delete(0, tk.END)
        no_model = model == self.please_select_model
        cde_state = tk.NORMAL if 'cde' in model else tk.DISABLED
        cde_state_inverse = tk.DISABLED if 'cde' in model else tk.NORMAL
        config_all_widgets(self.darksector_and_build_frame,
                state=tk.DISABLED if no_model else tk.NORMAL)
        if no_model:
            img = tk.PhotoImage(file=os.path.join(root, 'gui_files',
                'blank.gif'))
            self.img_lbl.config(image=img)
            self.img_lbl.image = img
            self.derived_combobox['values'] = [self.please_select_species,]
            self.derived_combobox.current(0)
            self.derived_combobox.config(state=tk.DISABLED)
            self.derived_lbl.config(state=tk.DISABLED)
            return None

        # map species label and name
        self.map_species = OrderedDict([
                (self.please_select_model+'\n', self.please_select_model+'\n'),
                (self.please_select_species, self.please_select_species),
                ])
        self.map_species_abbrv = OrderedDict([
                (self.please_select_species, self.please_select_species),
                ])
        self.mandatory_species = eval(self.available_models[model]['mandatory species'])
        self.optional_species = eval(self.available_models[model]['supported optional species'])
        self.combined_species = eval(self.available_models[model].get('supported composed species', '[]'))
        for species in self.mandatory_species + self.optional_species + self.combined_species:
            name = self.available_species['name'].get(species)
            abbrv = self.available_species['abbreviation'].get(species, None)
            if abbrv:
                abbrv = abbrv.replace(r'$\Lambda$', 'Λ')
            self.map_species_abbrv[species] = abbrv or name
            abbrv = '' if abbrv is None else ' (%s)' % abbrv
            self.map_species[species] = name + abbrv
        remap(self.map_species_abbrv)
        remap(self.map_species)

        self.mandatory_msg.config(text='\n'.join([self.map_species[species] \
                for species in self.mandatory_species]))
        self.derived_combobox['values'] = [self.map_species_abbrv[species] for species in self.mandatory_species]
        self.derived_combobox.current(len(self.derived_combobox['values'])-1)
        self.derived_combobox.config(state='readonly')
        self.derived_lbl.config(state=tk.NORMAL)
        if 'cde' in model:
            self.combined_var.set(0)
            self.interaction_propto_options['values'] = [self.please_select_species,] + [self.map_species_abbrv[species] \
                    for species in self.mandatory_species]
        else:
            self.interaction_propto_options['values'] = [self.please_select_species,]
        self.interaction_propto_options.current(0)
        self.combined_option.config(state=cde_state_inverse)
        self.int_propto_label.config(state=cde_state)
        config_all_widgets(self.int_frame, state=cde_state)
        for option in self.optional_species:
            self.optional_species_listbox.insert(tk.END, self.map_species[option])

        img = tk.PhotoImage(file=os.path.join(root, 'gui_files', 'blank.gif'))
        if model == 'lcdm':
            img = tk.PhotoImage(file=os.path.join(root, 'gui_files',
                'lcdm.gif'))
        elif model in ['wcdm', 'cpl', 'ba', 'fv1', 'fv2', 'fv3']:
            img = tk.PhotoImage(file=os.path.join(root, 'gui_files',
                'wde.gif'))
        self.img_lbl.config(image=img)
        self.img_lbl.image = img

    def show_tab(self, tab):
        return self.model_results_checkbuttons_var[tab].get() 

    def show_densities(self):

        if not hasattr(self, 'cosmo_model'):
            return None

        if not hasattr(self.cosmo_model, 'results'):
            return None 

        self.status_bar.config(text='Plotting...')
        self.status_bar.update()

        for plot_name, instructions in self.cosmo_model.results.items():
            self.model_solution_tabs_dict[plot_name].add_figure_to_widget(
                    **instructions)

        self.viewing = 'plots'
        self.status_bar.config(text='Done.')

def remap(d):
    d.update({v: k for k, v in d.items() if k != v})
        
def launch_gui(args):
    plt.rcdefaults()
    master = tk.Tk()
    app = Application(master=master, theme=args.theme)
    master.update_idletasks()
    w = master.winfo_width()
    h = master.winfo_height()
    W = master.winfo_screenwidth()
    H = master.winfo_screenheight()
    x = W//2 - w//2
    y = H//2 - h//2
    master.geometry('{}x{}+{}+{}'.format(w, h, x, y))
    master.mainloop()

def get_function_mp(model_d, key, shared_dict, z, **kwargs):
    factor = kwargs.pop('factor', 1)
    shared_dict[key] = factor * model_d(z, **kwargs)

def select_first_visible(nb):
    for tab in nb.tabs():
        if nb.tab(tab)['state'] == 'normal':
            nb.select(tab)
            return None

def config_all_widgets(w, **kwargs):
    for widget in w.winfo_children():
        try:
            widget.config(**kwargs)
            if isinstance(widget, EPIC_widgets.ReadonlyCombobox):
                if kwargs.get('state') == tk.NORMAL:
                    widget.config(state='readonly')
        except tk.TclError:
            pass
        config_all_widgets(widget, **kwargs)

def model_abbrevation(name):
    abbrv = name.split('(', 1)
    if len(abbrv) == 1:
        return abbrv[0]
    return abbrv[1].split(')')[0]
