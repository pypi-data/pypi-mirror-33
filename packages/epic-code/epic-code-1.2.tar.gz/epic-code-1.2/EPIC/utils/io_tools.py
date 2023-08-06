import os 
import re
import datetime
import argparse
import numpy as np
from collections import OrderedDict

tag_spec = [{'regular': 'italic', 'superscript': 'superitalic', 'subscript': 'subitalic'}, 
        {'regular': 'times', 'superscript': 'super', 'subscript': 'sub'}]

available_fonts = OrderedDict((
    ('Computer Modern', [
        ('fontenc', ['T1',]),
        ('ae',)
        ]),
    ('Times', [
        ('fontenc', ['T1',]),
        ('txfontsb',)
        ]),
    ('Bitstream Charter', [
        ('fontenc', ['T1',]),
        ('mathdesign', ['bitstream-charter',]),
        ]),
    ('Palatino', [
        ('fontenc', ['T1',]),
        ('pxfonts',),
        ]),
    ))

pdf_fonts = OrderedDict((
    ('Computer Modern', [
        ('fontenc', ['T1',]),
        ('ae',)
        ]),
    ('Times', [
        ('fontenc', ['T1',]),
        ('txfontsb',)
        ]),
    ('Pazo Math', [
        ('mathpazo', ['sc',]),
        ]),
    ))

