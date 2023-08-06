import numpy as np


def gaussian_band(wn, A, s, m):
    return A/s*np.sqrt(2*np.pi)*np.exp(-(wn-m)**2/2/s**2)
    
def lorentzian_band(wn, A, w, m):
    return A /(1 + (wn - m)**2/w**2)/(w*np.pi)


def band(wn, band_params):
    if band_params[0] == "gauss":
        return gaussian_band(wn, *band_params[1:])
    elif band_params[0] == "lorentz":
        return lorentzian_band(wn, *band_params[1:])
    else:
        raise ArgumentError('Unknown band {}'.format(band_params[0]))

def spectrum(wn, band_params, noise_level=0):
    spec = np.zeros_like(wn)
    for band_param in band_params:
        spec = spec + band(wn, band_param)
    if noise_level > 0:
        spec = spec + noise_level * np.random.randn(*spec.shape)
    return spec
    
    
    
def gaussian_2D(x, y, A, m_x, m_y, sigma_a, sigma_b, theta):
    theta_rad = theta/180*np.pi

    a = np.cos(theta_rad)**2/(2*sigma_a**2) + np.sin(theta_rad)**2/(2*sigma_b**2)
    b = - np.sin(2*theta_rad)/(4*sigma_a**2) + np.sin(2*theta_rad)/(4*sigma_b**2)
    c = np.sin(theta_rad)**2/(2*sigma_a**2) + np.cos(theta_rad)**2/(2*sigma_b**2)
    x_c = x - m_x
    y_c = y - m_y
    return A*np.exp(-(a*x_c**2+2*b*x_c*y_c+c*y_c**2))
