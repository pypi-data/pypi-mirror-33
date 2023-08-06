import numpy as np

def generic_runge_kutta(dt, t, f, derivatives, parameter_space={},
        intermediate=None, a0=1, accepts_default=False):
    '''
    This is a generic Runge-Kutta routine that supports evaluation of
    intermediate functions in order to avoid repetition (for example for
    Hubble, which explains the H) inside each fdot.
    Takes intermediate as a list of functions
    '''
    g = None 
    if intermediate:
        g = [H(t, parameter_space=parameter_space, given_densities=f,
            accepts_default=accepts_default) for H in intermediate]
    k1 = np.array([fdot(F, t, parameter_space=parameter_space, intermediate=g,
        a0=a0, accepts_default=accepts_default
        ) for F, fdot in zip(f, derivatives)])
    f_k1 = f + dt/2 * k1

    if intermediate:
        g = [H(t + dt/2, parameter_space=parameter_space, given_densities=f_k1,
            accepts_default=accepts_default) for H in intermediate]
    k2 = np.array([fdot(F, t, parameter_space=parameter_space, intermediate=g,
        a0=a0, accepts_default=accepts_default
        ) for F, fdot in zip(f_k1, derivatives)])
    f_k2 = f_k1 + dt/2 * k2

    if intermediate:
        g = [H(t + dt/2, parameter_space=parameter_space, given_densities=f_k2,
            accepts_default=accepts_default) for H in intermediate]
    k3 = np.array([fdot(F, t, parameter_space=parameter_space, intermediate=g,
        a0=a0, accepts_default=accepts_default
        ) for F, fdot in zip(f_k2, derivatives)])
    f_k3 = f_k2 + dt * k3

    if intermediate:
        g = [H(t + dt, parameter_space=parameter_space, given_densities=f_k3,
            accepts_default=accepts_default) for H in intermediate]
    k4 = np.array([fdot(F, t, parameter_space=parameter_space, intermediate=g,
        a0=a0, accepts_default=accepts_default
        ) for F, fdot in zip(f_k3, derivatives)])

    f += dt/6 * (k1 + 2*k2 + 2*k3 + k4)
    return f