class TimeString(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        value = check_against(values, '\d+h') # searches for time in hours first
        if value:
            setattr(namespace, self.dest, int(value[:-1]) * 60 * 60) 
            # always returns time in seconds
            return

        value = check_against(values, '\d+min')
        if value:
            setattr(namespace, self.dest, int(value[:-3]) * 60)

        value = check_against(values, '\d+sec')
        if value:
            setattr(namespace, self.dest, int(value[:-3]))
            return

class Prior(object):
    def __init__(self, vmin, vmax, vdefault):
        self.vmin = vmin
        self.vmax = vmax
        self.ref = vdefault
        self.interval_size = vmax - vmin

    def __repr__(self):
        return ',\t'.join(("%.3e" % self.vmin, "%.3e" % self.vmax, "%.3e" % self.ref))

class GaussianPrior(object):
    def __init__(self, mu, sigma):
        self.mu = float(mu)
        self.sigma = float(sigma)
        self.vmin = self.mu - 6 * self.sigma
        self.vmax = self.mu + 6 * self.sigma
        self.ref = self.mu
        self.interval_size = self.vmax - self.vmin

    def __repr__(self):
        return 'N(%.3e, %.3e)' % (self.mu, self.sigma)

class Fixed(object):
    def __init__(self, value):
        self.vmin = value
        self.vmax = value
        self.ref = value

    def __repr__(self):
        return ',\t'.join(("%.3f" % self.vmin, "%.3f" % self.vmax, "%.3f" % self.ref))

def lookarg(string, list_argv):
    for arg in list_argv:
        if string in arg:
            returnFound = arg
            break
    else:
        returnFound = False
    return returnFound

def assert_extension(name, ext):
    ext = '.' + ext
    if name.endswith(ext):
        return name
    else:
        return name + ext

def lookargext(string, list_argv):
    findres = lookarg(string, list_argv)
    return assert_extension(findres, string[-3:])

def re_lookarg(pattern, list_argv):
    p = re.compile(pattern)
    for arg in list_argv:
        if p.match(arg):
            return arg
    else:
        return False

def lookarg1(string, list_argv, instance=None, optask=None):
    findres = lookarg(string, list_argv)
    if findres:
        if instance:
            return instance(findres.split('=')[1])
        return findres.split('=')[1]
    if optask:
        return instance(input(optask))
    return findres

def lookarg1list(string, list_argv, instance=None, optask=None):
    findres = lookarg1(string, list_argv, optask=optask)
    if findres:
        if instance:
            return [instance(fr) for fr in findres.split(',')]
        return [fr for fr in findres.split(',')]
    return findres

def fixed_length(label, windowsize=False, fill_char=' ', barwidth=10, barlength=20):
    if not windowsize:
        try:
            import curses
            curses.setupterm()
            windowsize = curses.tigetnum("cols")
        except:
            windowsize=80
    windowsize = min(windowsize, 80)
    freespace = -1
    origlabel = label
    i = len(label)
    while freespace < 0:
        label = label[:i]
        if i < len(origlabel):
            label = label[:-3] + '...'
        freespace = windowsize - len(label) - barwidth - 2 - 2 - 2
        show_pos  = 1 + 2*len(str(barlength))
        show_percent = 4
        freespace -= max(show_pos, show_percent)
        i -= 1
    return label + freespace//len(fill_char) * fill_char

def unzip_chain(chain):
    extracted = []
    for line in chain[:,:]:
        for _ in range(int(line[-1])):
            extracted.append(line[:-1])
    return np.array(extracted)

def truncate(list_of_chains, stop_at=None):
    sizes = [len(chain) for chain in list_of_chains]
    smaller = min(sizes)
    if stop_at:
        smaller = min(smaller, stop_at)
    if smaller % 2 == 1:
        smaller -= 1

    new_chains = [chain[:smaller,:] for chain in list_of_chains]
    sizes = [len(chain) for chain in new_chains]
    assert len(set(sizes)) == 1
    return sizes[0], new_chains

def get_inifile_name(wdir):
    inifile = os.listdir(wdir)
    inifile = [df for df in inifile if not '.swp' in df]
    inifile = [df for df in inifile if not '.un~' in df]
    return lookargext('.ini', inifile)

def readfile(filename):
    with open(filename, 'r') as f:
        return f.readlines()

def read1linestring(datalines, label):
    l = iter(datalines)
    a = next(l)
    while l and (not label in a):
        a = next(l)
    a = next(l)
    return a.strip()

def read_model_name(wdir, label='NAME'):
    inifile = get_inifile_name(wdir)
    return read1linestring(readfile(os.path.join(wdir, inifile)), label)

def readlegend(iterable, nparams, I):
    text = r'' + next(iterable).split('\t')[1].strip('\n')
    for j in range(nparams-I-1): # I the number of integrated (marginalized) paramenters, the other in the line above
        text = text + '\n' + next(iterable).strip('\n')
    return text

def looktagstrings(inifile_lines, tag):
    import collections
    l = iter(inifile_lines)
    a = next(l)
    while l and (not tag in a):
        a = next(l)
    dicttag = collections.OrderedDict()
    while l and (not 'end' in a):
        if not a[0] == '#' and len(a.split()) == 2:
            key, string = a.split()
            dicttag[key] = string
        a = next(l)
    return dicttag

def saveint(filename, value):
    with open(filename, 'w') as wf:
        wf.write("%i\n" % value)

def readint(filename):
    with open(filename, 'r') as wf:
        integer = wf.readline().strip()
    return int(integer)

def lookprior(inifile_lines, needs_mq=True):
    import collections
    l = iter(inifile_lines)
    a = next(l)
    params = collections.OrderedDict()
    mq = collections.OrderedDict()
    nuisance = []
    while l and (not 'end' in a):
        slices = a.split()
        if len(slices) > 0 and not a[0] == '#':
            key = slices.pop(0)
            Nlist = [s for s in slices if 'N=' in s]
            # this is for retrocompatibility with old files which had a N=1000 column (grid)
            if len(Nlist) > 0:
                for element in Nlist:
                    slices.remove(element) # just ignore the Nphasespace number for the MCMC
            if 'nuisance' in slices:
                nuisance.append(key)
                slices.remove('nuisance')
            #if len(slices) == 3: # asymmetrical error
            #    pvalue, dx1, dx2 = slices
            #    params[key] = Prior(float(pvalue)-float(dx2), float(pvalue)+float(dx1), float(pvalue))

            if 'gaussian' in slices:
                nonflat = True
                slices.remove('gaussian')
            else:
                nonflat = False

            if len(slices) == 1: # fixed parameter
                pvalue = slices
                params[key] = Fixed(float(pvalue[0]))
            elif len(slices) == 3: # mq value
                mq[key] = float(slices.pop(-1))

            if len(slices) == 2: # plus/minus delta
                pmin, pmax = slices
                if nonflat:
                    params[key] = GaussianPrior(pmin, pmax)
                    if not key in mq:
                        mq[key] = float(pmax)
                else:
                    pdefault = (float(pmin) + float(pmax))/2
                    params[key] = Prior(float(pmin), float(pmax), pdefault) 
                if not key in mq and needs_mq:
                    mq[key] = float(input('Enter mq value for parameter %s: ' % key))

            if len(slices) > 3:
                raise

        a = next(l)
    return params, nuisance, mq

def check_against(value, pattern):
    p = re.compile(pattern)
    return value if p.match(value) else None

def find_timestring_convert_to_seconds(arg):
    value = re_lookarg('\d+h', arg)  # time in hours preferable over min
    if value:
        value = int(value[:-1])
        return value * 60 * 60 # time from hours to seconds
    else:
        value = re_lookarg('\d+min', arg)
        if value:
            value = int(value[:-3])
            return value * 60 # time from minutes to seconds
        else:
            value = re_lookarg('\d+sec', arg)
            if value:
                return int(value[:-3])
            else:
                return False

def printtime(time):
    if time < 60:
        return '%.1f seconds' % time
    else:
        if time < 60*60:
            return '%im%is' % divmod(time,60)
        else:
            if time < 60*60*24:
                return '%ih%im' % divmod(time/60,60)
            else:
                return '%id%.1fh' % divmod((time/60)/60, 24)

def deletefiles(folder):
    dirPath = os.path.join( os.path.abspath(os.path.curdir), folder )
    fileList = os.listdir( dirPath )
    for fName in fileList:
        os.remove( os.path.join( dirPath, fName ) )

def getfilelist(folder, ext):
    fl = os.listdir(folder)
    dext = '.' + ext
    fl = [FL for FL in fl if FL.endswith(dext)]
    return fl

def pasta(local, horario, clear=False):
    criar = os.path.join(local, horario)
    if not os.path.isdir( criar ):
        os.mkdir( criar )
    if clear:
        deletefiles( criar )
    return criar

def define_time():
    return datetime.datetime.utcnow().strftime("%y%m%d-%H%M%S")

def create_listbinsdict(wdir, combobins, binsfile, clear=False):
    listbins = []
    for cb in combobins:
        binsdict = {'default':  cb}
        if binsfile:
            binsdict = load_bins(binsfile, binsdict, cb)
        listbins.append(binsdict)
        pasta(wdir, "results%i" % cb, clear=clear)
    return listbins

def load_bins(binsfile, binsdict, cbins):
    lines = readfile(binsfile)

    l = iter(lines)
    a = next(l)
    while l and (not 'BINS' in a):
        a = next(l)
    while l and (not 'end' in a):
        if (not a[0] == '#') and len(a.split()) == 2:
            key, wbins = a.split()
            binsdict[key] = int(round(float(wbins)*cbins))
        a = next(l)
    return binsdict

def power_notation(factor):
    from math import log10
    if len(str(factor)) > 3:
        return r'10^{' + str(int(log10(factor))) + r'}'
    else:
        return str(factor)

def append_distribution_parameters_to_tex(texfile, tex, bf, sigmasCL, prior='', factor=1, fmt=5):
    factorstr = power_notation(factor) + r'\,' if factor != 1 else ''
    priorstr = bool(prior) and r'$\left[' + ', '.join(["%.2f" % (factor*prior[0]), "%.2f" % (factor*prior[1])]) + r'\right]$' or prior
    #priorstr = bool(prior) and r'$\mathcal{N}\left(' + ' ,'.join(["%.2f" % (factor*prior.mu), "%.2f" % (factor*prior.sigma)]) + r'\right)$' or prior
    texfile.write(
            '\t&\t'.join([
                r'                $' + factorstr + tex.replace('mathrm','text') + '$',
                priorstr,
                (factor*bf).__format__(".%if" % fmt),
                ] + sigmasCL
                ) + '\t' + r'\\' + '\n'
            )
    return None

def close_tex(texfile):
    texfile.write(
            '\n'.join([
                r'            \end{tabular}',
                r'        \end{ruledtabular}',
                r'    \end{table}',
                r'\end{document}',
                ])
            )
    texfile.write('\n')
    texfile.close()
    return None

def table_headings(texfile, levels=[1, 2]):
    texlevels = [
            r'\multicolumn{1}{c}{$' + str(level) + r'\sigma$ C.L.}'
            for level in levels
            ]
    texfile.write(
            '    &    '.join([
                r'                Parameter',
                r'Prior',
                r'\multicolumn{1}{c}{Best-fit}',
                ] + texlevels
                )
            )
    texfile.write(r'    \\    \hline')
    texfile.write('\n')

def create_tex_table(file_path, len_levels=2, cfont=None):
    texfile = open(file_path, 'w')
    latex_lines = [
            r'\documentclass[landscape]{revtex4-1}',
            r'\usepackage{mathtools}',
            r'\usepackage{dcolumn}',
            r'\usepackage{siunitx}',
            ]
    if cfont == 'Times':
        latex_lines.append(r'\usepackage{txfontsb}')
    latex_lines += [
            r'\newcolumntype{m}{D{+}{\,\pm\,}{-1}}',
            r'\sisetup{separate-uncertainty = true}',
            r'\begin{document}',
            r'    \begin{table}[t]',
            r'        \caption{\label{your_label_here}Results}',
            r'        \begin{ruledtabular}',
            r'            \renewcommand{\arraystretch}{1.4}',
            '            \\begin{tabular}{c c D..{-1} %s}' % ' '.join('m'*len_levels),
            ]
    texfile.write('\n'.join(latex_lines))
    texfile.write('\n')
    return texfile

def format_with_uncertainties(list_pars, wdirn, ffile, fmt='.5e'):
    from uncertainties import ufloat
    with open(os.path.join(wdirn, ffile), 'w') as fitfile:
        for fit in list_pars:
            nom, dev = fit
            fitfile.write(ufloat(nom, dev).format('.5e').replace('/-','') + '\n')

def load_chains_and_model_details(wdir):
    try:
        import cPickle as pickle
    except ImportError:
        import pickle

    with open(os.path.join(wdir, 'priors.p'), 'rb') as filehandler:
        priors = pickle.load(filehandler)
    with open(os.path.join(wdir, 'nuisance.p'), 'rb') as filehandler:
        nuisance = pickle.load(filehandler)
    with open(os.path.join(wdir, 'mq.p'), 'rb') as filehandler:
        mq = pickle.load(filehandler)
    with open(os.path.join(wdir, 'tex.p'), 'rb') as filehandler:
        tex = pickle.load(filehandler)
    for par in tex.keys():
        tex[par] = tex[par].replace('text', 'mathrm')
    with open(os.path.join(wdir, 'parnames.p'), 'rb') as filehandler:
        parnames = pickle.load(filehandler)
    nparams = readint(os.path.join(wdir, 'nparams.txt'))
    nchains = readint(os.path.join(wdir, 'nchains.txt'))
    return priors, nuisance, mq, tex, parnames, nparams, nchains

def parse_unit(text, latex=True):
    new_units = []
    units = text.strip().split()
    if latex:
        for unit in units:
            if '^' in unit:
                parts = unit.split('^')
                unit = r'\rm' + '{{{0}}}^{{{1}}}'.format(*parts)
            else:
                unit = r'\rm{' + '%s}' % unit
            new_units.append(unit)
        return ' \\, '.join(new_units)
    # unicode superscripts and subscripts:
    for unit in units:
        if '^' in unit:
            parts = unit.split('^')
            scripts = parts[1]
            for char, ucode_superscript in (
                    ('+', ''),
                    ('-', '\u207B'),
                    ('0', '\u2070'),
                    ('1', '\u00B9'),
                    ('2', '\u00B2'),
                    ('3', '\u00B3'),
                    ('4', '\u2074'),
                    ('5', '\u2075'),
                    ('6', '\u2076'),
                    ('7', '\u2077'),
                    ('8', '\u2078'),
                    ('9', '\u2079'),
                    ):
                scripts = scripts.replace(char, ucode_superscript)
            unit = parts[0] + scripts
        new_units.append(unit)
    return ' '.join(new_units)

def greek_character(string):
    try:
        string.encode('ascii')
        return False
    except UnicodeEncodeError:
        return True

def add_with_tag(part, c, forced_upright=False):
    is_greek_or_numeric = c.isnumeric() or greek_character(c) or forced_upright
    return c, tag_spec[int(is_greek_or_numeric)][part]

def apply_replacements(label):
    newlabel = label
    for (o, n) in [
            (r'\Omega', 'Ω'), #\u03A9'),
            (r'\Lambda', 'Λ'), #\u1D27'),
            (r'\xi', 'ξ'),
            (r'\tau', 'τ'),
            (r'\gamma', 'γ'),
            (r'\log', '[log]'),
            (r'\rm{', '['),
            (r' \, ', ' '),
            ]:
        newlabel = newlabel.replace(o, n)
    return newlabel

def parse_tex(label):
    processed = []
    part = 'regular'
    label_replaced = apply_replacements(label)
    forced_upright = False
    for c in label_replaced:
        if c not in '^_{}[]':
            processed.append((part, c, forced_upright))
        elif c == '^':
            part = 'superscript'
        elif c == '_':
            part = 'subscript'
        elif c == '{' :
            pass
        elif c == '[':
            forced_upright = True
        elif c == ']':
            forced_upright = False
        else: # i.e., }
            part = 'regular'

    tagged = []
    for part, c, forced_upright in processed:
        tagged.append(add_with_tag(part, c, forced_upright=forced_upright))

    return tagged

    #for o, n in (
    #        ('logat', 'log\u2081\u2080 a\u209C'),
    #        ('logtau', 'log\u2081\u2080 \u03C4'),
    #        ('O', '\u03A9'),
    #        ('h2', 'h\u00B2'),
    #        ('wd', 'we'),
    #        ('0', '\u2080'),
    #        ('c', 'c\u2080'),
    #        ('b', 'b\u2080'),
    #        ('m', '\u2098\u2080'),
    #        ('d', '\u0064\u2080'),
    #        ('we', 'w\u0064'),
    #        ('_CMB', '_CMB')
    #        ):
    #    newlabel = newlabel.replace(o, n)

def split_last(string, sep=' '):
    return [s[::-1] for s in string[::-1].split(sep, maxsplit=1)][::-1]

def tex_packages(font_config):
    l = [r'\usepackage{mathtools}']#r'\usepackage{amsmath}',
    for package in font_config:
        if len(package) == 1:
            l.append('\\usepackage{%s}' % package[0])
        else:
            l.append('\\usepackage[%s]{%s}' % (','.join(package[1]),
                package[0]))
    return l
