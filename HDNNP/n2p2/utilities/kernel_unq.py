from dscribe.descriptors import ACSF
from ase.io import *
from dscribe.kernels import REMatchKernel
from sklearn.preprocessing import normalize
import numpy as np
import matplotlib.pyplot as plt
from ase.io.trajectory import TrajectoryWriter
import glob

etas = [0.0356, 0.062, 0.1082, 0.1886, 0.3289, 0.5735, 1.1667, 1.5727, 2.12,   2.8577, 3.8522, 5.1929]
r_ss = [0, 6.0664, 3.3385, 1.8372, 1.0111, 0.5564, 0.3062]
g2_params = []

for eta in etas:
    for r_s in r_ss:
        g2_params.append([eta, r_s])

lambdas = [-1.,  1.]
zetas = [ 1.,  4., 16.]

g4_params=[]
for eta in etas:
    for zeta in zetas:
        for l in lambdas:
            g4_params.append([eta, zeta, l])

acsf = ACSF(
    species=["Pt", "C", "O"],
    rcut=6.5,
    g2_params=g2_params,
    g4_params=g4_params,)

name = glob.glob('*.traj')
traj = read(name[0],':')
traj2 = read(name[0],':')
trajw = TrajectoryWriter('unq.traj','a')

collect_desc=[]
for atoms in traj:
    pos = atoms.get_positions()
    pos2 = pos[:,2]
    ndx = np.where(pos2<18.5)[0]
    ndx = np.sort(ndx)[::-1]
    for j in ndx:
        del atoms[j]

    features = acsf.create(atoms)
    features = normalize(features)
    collect_desc.append(features)

re = REMatchKernel(metric="laplacian", gamma=0.5, threshold=1e-5)
re_kernel = re.create(collect_desc)


re_kernel = np.where(re_kernel > 0.85, 1, 0)
columns = np.full((re_kernel.shape[0],), True, dtype=bool)

for i in range(re_kernel.shape[0]):
    for j in range(i+1, re_kernel.shape[0]):
        if re_kernel[i,j] == 1:
            if columns[j]:
                columns[j] = False

col = np.arange(len(traj))
unq_ndx = col[columns]

for i in unq_ndx:
    atoms = traj2[i]
    trajw.write(atoms)

np.savetxt('mat.txt',re_kernel, fmt='%d')
plt.imshow(re_kernel, cmap='gray_r')
plt.show()
