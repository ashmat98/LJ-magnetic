# Theoretical autocorrelation functions
import numpy as np


def Cv(t, gamma, T,O):
    a=1
    I = 1j; Sqrt = np.sqrt
    
    od = [None]
    ou = [None]
    for o in [(I*gamma - Sqrt(4*a**2 - gamma*(gamma + (4*I)*O)))/2, 
               (I*gamma + Sqrt(4*a**2 - gamma*(gamma + (4*I)*O)))/2,
               ((-I)*gamma - Sqrt(4*a**2 - gamma*(gamma - (4*I)*O)))/2,
               ((-I)*gamma + Sqrt(4*a**2 - gamma*(gamma - (4*I)*O)))/2]:
        if np.imag(o) >=0:
            ou.append(o)
        else:
            od.append(o)
        
    c = (-4j)*gamma*T*((np.exp(1j*t*ou[1])*ou[1]**2)/((od[1] - ou[1])*(-od[2] + ou[1])*(ou[1] - ou[2])) + (np.exp(1j*t*ou[2])*ou[2]**2)/((od[1] - ou[2])*(-od[2] + ou[2])*(-ou[1] + ou[2])))
    return c

def Cr(t, gamma, T,O):
    c = Cv(t, gamma, T, O)
    return c * np.exp(-1j*O*t)