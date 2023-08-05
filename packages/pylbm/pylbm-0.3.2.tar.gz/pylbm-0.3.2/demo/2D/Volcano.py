import numpy as np
import sympy as sp
import sys
import mpi4py.MPI as mpi
import pylbm

withPlot = False
verbose = True
filename = 'volcano'
filepath = './volcano'

#########################################################
# Physical parameters
#########################################################

d_p = {
    'geometry': {
        'xmin': 0,
        'xmax': 2,
        'ymin': 0,
        'ymax': 1,
        'volcano_center_x':   1./2,
        'volcano_width_up':   1./16,
        'volcano_width_down': 1./8,
        'volcano_height':     1./8,
    },
    'temperature': {
        'cold': -.5,
        'hot':   .5,
    },
    'Rayleigh_number': 1000000,
    'Prandtl_number': .71,
    'thermal_expansion_coeff': .01,
    'gravity_constant': 9.81,
    'wind_velocity': 0.01,
    'volcano_velocity': 0.1,
}

#########################################################
# Scheme parameters
#########################################################

d_s = {
    'spatial_step': 1./256,
    'scheme_velocity': 1,
    'mean_density': 1,
    'final_time': 10,
    'time_step_of_plot': 1./4,
}

#########################################################
# Build the parameters from dictionaries
#########################################################

Tu, Td =  d_p['temperature']['hot'], d_p['temperature']['cold']
xmin, xmax = d_p['geometry']['xmin'], d_p['geometry']['xmax']
ymin, ymax = d_p['geometry']['ymin'], d_p['geometry']['ymax']
u_wind = d_p['wind_velocity']
u_volcano = d_p['volcano_velocity']

Ra = d_p['Rayleigh_number']
Pr = d_p['Prandtl_number']
alpha = d_p['thermal_expansion_coeff']
g = d_p['gravity_constant']

dx = d_s['spatial_step']
la = d_s['scheme_velocity']
rhoo = d_s['mean_density']

dummy =  1./(la*rhoo*dx)

nu = np.sqrt(Pr*alpha*9.81*abs(Td-Tu)*(ymax-ymin)/Ra)
kappa = nu/Pr
print(nu, kappa)
eta = nu
snu = 1./(.5+3*dummy*nu)
seta = 1./(.5+3*dummy*eta)
sq = 8*(2-snu)/(8-snu)
se = seta
sf = [0., 0., 0., seta, se, sq, sq, snu, snu]
a = .5
skappa = 1./(.5+10*dummy*kappa/(4+a))
se = 1./(.5+np.sqrt(3)/3)
snu = se
sT = [0., skappa, skappa, se, snu]

if verbose:
    print("="*80)
    print("Relaxation parameters for the hydrodynamic")
    print(sf[3:])
    print("Relaxation parameters for the temperature")
    print(sT[1:])
    print("Scheme velocity")
    print(la)
    print("="*80)


#########################################################
# Boundary conditions
#########################################################

idx_down, idx_left, idx_right, idx_up = list(range(4))
idx_volcano = 4

def bc_volcano(f, m, x, y):
    m[qx] = 0.
    m[qy] = u_volcano
    m[T] = Tu

def bc_down(f, m, x, y):
    m[qx] = 0.
    m[qy] = 0.
    m[T] = Td

def bc_left(f, m, x, y):
    m[qx] = u_wind
    m[qy] = 0.
    m[T] = Td

def bc_right(f, m, x, y):
    m[qx] = u_wind
    m[qy] = 0.
    m[T] = Td

def bc_up(f, m, x, y):
    m[qx] = u_wind
    m[qy] = 0.
    m[T] = Td

#########################################################
# Plot functions
#########################################################

def plot_T(sol, bornes = False):
    #### temperature
    temp = sol.m[T]
    if bornes:
        ymin, ymax = min(Tu, Td), max(Tu, Td)
        dy = .1*(ymax-ymin)
        return temp.T, ymin-dy, ymax+dy, 0
    else:
        return temp.T

def plot_ux(sol, bornes = False):
    #### velocity in the x direction
    ux = sol.m[qx]
    if bornes:
        vm = 10*max(u_wind, u_volcano)
        return ux.T, -vm, vm, 0
    else:
        return ux.T

def plot_uy(sol, bornes = False):
    #### velocity in the y direction
    uy = sol.m[qy]
    if bornes:
        vm = 10*max(u_wind, u_volcano)
        return uy.T, -vm, vm, 0
    else:
        return uy.T

def plot_vorticity(sol, bornes = False):
    #### vorticity
    ux = sol.m[qx]
    uy = sol.m[qy]
    vort = np.abs(ux[1:-1, 2:] - ux[1:-1, :-2]
                  - uy[2:, 1:-1] + uy[:-2, 1:-1])
    if bornes:
        return vort.T, 0.0, 0.1, 1
    else:
        return vort.T

#########################################################
# Build the simulation
#########################################################

X, Y, LA = sp.symbols('X, Y, LA')
rho, qx, qy, T = sp.symbols('rho, qx, qy, T')

geo = d_p['geometry']
xL = geo['volcano_center_x'] - .5*geo['volcano_width_down']
xa = geo['volcano_center_x'] - .5*geo['volcano_width_up']
xb = geo['volcano_center_x'] + .5*geo['volcano_width_up']
xR = geo['volcano_center_x'] + .5*geo['volcano_width_down']
ya = geo['ymin']
yb = geo['ymin'] + geo['volcano_height']

