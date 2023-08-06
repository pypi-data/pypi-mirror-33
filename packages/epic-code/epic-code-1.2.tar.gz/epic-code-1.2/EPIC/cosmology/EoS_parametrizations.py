import numpy as np
import configparser
import os
from EPIC import root

default_values = configparser.ConfigParser()
default_values.read([
    os.path.join(root, 'cosmology', 'default_parameter_values.ini'),
    os.path.join(root, 'modifications', 'cosmology',
        'default_parameter_values.ini'),
    ])

# This module is reserved for parametrizations of dark energy

# Exponential of the integral of w(a)/a for calculation of the energy density
# of the different parametrizations
# integral = int_a0^a w(a') da'/a'

def get_value(label, model, parameter_space={}, accepts_default=False):
    try:
        return parameter_space[label]
    except KeyError:
        if accepts_default:
            model_name_or_default = model if model in default_values else 'DEFAULT'
            default = eval(default_values[model_name_or_default].get(label, 'None'))
            return default
        return None

# CPL parametrization
def de_cpl(a, parameter_space={}, accepts_default=False, a0=1, expIwoa=False, **kwargs):
    model = 'cpl'
    w0 = get_value('w0', model, parameter_space=parameter_space,
            accepts_default=accepts_default)
    wa = get_value('wa', model, parameter_space=parameter_space,
            accepts_default=accepts_default)
    if expIwoa:
        return (a/a0)**(w0+wa) * np.exp(wa*(1 - a/a0))
    return w0 + wa * (1 - a/a0)

# Barboza-Alcaniz parametrization
def de_ba(a, parameter_space={}, accepts_default=False, a0=1, expIwoa=False, **kwargs):
    model = 'ba'
    w0 = get_value('w0', model, parameter_space=parameter_space,
            accepts_default=accepts_default)
    w1 = get_value('w1', model, parameter_space=parameter_space,
            accepts_default=accepts_default)
    x = a0/a
    if expIwoa:
        return x**(-w0) * (x*x - 2*x + 2)**(w1/2)
    return w0 + w1 * (x-1)*x/(x*x - 2*x + 2)

# fast varying models
## fv1
def de_fv1(a, parameter_space={}, accepts_default=False, a0=1, expIwoa=False, **kwargs):
    assert a0 == 1
    model = 'fv1'
    wf = get_value('wf', model, parameter_space=parameter_space,
            accepts_default=accepts_default)
    wp = get_value('wp', model, parameter_space=parameter_space,
            accepts_default=accepts_default)
    logat = get_value('logat', model, parameter_space=parameter_space,
            accepts_default=accepts_default)
    logtau = get_value('logtau', model, parameter_space=parameter_space,
            accepts_default=accepts_default)
    at = 10**logat
    tau = 10**logtau
    invtau = 1/tau
    if expIwoa:
        return a**wp * ((1 + (1/at)**invtau)/(1 + (a/at)**invtau))**(tau*(wp-wf))
    return wf + (wp - wf) / (1 + (a/at)**invtau)

## fv2
def de_fv2(a, parameter_space={}, accepts_default=False, a0=1, expIwoa=False, **kwargs):
    assert a0 == 1
    model = 'fv2'
    w0 = get_value('w0', model, parameter_space=parameter_space,
            accepts_default=accepts_default)
    wp = get_value('wp', model, parameter_space=parameter_space,
            accepts_default=accepts_default)
    logat = get_value('logat', model, parameter_space=parameter_space,
            accepts_default=accepts_default)
    logtau = get_value('logtau', model, parameter_space=parameter_space,
            accepts_default=accepts_default)
    tau = 10**logtau
    invtau = 1/tau
    at = 10**logat
    if expIwoa:
        invat = 1/at
        return a**wp * np.exp( (w0-wp)/(1 - invat**invtau) \
                * (a - 1 - 1/(invtau + 1) * invat**invtau \
                * (a**(invtau+1) - 1)) )
    return wp + (w0 - wp) * a * (1 - (a/at)**invtau)/(1 - (1/at)**invtau)

## fv3
def de_fv3(a, parameter_space={}, accepts_default=False, a0=1, expIwoa=False, **kwargs):
    assert a0 == 1
    model = 'fv3'
    w0 = get_value('w0', model, parameter_space=parameter_space,
            accepts_default=accepts_default)
    wp = get_value('wp', model, parameter_space=parameter_space,
            accepts_default=accepts_default)
    logat = get_value('logat', model, parameter_space=parameter_space,
            accepts_default=accepts_default)
    logtau = get_value('logtau', model, parameter_space=parameter_space,
            accepts_default=accepts_default)
    tau = 10**logtau
    at = 10**logat
    invtau = 1/tau
    if expIwoa:
        invat = 1/at
        return a**wp * np.exp(tau * (w0-wp)*(a**invtau-1)*((a/at)**invtau \
                + invat**invtau - 2)/2/(invat**invtau-1))
    return wp + (w0 - wp) * a**invtau * (1 - (a/at)**invtau)/(1 - (1/at)**invtau)
