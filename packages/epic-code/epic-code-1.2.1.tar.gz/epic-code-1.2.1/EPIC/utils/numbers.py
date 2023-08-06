from math import pi, log

# constants of nature
speedoflight = 299792458. # in m/s
G = 4.3021135e-9 # in units of Mpc Msun**-1 (km/s)**2
mH = 1.67262178e-27 # in units of kg 
G_SI = 6.674e-11 / (3.2408e-20)**2 # in units of (km/Mpc)^2 m^3 kg^-1 s^-2
h_Pl = 6.62607e-34 # in units of J s = N m s = kg m^2 s^-1
k_B = 1.3806503e-23 # in units of kg m^2 s^-2 K^-1 = J K^-1 
a_B = 8 * pi**5 * k_B**4 / (15 * (h_Pl * speedoflight)**3) # in units of J^4 K^-4 / (J^3 s^3 m^3 s^-3) = J m^-3 K^-4
a_B_over_c2 = a_B / speedoflight**2 # in units of kg m^-3 K^-4

# common numbers
log2pi = log(2*pi)
log2pi_over_2 = log2pi/2
ln10 = log(10)

# units conversion
keV = 1.602176565e-22 # in units of kg (km/s)**2
kg = 1/keV # in units of keV (km/s)**-2
mumH = mH * kg * 0.63
GmumH = G * mumH
Mpc_to_km = 3.085677581e19

# statistics
#CL68 = 0.682689492137086       # 1 sigma
#CL95 = 0.954499736103642       # 2 sigma 
#CL997 = 0.997300203936740      # 3 sigma
#CL999 = 0.999936657516334      # 4 sigma

# this is given by either
# lambda n: 1 - 2 * scipy_stats_standard_normal.cdf(-n)
# or
# lambda n: st.distributions.chi2(1).cdf(n**2)