volcano = [
    pylbm.Parallelogram([xa, ya], [xb-xa, 0], [0, yb-ya], 
        label=[idx_down, idx_down, idx_volcano, idx_down]),
    pylbm.Triangle([xa, ya], [xL-xa, 0], [0, yb-ya], label=idx_down),
    pylbm.Triangle([xb, ya], [xR-xb, 0], [0, yb-ya], label=idx_down),
]

dico = {
    'box': {
        'x': [xmin, xmax], 
        'y': [ymin, ymax], 
        'label': [idx_left, idx_right, idx_down, idx_up],
    },
    'elements': volcano,
    'space_step': dx,
    'scheme_velocity': la,
    'schemes':[
        {
            'velocities': list(range(9)),
            'conserved_moments': [rho, qx, qy],
            'polynomials': [
                1, X, Y,
                3*(X**2+Y**2)-4,
                0.5*(9*(X**2+Y**2)**2-21*(X**2+Y**2)+8),
                3*X*(X**2+Y**2)-5*X, 3*Y*(X**2+Y**2)-5*Y,
                X**2-Y**2, X*Y
            ],
            'relaxation_parameters': sf,
            'equilibrium': [
                rho, qx, qy,
                -2*rho + 3*(qx**2+qy**2),
                rho - 3*(qx**2+qy**2),
                -qx, -qy,
                qx**2 - qy**2, qx*qy
            ],
            'source_terms': {qy: alpha*g * T},
            'init': {rho: rhoo, qx: 0., qy: 0.},
        },
        {
            'velocities': list(range(5)),
            'conserved_moments': T,
            'polynomials': [1, X, Y, 5*(X**2+Y**2) - 4, (X**2-Y**2)],
            'equilibrium': [T, T*qx, T*qy, a*T, 0.],
            'relaxation_parameters': sT,
            'init': {T: Td},
        },
    ],
    'boundary_conditions': {
        idx_down: {
            'method': {
                0: pylbm.bc.Bouzidi_bounce_back, 
                1: pylbm.bc.Bouzidi_anti_bounce_back,
            }, 
            'value': bc_down,
        },
        idx_left: {
            'method': {
                0: pylbm.bc.Bouzidi_bounce_back, 
                1: pylbm.bc.Bouzidi_anti_bounce_back,
            }, 
            'value': bc_left,
        },
        idx_right: {
            'method': {
                0: pylbm.bc.Bouzidi_bounce_back, 
                1: pylbm.bc.Bouzidi_anti_bounce_back,
            }, 
            'value': bc_right,
        },
        idx_up: {
            'method': {
                0: pylbm.bc.Bouzidi_bounce_back, 
                1: pylbm.bc.Bouzidi_anti_bounce_back,
            }, 
            'value': bc_up,
        },
        idx_volcano: {
            'method': {
                0: pylbm.bc.Bouzidi_bounce_back, 
                1: pylbm.bc.Bouzidi_anti_bounce_back,
            }, 
            'value': bc_volcano,
        },
    },
    'generator': 'cython',
}

def update(iframe):
    while sol.t < iframe * d_s['time_step_of_plot']:
        sol.one_time_step()
    image.set_data(plot_field(sol))
    ax.title = "Solution t={0:f}".format(sol.t)

def save(sol, im):
    x, y = sol.domain.x, sol.domain.y
    h5 = pylbm.H5File(sol.mpi_topo, filename, filepath, im)
    h5.set_grid(x, y)
    rank = mpi.COMM_WORLD.rank*np.ones_like(sol.m[T])
    h5.add_scalar('T', sol.m[T])
    h5.add_scalar('rank', rank)
    h5.add_vector('velocity', [sol.m[qx], sol.m[qy]])
    h5.save()

def printProgress (iteration, total, prefix = '', suffix = '', decimals = 1,  barLength = 100):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        barLength   - Optional  : character length of bar (Int)
    """
    formatStr       = '{0:.' + str(decimals) + 'f}'
    percents        = formatStr.format(100 * (iteration / float(total)))
    filledLength    = int(round(barLength * iteration / float(total)))
    bar             = '-' * filledLength + ' ' * (barLength - filledLength)
    print('\r{0:s} |{1:s}| {2:s}% {3:s}'.format(prefix, bar, percents,  suffix), end='', file=sys.stdout, flush=True)
    if iteration == total:
        print('', end = '\n', file=sys.stdout, flush=True)

#### Visualize the geometry
# g = pylbm.Geometry(dico)
# g.visualize(viewlabel=True, viewgrid=False, fluid_color='navy', alpha = 0.5)

#### init simulation
sol = pylbm.Simulation(dico)

if withPlot:
    #### choice of the plotted field
    plot_field = plot_T

    #### init viewer
    viewer = pylbm.viewer.matplotlibViewer
    fig = viewer.Fig()
    ax = fig[0]
    ax.xaxis_set_visible(False)
    ax.yaxis_set_visible(False)
    field, ymin, ymax, decalh = plot_field(sol, bornes = True)
    image = ax.image(field, clim=[ymin, ymax], cmap="jet")
    decalh += .5
    ax.polygon(np.array([[xL,ya],[xR,ya],[xb,yb],[xa,yb],[xL,ya]])/dx-decalh, color='gray')

    #### run the simulation
    fig.animate(update, interval=1)
    fig.show()

else:
    Tf = d_s['final_time']
    dt = d_s['time_step_of_plot']

    im = 0
    save(sol, im)
    while sol.t < Tf:
        im += 1
        while sol.t < im * dt:
            sol.one_time_step()
        #printProgress(im, int(Tf/dt), prefix = 'Progress:', suffix = 'Complete', barLength =  50)
        save(sol, im)
