from ase.io import *
from tqdm import tqdm
import numpy as np
import matplotlib.pyplot as plt
from ase.geometry import wrap_positions
import argparse
from ase.io.trajectory import TrajectoryWriter
import copy

def prep_traj(traj):
    data=[]
    for atoms in traj:
        del atoms.constraints
        atoms.set_pbc([1,1,0])
        atoms.set_calculator()
        cell = atoms.get_cell()
        pos = atoms.get_positions()
        pos2 = wrap_positions(pos, cell)
        atoms.set_positions(pos2)
        data.append(atoms)

    return data

def mag_f(f):
    return np.sqrt(np.sum(f**2))

def check_in_train(traj, train_traj):
    data_t = traj.copy()
    train_data_t = train_traj.copy()

    print('Prepping Data')
    train_data = prep_traj(train_data_t)
    data = prep_traj(data_t)
    train, valid=[],[]

    print('Creating train/valid list')
    for i in tqdm(range(len(data))):
        atoms = data[i]
        if atoms in train_data:
            train.append(i)
        else:
            valid.append(i)

    return train, valid

def add_train(traj, traj_nn, train_traj=None, cond='force'):
    trajw = TrajectoryWriter('add_train.traj','a')
    traj2 = copy.deepcopy(traj)
    traj_nn2 = copy.deepcopy(traj_nn)
    e_dft = np.array([atoms.get_potential_energy()/len(atoms) for atoms in traj])
    e_nn =  np.array([atoms.get_potential_energy()/len(atoms) for atoms in traj_nn])
    f_dft = [atoms.get_forces() for atoms in traj]
    f_nn =  [atoms.get_forces() for atoms in traj_nn]

    if train_traj:
        train_list, valid_list = check_in_train(traj, train_traj)

        print(len(train_list), len(valid_list))

        if cond=='energy':
            print('Using energy criteria for selection \n')
            e_dft_v = np.take(e_dft, valid_list)
            e_nn_v = np.take(e_nn, valid_list)
            err = abs(e_dft_v-e_nn_v)*1000
            ndx_add_train = np.where(err>10)[0]
            for ndx in ndx_add_train:
                atoms = traj2[valid_list[ndx]]
                trajw.write(atoms)

        if cond=='force':
            f_dft_v = np.take(f_dft, valid_list)
            f_nn_v = np.take(f_nn, valid_list)

            ndx_add_train=[]

            for i in range(len(f_dft_v)):
                f_d = np.array(f_dft_v[i])
                f_n = np.array(f_nn_v[i])
                f_d_mag = np.apply_along_axis(mag_f, 1, f_d)
                f_n_mag = np.apply_along_axis(mag_f, 1, f_n)
                e = abs(f_d - f_n)
                fmax = np.max(f_d_mag)
                emax = np.max(e)
                if emax>5 and fmax<30:
                    ndx_add_train.append(i)

            for ndx in ndx_add_train:
                atoms = traj2[valid_list[ndx]]
                trajw.write(atoms)

    else:
        if cond=='force':
            ndx_add_train=[]
            for i in range(len(e_dft)):
                f_d = np.array(f_dft[i])
                f_n = np.array(f_nn[i])
                f_d_mag = np.apply_along_axis(mag_f, 1, f_d)
                f_n_mag = np.apply_along_axis(mag_f, 1, f_n)
                e = abs(f_d - f_n)
                fmax = np.max(f_d_mag)
                emax = np.max(e)
                if emax>5 and fmax<30:
                    ndx_add_train.append(i)

            print(len(ndx_add_train))
            for ndx in ndx_add_train:
                atoms = traj2[ndx]
                trajw.write(atoms)

        if cond=='energy':
            ndx_add_train=[]
            err = abs(e_dft-e_nn)*1000
            ndx_add_train = np.where(err>10)[0]
            for ndx in ndx_add_train:
                atoms = traj2[ndx]
                trajw.write(atoms)

if __name__=="__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--d', help="Ref DFT trajectory", default=None)
    parser.add_argument('--n', help="NN trajectory", default=None)
    parser.add_argument('--t', help="Train trajectory", default=None)
    parser.add_argument('--c', help="Choice between forces & energy to choose index", default='force')

    args = parser.parse_args()

    traj = read(args.d,':')
    traj_nn = read(args.n,':')

    print(args.c)

    if args.t:
        train = read(args.t,':')
        add_train(traj, traj_nn, train, cond=args.c)

    else:
        add_train(traj, traj_nn, cond=args.c)
