import os
from numpy import savetxt, log10, average, allclose
import itertools
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import NavigationToolbar2Tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import matplotlib.gridspec as gridspec
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from EPIC import root
from EPIC.utils.io_tools import parse_tex, split_last
import platform

if platform.system() == 'Windows':
    platform_reduce_font_parameter = 4
    pixels_to_char_size = 6
else:
    platform_reduce_font_parameter = 0
    pixels_to_char_size = 8

class ReadonlyCombobox(ttk.Combobox):
    def __init__(self, *args, state='readonly', **kwargs):
        super().__init__(*args, state=state, style='Readonly.TCombobox',
                **kwargs)
        self.bind('<<ComboboxSelected>>', 
                func=(lambda _ : self.selection_clear()))

class Separator(tk.Frame):
    pass

class ListboxEditable(tk.Listbox):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.bind('<Double-Button-1>', self.edit)

    def edit(self, editevent=None):
        if len(self.curselection()) > 1:
            return None
        index = self.curselection()[0]
        x, y, _, h = self.bbox(index)
        entry_var = tk.StringVar()
        entry_var.set(self.get(index))
        self.entry = ttk.Entry(self, text=entry_var)
        extraheight = 4
        self.entry.place(x=x-2, y=y-2-extraheight//2,
                width=self.winfo_width()-self['borderwidth']-self['highlightthickness']-1,
                height=h+extraheight)
        self.entry.bind('<Return>', (lambda event: self.rename(index, entry_var.get())))
        self.entry.select_range(0, tk.END)
        self.entry.config(validate='focusout')
        self.entry.config(validatecommand=(lambda: self.rename(index, entry_var.get())))
        self.entry.icursor(tk.END)
        self.entry.focus()

    def rename(self, index, newtext):
        self.delete(index)
        self.insert(index, newtext)
        self.entry.destroy()

class TwoPanes(ttk.PanedWindow):
    def __init__(self, *args, label=None, labelstyle='TLabel',
            framestyle='TFrame', **kwargs):
        super().__init__(*args, **kwargs)
        orient = kwargs.get('orient', tk.VERTICAL)
        self.main = ttk.Frame(self, style=framestyle)
        self.second = ttk.Frame(self, style=framestyle)
        self.add(self.main, weight=1)
        self.add(self.second)
        if label:
            ttk.Label(self.second, style=labelstyle, text=label).pack(
                    side=tk.TOP if orient == tk.VERTICAL else tk.LEFT)
        self.pack(fill=tk.BOTH, expand=1)

