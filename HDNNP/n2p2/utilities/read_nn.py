from ase.io.n2p2 import read_n2p2
from ase.io.trajectory import TrajectoryWriter

traj = read_n2p2('output.data', index=None)

trajw = TrajectoryWriter('NN.traj','a')

for atoms in traj:
    trajw.write(atoms)
