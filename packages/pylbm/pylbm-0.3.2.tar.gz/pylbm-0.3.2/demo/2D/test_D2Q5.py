from __future__ import print_function, division
from six.moves import range
import numpy as np
import sympy as sp
import pylbm
import sys

X, Y, LA = sp.symbols('X, Y, LA')
rho, qx, qy = sp.symbols('rho, qx, qy', real=True)

def feq(v, u):
    x, y = sp.symbols('x, y')
    vsymb = sp.Matrix([x, y])
    weight = sp.Matrix([sp.Rational(1, 3),
                        sp.Rational(1, 6),
                        sp.Rational(1, 6),
                        sp.Rational(1, 6),
                        sp.Rational(1, 6),
                        ])
    print(weight)
    f = rho*(1 + 3*u.dot(vsymb) + sp.Rational(9, 2)*u.dot(vsymb)**2 - sp.Rational(3, 2)*u.norm()**2)
    return sp.Matrix([weight[iv]*f.subs([(x, vv[0]), (y, vv[1])])-weight[iv] for iv, vv in enumerate(v)])


dx = .1
xmin, xmax = 0, 1
ymin, ymax = 0, 1

dico = {
    'box':{'x':[xmin, xmax], 'y':[ymin, ymax], 'label':[-1, -1, 0, 1]},
    'space_step':dx,
    'scheme_velocity':1,
    'schemes':[
        {
            'velocities': [0, 3, 4, 1, 2] ,
            'conserved_moments': [rho, qx, qy],
            'polynomials':[1, X, Y, 5*(X**2+Y**2) - 4, (X**2-Y**2)],
            'feq': (feq, (sp.Matrix([qx/rho, qy/rho]),)),
            'relaxation_parameters':[0, 0, 0, 1.5, 1.5],
        },
    ],
    'parameters': {LA: 1},
}

sol = pylbm.Scheme(dico)

