# Theoretical autocorrelation functions
import numpy as np
import scipy.signal

def AC(x):
    n = len(x)
    # ac = np.correlate(x, x, "full")
    ac = scipy.signal.correlate(x, x, "full")

    w = np.arange(n, 0, -1)
    ac = ac[n-1:] / w
    return ac


def Cv(t, gamma, T,O, a):
    
    I = 1j; 
    Sqrt = np.sqrt
    
    od = [None]
    ou = [None]
    for o in [( I*gamma - Sqrt(4 * a**2 - gamma * (gamma + (4*I)*O )) )/2, 
               (I*gamma + Sqrt(4 * a**2 - gamma * (gamma + (4*I)*O ))  )/2,
               ((-I)*gamma - Sqrt(4*a**2 - gamma*(gamma - (4*I)*O)))/2,
               ((-I)*gamma + Sqrt(4*a**2 - gamma*(gamma - (4*I)*O)))/2]:
        if np.imag(o) >=0:
            ou.append(o)
        else:
            od.append(o)
        
    c = (-4j)*gamma*T*(( np.exp(1j*t*ou[1]) * ou[1]**2 ) / ( (od[1] - ou[1]) * (-od[2] + ou[1]) * (ou[1] - ou[2]) ) 
                     + ( np.exp(1j*t*ou[2]) * ou[2]**2 ) / ( (od[1] - ou[2]) * (-od[2] + ou[2]) * (-ou[1] + ou[2]) ))
    return c

def Cv_approx_1(t, g, T, O, a):
    nu = 0.5 * g * O / a
    
    return a**2*T/(a**2-O**2) * np.exp(-g*t/2) * \
    (2 * np.cos((a-1j*nu)*t)
    +(2j*O/a - (g/a)*(1-(O/a)**2)) * np.sin((a-1j*nu)*t))

def Cr(t, gamma, T,O):
    c = Cv(t, gamma, T, O)
    return c * np.exp(-1j*O*t)