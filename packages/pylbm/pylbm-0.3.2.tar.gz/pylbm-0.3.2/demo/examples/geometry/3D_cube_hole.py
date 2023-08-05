from __future__ import print_function
from __future__ import division
# Authors:
#     Loic Gouarin <loic.gouarin@math.u-psud.fr>
#     Benjamin Graille <benjamin.graille@math.u-psud.fr>
#
# License: BSD 3 clause

"""
Example of a 3D geometry: the cube [0,1] x [0,1] x [0,1] with a spherical hole
"""
import pylbm
dico = {
    'box':{'x': [0, 1], 'y': [0, 1], 'z':[0, 1], 'label':0},
    'elements':[pylbm.Sphere((.5,.5,.5), .25, label=1)],
}
geom = pylbm.Geometry(dico)
print(geom)
geom.visualize(viewlabel=True)