class MyNavigationToolbar(NavigationToolbar2Tk):

    MS_LW = 3 # markersize in units of linewidth
    line_styles = ['-', '--', '-.', ':']
    marker_styles = ['', 'o', 's', 'x', '*', '^', 'd']

    def __init__(self, canvas, parent, parent_figframe, plot_name,
            xscale_toggle=False, yscale_toggle=False, difference_toggle=False,
            **kwargs):
        self.plot_name = plot_name
        self.gridstyles = itertools.cycle([(0.5, '--'), (0.5, ':'), (0, ''),
            (1, '-'), (0.5, '-')])
        self.linewidths = itertools.cycle([0.5, 1, 1.5, 2])
        # icons are stored in
        # lib/python3.x/site-packages/matplotlib/mpl-data/images
        buttons = [
                ('Home', 'Reset original view', 'home', 'home'),
                ('Zoom', 'Zoom to rectangle', 'zoom_to_rect', 'zoom'),
                ('Pan', 'Pan axes with left click, zoom with right click', 
                    'move', 'pan'),
                (None, None, None, None),
                ]

        if xscale_toggle:
            buttons.append(
                    ('Toggle scale', 'Toggle x-axis scale (linear/log)',
                        'xscale', 'toggle_scale_xaxis')
                )
        if yscale_toggle:
            buttons.append(
                    ('Toggle scale', 'Toggle y-axis scale (linear/log)',
                        'yscale', 'toggle_scale_yaxis')
                )
        if xscale_toggle or yscale_toggle:
            buttons.append(
                    (None, None, None, None)
                )

        if difference_toggle:
            buttons.extend([
                    ('Residual', 'Show/hide fractional difference', 'residual',
                        'show_hide_difference_plot'),
                    (None, None, None, None)
                ])

        buttons.extend([
            ('Change grid', 'Change grid style (thick/solid/dashed/dotted/off)',
                'change_grid', 'change_grid'),
            ('Change line width', 'Change line widths (0.5/1.0/1.5/2.0)',
                'line_width', 'change_line_width'),
            ('Toggle color mode', 'Toggle line mode (colors/styles)', 'color_mode',
                'toggle_color_mode'),
            ('Change legend', 'Change legend (off/on/on+title)', 'legend',
                'change_legend'),
            (None, None, None, None),
            ('Save', 'Save the figure and data files', 'filesave',
                'save_figure'),
            ])
                
        self.toolitems = tuple(buttons)
        super().__init__(canvas, parent, **kwargs)
        self.parent_figframe = parent_figframe

    def _Spacer(self):
        s = Separator(
            master=self, height=21, relief=tk.RIDGE, pady=2, bg='#dddddd')
        s.pack(side=tk.LEFT, padx=8)
        return s

    def _Button(self, text, file, command, extension=None):
        if extension is None:
            extension = '.png' if tk.TkVersion >= 8.6 else '.gif'
        img_file = os.path.join(root, 'gui_files', 'images', file + extension)
        im = tk.PhotoImage(master=self, file=img_file)
        b = ttk.Button(self, text=text, style='White.Flat.TButton', image=im,
                command=command)
        b._ntimage = im
        b.pack(side=tk.LEFT)
        return b

    def show_hide_difference_plot(self):
        fig, ax = self.get_figure()
        if len(ax) == 0:
            return None
        elif len(ax) == 1:
            self.show_difference_plot(fig, ax[0])
        else:
            self.hide_difference_plot(fig, ax)

    def hide_difference_plot(self, fig, ax):
        xlabel = ax[1].get_xlabel()
        fig.delaxes(ax[1])
        ax[0].tick_params(axis='x', which='both', direction='out', top=False,
                bottom=True)
        ax[0].tick_params(axis='y', which='both', direction='out', left=True,
                right=False)
        ax[0].set_xlabel(xlabel)
        gs = gridspec.GridSpec(1, 1)
        ax[0].set_position(gs[0].get_position(fig))
        ax[0].set_subplotspec(gs[0])
        #fig.tight_layout()
        self.update_figure()

    def show_difference_plot(self, fig, ax):
        xscale = ax.get_xscale()
        yscale = ax.get_yscale()
        xlabel = ax.get_xlabel()
        ylabel = ax.get_ylabel()
        grid = {
                'state': ax.xaxis._gridOnMajor or ax.xaxis._gridOnMinor \
                        or ax.yaxis._gridOnMajor or ax.yaxis._gridOnMinor,
                'lw': ax.xaxis.get_gridlines()[0].get_linewidth(),
                'ls': ax.xaxis.get_gridlines()[0].get_linestyle(),
            }
        legend, size, title = self.get_legend_settings(ax)
        originals = []
        for line in ax.lines:
            x, y = line.get_data()
            properties = line.properties()
            for prop in [
                    'agg_filter', 'animated', 'children', 'clip_box',
                    'clip_on', 'clip_path', 'contains', 'data', 'drawstyle',
                    'figure', 'gid', 'path', 'path_effects', 'picker',
                    'pickradius', 'rasterized', 'sketch_params', 'snap',
                    'solid_capstyle', 'solid_jointstyle', 'transform',
                    'transformed_clip_path_and_affine', 'url', 'visible',
                    'xdata', 'ydata', 'xydata', 
                    ]:
                properties.pop(prop, None)
            originals.append((x, y, properties))
        line0_label = ax.lines[0].get_label()

        for data_info in originals:
            if not allclose(originals[0][0], data_info[0]):
                messagebox.showerror('Error', 'Use the same redshift ranges to calculate distance percentage differences.')
                return None

        reset_figure(fig, **self.parent_figframe.figproperties)
        gs = gridspec.GridSpec(2, 1, height_ratios=[3, 1])
        gs.update(hspace=0)
        main = fig.add_subplot(gs[0])
        res = fig.add_subplot(gs[1], sharex=main)
        main.format_coord = lambda X, Y: format_coord(main, X, Y) 
        res.format_coord = lambda X, Y: format_coord(res, X, Y) 
        for data_info in originals:
            x, y, properties = data_info
            main.plot(x, y, **properties)
            res.plot(x, y/originals[0][1] - 1, **properties)
        main.set_xscale(xscale)
        main.set_yscale(yscale)
        res.set_xscale(xscale)
        res.set_yscale('linear')
        main.set_ylabel(ylabel)
        main.set_xlabel(xlabel)
        res.set_xlabel(xlabel)
        res_ylabel = residual_label(ylabel, line0_label)
        if plt.rcParams['text.usetex']:
            res_ylabel = res_ylabel.replace(r'\rm', r'\text')
        else:
            if '$' in line0_label:
                if line0_label.startswith('$'):
                    sep_rm, l0label = line0_label.lstrip('$').split('$', 1)
                    res_ylabel = res_ylabel.replace(r'\rm{' + line0_label, 
                            sep_rm + r'\rm{' + l0label) 
                if line0_label.endswith('$'):
                    l0label, sep_rm = split_last(line0_label.rstrip('$'), sep='$')
                    res_ylabel = res_ylabel.replace(line0_label + '}', 
                            l0label + '}' + sep_rm)
                if (not line0_label.startswith('$')) \
                        and (not line0_label.endswith('$')):
                    a, l0label, b = line0_label.split('$', 2)
                    res_ylabel = res_ylabel.replace(line0_label,
                            a + '}' + l0label + r'\rm{' + b)
            res_ylabel = res_ylabel.replace(' ', r'}\,\rm{')
        res.set_ylabel(res_ylabel)
        if grid['state']:
            for axes in [main, res]:
                axes.grid(which='minor', alpha=self.parent_figframe.ALPHA_MINOR,
                        linestyle=grid['ls'], linewidth=grid['lw'])
                axes.grid(which='major', alpha=self.parent_figframe.ALPHA_MAJOR,
                        linestyle=grid['ls'], linewidth=grid['lw'])
                axes.tick_params(axis='x', which='both', direction='in', top=True,
                        bottom=True)
                axes.tick_params(axis='y', which='both', direction='in', left=True,
                        right=True)
        if legend:
            self.set_legend_settings(main, size, title)
        #fig.tight_layout()
        fig.align_ylabels()
        self.update_figure()

    def get_figure(self):
        fig = self.canvas.figure
        return fig, fig.get_axes()

    def update_figure(self):
        self.canvas.draw()
        self.update()

    def save_figure(self):
        fig, ax = self.get_figure()
        if len(ax) == 0:
            return None
        xdata_name = extract_label(ax[0].get_xlabel()).replace('$', '')
        ydata_name = extract_label(ax[0].get_ylabel()).replace('$', '')

        local = filedialog.askdirectory()
        if local:
            for line in ax[0].get_lines():
                untex_label = line.get_label().replace(r'$\Lambda$', 'Λ')
                line_label = self.map_species.get(untex_label, untex_label) \
                        if hasattr(self, 'map_species') else untex_label
                savetxt(
                        os.path.join(local,
                            '{0}_{1}.txt'.format(self.plot_name,
                                split_last(line_label)[0]).replace(' ', '_')
                            ),
                        line.get_xydata(),
                        header='{0} plot, data for {1} curve: {2}, {3}'.format(
                            self.plot_name, line_label, xdata_name, ydata_name)
                    )
            img_name = os.path.join(local,
                '{0}_plot'.format(self.plot_name).replace(' ',
                    '_').replace('$', ''))
            fig.savefig(img_name + '.pdf')
            fig.savefig(img_name + '.png', dpi=180)
            messagebox.showinfo('OK!', 'Files saved in %s' % local)

    def change_line_width(self):
        fig, axes = self.get_figure()
        if len(axes) == 0:
            return None
        width = next(self.linewidths)
        
        for ax in axes:
            legend, size, title = self.get_legend_settings(ax)

            for line in ax.get_lines():
                line.set_linewidth(width)
                line.set_markersize(self.MS_LW*width)

            if legend:
                self.set_legend_settings(ax, size, title)

        self.update_figure()

    def get_legend_settings(self, ax):
        legend = ax.get_legend()
        if legend:
            size = legend._fontsize
            title = legend.get_title().get_text()
            return legend, size, title
        return None, None, None

    def set_legend_settings(self, ax, size, title):
        ncol = len(ax.lines)//6+1
        if title == 'None':
            ax.legend(fontsize=size, ncol=ncol)
        else:
            ax.legend(fontsize=size, title=title, ncol=ncol)
            plt.setp(ax.legend_.get_title(), fontsize=size)

    def change_legend(self):
        fig, axes = self.get_figure()
        if len(axes) == 0:
            return None
        ax = axes[0]
        legend = ax.get_legend()
        ncol = len(ax.lines)//6+1
        if legend:
            title = legend.get_title().get_text()
            if title == 'None':
                ax.legend(title=self.legend_title, fontsize=self.legend_size, ncol=ncol)
                plt.setp(ax.legend_.get_title(), fontsize=self.legend_size)
            else:
                self.legend_title = title
                self.legend_size = legend._fontsize
                legend.remove()
        else:
            ax.legend(fontsize=self.legend_size, ncol=ncol)
        self.update_figure()

    def toggle_scale_xaxis(self, axis='x'):
        fig, ax = self.get_figure()
        if len(ax) == 0:
            return None
        log_scale = getattr(ax[0], 'get_%sscale' % axis)() == 'log'
        getattr(ax[0], 'set_%sscale' % axis)('linear' if log_scale else 'log')
        self.update_figure()

    def toggle_scale_yaxis(self):
        self.toggle_scale_xaxis(axis='y')

    def change_grid(self):
        fig, axes = self.get_figure()
        if len(axes) == 0:
            return None
        width, style = next(self.gridstyles)
        for ax in axes:
            ax.grid(bool(style), which='minor', linestyle=style,
                    linewidth=width, alpha=self.parent_figframe.ALPHA_MINOR)
            ax.grid(bool(style), which='major', linestyle=style,
                    linewidth=width, alpha=self.parent_figframe.ALPHA_MAJOR)
            ax.set_axisbelow(True)
        self.update_figure()

    def toggle_color_mode(self):
        fig, axes = self.get_figure()
        if len(axes) == 0:
            return None
        for ax in axes:
            linestyles = itertools.product(self.marker_styles, self.line_styles)
            linestyles = itertools.cycle(linestyles)
            legend, size, title = self.get_legend_settings(ax)
            previous_colors = [line.get_c() for line in ax.lines]
            if all([color == plt.rcParams['axes.labelcolor'] \
                    for color in previous_colors]):
                for line, color in zip(ax.lines, self.previous_colors):
                    line.set_c(color)
                    line.set_linestyle('-')
                    line.set_marker('')
            else:
                self.previous_colors = previous_colors
                for line, style in zip(ax.lines, linestyles):
                    mk, sty = style
                    line.set_c(plt.rcParams['axes.labelcolor'])
                    line.set_linestyle(sty)
                    line.set_marker(mk)
                    lw = line.get_linewidth()
                    line.set_markersize(self.MS_LW*lw)
                    line.set_markevery(len(line.get_ydata()) // 20)
            if legend:
                self.set_legend_settings(ax, size, title)
        self.update_figure()

class FigureFrame(ttk.Frame):

    #pts_to_in = 0.04167/3
    figproperties = {
            #'dpi': 100,
            'tight_layout': True,
            'constrained_layout': False,#{
            #        'w_pad': 12 * pts_to_in,
            #        'h_pad': 12 * pts_to_in,
            #        },
            }

    ALPHA_MINOR = 0.4
    ALPHA_MAJOR = 0.8

    def __init__(self, *args, plot_name=None, xlabel=None, ylabel=None,
            yscale='linear', xscale_toggle=False,
            yscale_toggle=False, difference_toggle=False, bg=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.yscale = yscale
        self.xlabel = xlabel
        self.ylabel = ylabel
        self.figure()

        nav_pane = ttk.Frame(self)
        nav_pane.pack(side=tk.BOTTOM, anchor=tk.S, fill=tk.X, expand=0)
        sup_pane = ttk.Frame(self)
        sup_pane.pack(side=tk.TOP, fill=tk.BOTH, expand=1)

        v_panes = TwoPanes(sup_pane, label='\u2195 Drag the borders to resize plot \u2195',
                labelstyle='TLabel', framestyle='White.TFrame')
        h_panes = TwoPanes(v_panes.main, label='\u2194', orient=tk.HORIZONTAL,
                labelstyle='TLabel', framestyle='White.TFrame')

        self.canvas = FigureCanvasTkAgg(self.fig, h_panes.main)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

        self.toolbar = MyNavigationToolbar(self.canvas, nav_pane,
                self, plot_name, xscale_toggle=xscale_toggle,
                yscale_toggle=yscale_toggle,
                difference_toggle=difference_toggle)
        paint_backgrounds(self.toolbar, background='white')
        self.toolbar.update()
        self.canvas._tkcanvas.pack(side=tk.TOP, fill=tk.BOTH, expand=1)

    def figure(self):
        self.fig = Figure(**self.figproperties)
        #if self.figproperties.get('tight_layout'):
        #    self.fig.tight_layout()

    def add_figure_to_widget(self, x, ydict, exclude=[], factor=1,
            ysecond=None, title=None, map_species={}, sec_weights=[1, 1]):

        self.toolbar.map_species = map_species
        def plot_from_dictionary(d, ax):
            for key, solution in d.items():
                if not key in exclude:
                    ax.plot(x, factor * solution, lw=2,
                            label=map_species.get(key, key).replace('Λ',
                                r'$\Lambda$'))

        reset_figure(self.fig, **self.figproperties)
        ax = self.fig.add_subplot(111)
        ax.format_coord = lambda X, Y: format_coord(ax, X, Y) 
        plot_from_dictionary(ydict, ax)
        ax.set_xscale('log' if log10(x[-1]) > 1 or self.xlabel == r'$a$' else 'linear')
        ax.set_yscale(self.yscale)
        ax.set_xlabel(self.xlabel)
        ax.set_ylabel(self.ylabel)

        if ysecond and log10(x[-1]) > 1:
            y1, y2 = ax.get_ylim()
            plot_from_dictionary(ysecond, ax)
            _, y3 = ax.get_ylim()
            ax.set_ylim(y1, 10**average(log10([y2, y3]), weights=sec_weights))

        ax.grid(which='minor', alpha=self.ALPHA_MINOR)
        ax.grid(which='major', alpha=self.ALPHA_MAJOR)
        ax.set_axisbelow(True)
        ncol = len(ax.lines)//6+1
        ax.legend(ncol=ncol, title=title)
        #fig.tight_layout()
        #plt.setp(ax.legend_.get_title(), fontsize=legend_size)
        # update figure
        self.canvas.draw()
        update_tabs()

    def add_distance_comparison_to_widget(self, plot_name, instructions,
            labels):
        reset_figure(self.fig, **self.figproperties)
        ax = self.fig.add_subplot(111)
        ax.format_coord = lambda X, Y: format_coord(ax, X, Y) 
        for inst, label in zip(instructions, labels):
            ax.plot(inst['x'], inst['ydict'].get(plot_name,
                inst.get('ysecond', {}).get(plot_name, None)), label=label)

        ax.set_xlabel(self.xlabel)
        ax.set_ylabel(self.ylabel)
        ax.set_xscale('log' if log10(inst['x'][-1]) > 1 else 'linear')
        ax.set_yscale(self.yscale)
        ncol = len(ax.lines)//6+1
        ax.legend(title='Model', ncol=ncol)

        ax.grid(which='minor', alpha=self.ALPHA_MINOR)#, linestyle='-', linewidth=0.5)
        ax.grid(which='major', alpha=self.ALPHA_MAJOR)#, linestyle='-', linewidth=0.5)
        ax.set_axisbelow(True)

        self.fig.tight_layout()
        # update figure
        self.canvas.draw()
        update_tabs()

class MyTextLabel(tk.Text):
    def __init__(self, parent, label, justify=tk.RIGHT, background=None,
            reduce_=None, width=10, **kwargs):
        reduce_ = reduce_ or platform_reduce_font_parameter
        self.script_size = 11 - reduce_
        self.regular_size = 16 - reduce_
        for attr in (
                ('relief', tk.FLAT),
                ('borderwidth', 0),
                ('highlightthickness', 0),
                ('height', 2),
                ('width', width),
                ('padx', 0),
                ):
            kwargs.__setitem__(*attr)
        super().__init__(parent, **kwargs)
        self.tag_config('times', offset=-reduce_,
                font=('Times', self.regular_size))
        self.tag_config('align', offset=-reduce_, justify=justify)
        self.tag_config('italic', offset=-reduce_,
                font=('Times', self.regular_size, 'italic'))
        self.tag_config('sub', offset=-3-reduce_,
                font=('Times', self.script_size))
        self.tag_config('subitalic', offset=-3-reduce_, font=('Times',
            self.script_size, 'italic'))
        self.tag_config('super',
                offset=3+self.regular_size-self.script_size-reduce_,
                font=('Times', self.script_size))
        self.tag_config('superitalic',
                offset=3+self.regular_size-self.script_size-reduce_,
                font=('Times', self.script_size, 'italic'))
        for piece, tag in parse_tex(label):
            self.insert(tk.END, piece, (tag, 'align'))
        if justify == tk.RIGHT:
            self.insert(tk.END, '   = ', 'times')
        self.config(state=tk.DISABLED)
        if background:
            self.config(background=background)

def paint_backgrounds(widget, background=None):
    try:
        if not isinstance(widget, Separator):
            widget.config(bg=background or 'white')#, fg=foreground)
    except tk.TclError:
        pass
    for w in widget.winfo_children():
        paint_backgrounds(w)

def reset_figure(fig, **kwargs):
    fig.__init__(figsize=fig.get_size_inches(), **kwargs)
    if kwargs.get('tight_layout'):
        fig.tight_layout()

def residual_label(label, ref):
    res = split_last(label, ',\\')[0].strip('$')
    return r'$\frac{' + res + '}{' + res + r'_{\rm{' + ref + '}}}-1$'

def extract_label(data_label):
    xdata_unit = data_label.strip('$').split('$', 1)
    if len(xdata_unit) > 1:
        xname, xunit = xdata_unit
        return ' '.join([xname, xunit.strip()])
    return xdata_unit[0].strip()

def format_with_unit(name, value):
    # in case unit is '' the spaces will be stripped
    return '{0} = {2} {1}'.format(*name, value).strip()

def axislabel_replacements(self, replacement_list):
    for o, n in replacement_list:
        self = self.replace(o, n)
    return self.strip()

def format_label(label):
    name_unit = label.split('[')
    if len(name_unit) > 1:
        name, unit = name_unit
        unit = unit.split(']')[0]
        unit = axislabel_replacements(unit,
                [('\\rm{', ''), ('}', ''), ('^3', '³'), ('\\,', '')])
    else:
        name, unit = name_unit[0], ''
    name = name.strip('$').split('(')[0].split('_')[0]
    name = axislabel_replacements(name, 
            [('\\rho', 'ρ'), ('\\Omega', 'Ω'), ('\\,', '')])
    if '\\frac' in name:
        name = 'δ'
    return name, unit

def format_coord(ax, x, y):
    """Return a format string formatting the *x*, *y* coord"""
    xs = '???' if x is None else "%.5e" % x #ax.format_xdata(x).strip()
    ys = '???' if y is None else "%.5e" % y #ax.format_ydata(y).strip()
    names = [format_label(getattr(axis.get_label(), 'get_text')()) \
            for axis in ax._get_axis_list()]
    return ', '.join([format_with_unit(name, s) \
            for name, s in zip(names, [xs, ys])])

def configure_ttk(theme='clam'):
    s = ttk.Style()
    s.theme_use(theme) # alt, clam, classic, default
    frame_bg = s.lookup('TFrame', 'background')
    disabled_text = tk.Label().config('disabledforeground')[-1]
    foreground_text = tk.Label().config('foreground')[-1]
    active_bg = tk.Button().config('activebackground')[-1]
    s.map('Readonly.TCombobox',
            background=[
                ('disabled', frame_bg),
                ('active', active_bg)
                ],
            foreground=[('disabled', disabled_text)],
            fieldforeground=[('disabled', disabled_text)],
            fieldbackground=[('disabled', frame_bg)],
            )
    s.configure('Image.TLabel', borderwidth=0)
    s.configure('TButton', justify=tk.CENTER)
    s.configure('Flat.TButton', relief=tk.FLAT, padding=0)
    s.map('TLabelFrame',
            foreground=[('disabled', disabled_text)]
            )
    s.map('Flat.TButton', 
            relief=[('pressed', '!disabled', 'sunken')],
            #highlightthickness=[('active', 1)]
            )
    s.configure('White.TButton', background='white')
    s.configure('TMenubutton', arrowsize=3)
    s.configure('White.Flat.TButton', background='white')
    s.configure('White.TFrame', background='white')
    s.configure('White.TLabel', background='white')

    update_tabs()

    return frame_bg, foreground_text

def translate_pyplot_color(name):
    try:
        c = float(name)
        c = round(c*255)
        HEX = '#%02x%02x%02x' % (c, c, c)
        return HEX
    except ValueError:
        if name == 'k':
            return 'black'
        if name == 'w':
            return 'white'
        return name

def update_tabs():
    s = ttk.Style()
    rc_bg = translate_pyplot_color(plt.rcParams['figure.facecolor'])
    rc_fg = translate_pyplot_color(plt.rcParams['axes.labelcolor'])
    org_tabbg = s.lookup('TNotebook.Tab', 'background')
    s.configure('Plot.TNotebook.Tab', background=org_tabbg)
    s.map('Plot.TNotebook.Tab', 
            background=[('selected', rc_bg)],
            foreground=[('selected', rc_fg)],
            )

