from __future__ import print_function
from __future__ import division
"""
test: True
"""
import pylbm
from six.moves import range
import sympy as sp
import math
import mpi4py.MPI as mpi

X, Y, Z, LA = sp.symbols('X, Y, Z, LA')
rho, qx, qy, qz = sp.symbols('rho, qx, qy, qz', real=True)

def feq(v, u):
    cs2 = sp.Rational(1, 3)
    x, y, z = sp.symbols('x, y, z')
    vsymb = sp.Matrix([x, y, z])
    w = sp.Matrix([sp.Rational(1,3)] + [sp.Rational(1, 18)]*6 + [sp.Rational(1, 36)]*12)
    f = rho + u.dot(vsymb)/cs2 + u.dot(vsymb)**2/(2*cs2**2) - u.norm()**2/(2*cs2)
    return sp.Matrix([w[iv]*f.subs([(x, vv[0]), (y, vv[1]), (z, vv[2])]) for iv, vv in enumerate(v)])

def bc_rect(f, m, x, y, z, rhoo, uo):
    m[rho] = 0.
    m[qx] = rhoo*uo
    m[qy] = 0.
    m[qz] = 0.

def save(sol, im):
    x, y, z = sol.domain.x, sol.domain.y, sol.domain.z
    h5 = pylbm.H5File(sol.mpi_topo, 'karman', './karman', im)
    h5.set_grid(x, y, z)
    h5.add_scalar('rho', sol.m[rho])
    qx_n, qy_n, qz_n = sol.m[qx], sol.m[qy], sol.m[qz]
    h5.add_vector('velocity', [qx_n, qy_n, qz_n])
    h5.save()

def run(dx, Tf, generator="cython", sorder=None, withPlot=True):
    """
    Parameters
    ----------

    dx: double
        spatial step

    Tf: double
        final time

    generator: pylbm generator

    sorder: list
        storage order

    withPlot: boolean
        if True plot the solution otherwise just compute the solution

    """
    la = 1
    rhoo = 1.
    uo = 0.1
    radius = 0.125

    Re = 500
    nu = rhoo*uo*2*radius/Re

    tau = .5*(6*nu/la/dx + 1)

    r = X**2+Y**2+Z**2

    dico = {
        'box':{'x':[0., 2.], 'y':[0., 1.], 'z':[0.5-3*dx, .5+3*dx], 'label':[0, 1, 0, 0, -1, -1]},
        'elements':[pylbm.Cylinder_Circle((.3,.5,0), (radius, 0, 0), (0., radius, 0), (0., 0., 1), 2)],
        'space_step':dx,
        'scheme_velocity':la,
        'schemes':[{
            'velocities': list(range(19)),
            'conserved_moments':[rho, qx, qy, qz],
            'polynomials':[
                1,
                X, Y, Z,
                19*r - 30,
                2*X**2 - Y**2 - Z**2,
                Y**2-Z**2,
                X*Y, 
                Y*Z, 
                Z*X,
                X*(5*r - 9),
                Y*(5*r - 9),
                Z*(5*r - 9),
                X*(Y**2 - Z**2),
                Y*(Z**2 - X**2),
                Z*(X**2 - Y**2),
                (2*X**2 - Y**2 - Z**2)*(3*r - 5),
                (Y**2 - Z**2)*(3*r - 5),
                -sp.Rational(53,2)*r + sp.Rational(21,2)*r**2 + 12
            ],
            'relaxation_parameters':[0]*4 + [1./tau]*15,
            'feq':(feq, (sp.Matrix([qx, qy, qz]),)),
            'init':{
                rho:rhoo,
                qx: rhoo*uo,
                qy: 0.,
                qz: 0.
            },
        }],
        'boundary_conditions':{
            0:{'method':{0: pylbm.bc.Bouzidi_bounce_back}, 'value':(bc_rect, (rhoo, uo))},
            1:{'method':{0: pylbm.bc.Neumann_x}},
            2:{'method':{0: pylbm.bc.Bouzidi_bounce_back}},
        },
        'parameters': {LA: la},
        'generator': generator,
    }

    sol = pylbm.Simulation(dico, sorder=sorder)

    im = 0
    compt = 0
    while sol.t < Tf:
        sol.one_time_step()
        compt += 1
        if compt == 128 and withPlot:
            im += 1
            save(sol, im)
            compt = 0

    return sol

if __name__ == '__main__':
    dx = 1./128
    Tf = 200.
    run(dx, Tf)
