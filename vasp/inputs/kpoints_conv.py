from ase.io import *
from ase.calculators.vasp.vasp2 import Vasp2
import numpy as np
import  math
import matplotlib.pyplot as plt

def calculator(kpts):
    calc = Vasp2(xc='pbe',
            encut=400,
            ediff = 1.00e-06,
            prec='A',
            algo='fast',
            ispin=1,
            ismear=2,
            ibrion=2,
            nsw=1,
            sigma=0.1,
            lreal='F',
            nelmin=6,
            nelm=150,
            lwave=False,
            lcharg=False,
            kpts = kpts,
            npar=4)
    return calc

def reciprocal_ratio(atoms):
    cell = atoms.get_cell()
    rec = cell.reciprocal()
    rec = np.linalg.norm(rec, axis=1)
    rec_ratio = rec/min(rec)
    rec_ratio = np.array([round(i) for i in rec_ratio])
    return rec_ratio

atoms = read('POSCAR')
rec_ratio = reciprocal_ratio(atoms)

#kpoints will be a integer multiplier of rec_ration
calc = calculator(kpts=rec_ratio)
atoms.set_calculator(calc)
e0 = atoms.get_potential_energy()

de = 1000
cnt = 2
crit=0.05

de_col = []
cnt_col = []
while de>crit:
    kpts = rec_ratio*cnt
    calc = calculator(kpts=kpts)
    atoms.set_calculator(calc)
    e1 = atoms.get_potential_energy()
    cnt_col.append(cnt)
    de = abs(e1-e0)
    de_col.append(de)
    e0 = e1
    cnt+=1

np.save('cnt_col.npy',cnt_col)
np.save('de_col.npy', de_col)
plt.plot(cnt_col, de_col, 'o')

print('Converged k-points = '+str(kpts))

plt.ylim([0,1])
plt.savefig('kpts_conv.png')
plt.show()
