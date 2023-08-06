from EPIC.utils.numbers import G, G_SI
from math import pi

def a_of_z(z, a0=1):
    return a0/(1+z)

def z_of_a(A, a0=1):
    return a0/A - 1

def rho_critical(Hz):
    return 3*Hz**2/(8*pi*G)    # Msun Mpc^-3 or h^2 Msun Mpc^-3 if H in h km/s/Mpc

def rho_critical_SI(Hz):
    return 3*Hz**2/(8*pi*G_SI)    # h^2 Msun Mpc^-3

