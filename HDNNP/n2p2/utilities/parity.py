bash-3.2$ cat parity.py
from ase.io import *
from tqdm import tqdm
import numpy as np
import matplotlib.pyplot as plt
from ase.geometry import wrap_positions
import argparse

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

def plot_parity(traj, traj_nn, train_traj=None):
    e_dft = np.array([atoms.get_potential_energy()/len(atoms) for atoms in traj])
    e_nn =  np.array([atoms.get_potential_energy()/len(atoms) for atoms in traj_nn])
    f_dft = [atoms.get_forces() for atoms in traj]
    f_nn =  [atoms.get_forces() for atoms in traj_nn]

    if train_traj:
        train_list, valid_list = check_in_train(traj, train_traj)

        e_dft_t = np.take(e_dft, train_list)
        e_dft_v = np.take(e_dft, valid_list)
        e_nn_t = np.take(e_nn, train_list)
        e_nn_v = np.take(e_nn, valid_list)
        f_dft_t = np.take(f_dft, train_list)
        f_dft_v = np.take(f_dft, valid_list)
        f_nn_t = np.take(f_nn, train_list)
        f_nn_v = np.take(f_nn, valid_list)

        f_dft = np.concatenate(f_dft).ravel()
        f_nn = np.concatenate(f_nn).ravel()
        f_dft_t = np.concatenate(f_dft_t).ravel()
        f_dft_v = np.concatenate(f_dft_v).ravel()
        f_nn_t = np.concatenate(f_nn_t).ravel()
        f_nn_v = np.concatenate(f_nn_v).ravel()

        rmse_e_t = np.sqrt(np.mean(abs(e_dft_t-e_nn_t)**2))*1000
        rmse_e_v = np.sqrt(np.mean(abs(e_dft_v-e_nn_v)**2))*1000
        rmse_f_t = np.sqrt(np.mean(abs(f_dft_t-f_nn_t)**2))
        rmse_f_v = np.sqrt(np.mean(abs(f_dft_v-f_nn_v)**2))

        xx_e = [np.min(np.concatenate((e_dft,e_nn))), np.max(np.concatenate((e_dft,e_nn)))]
        x_text = np.mean(xx_e)-0.05*(np.max(np.concatenate((e_dft,e_nn)))-np.min(np.concatenate((e_dft,e_nn))))
        y_text_t = np.mean(xx_e)-0.3*(np.max(np.concatenate((e_dft,e_nn)))-np.min(np.concatenate((e_dft,e_nn))))
        y_text_v = np.mean(xx_e)-0.35*(np.max(np.concatenate((e_dft,e_nn)))-np.min(np.concatenate((e_dft,e_nn))))

        plt.figure(figsize=(10,7.5))
        plt.subplot(1, 2, 1)
        plt.plot(e_dft_t,e_nn_t,'o', color='#1f77b4', alpha=0.5)
        plt.plot(e_dft_v,e_nn_v,'o', color='tab:orange', alpha=0.5)
        plt.legend(['Train','Validation'])
        plt.plot(xx_e,xx_e,'k--')
        plt.text(x_text,y_text_t,'RMSE(T) = %.02f meV/atom'% (rmse_e_t))
        plt.text(x_text,y_text_v,'RMSE(V) = %.02f meV/atom'% (rmse_e_v))
        plt.xlabel('$E_{DFT}$ eV/atom')
        plt.ylabel('$E_{NN}$ eV/atom')

        xx_f = [np.min(np.concatenate((f_dft,f_nn))), np.max(np.concatenate((f_dft,f_nn)))]
        x_text = np.mean(xx_f)-0.05*(np.max(np.concatenate((f_dft,f_nn)))-np.min(np.concatenate((f_dft,f_nn))))
        y_text_t = np.mean(xx_f)-0.3*(np.max(np.concatenate((f_dft,f_nn)))-np.min(np.concatenate((f_dft,f_nn))))
        y_text_v = np.mean(xx_f)-0.35*(np.max(np.concatenate((f_dft,f_nn)))-np.min(np.concatenate((f_dft,f_nn))))

        plt.subplot(1, 2, 2)
        plt.plot(f_dft_t,f_nn_t,'o', color='#1f77b4', alpha=0.5)
        plt.plot(f_dft_v,f_nn_v,'o', color='tab:orange', alpha=0.5)
        plt.legend(['Train','Validation'])
        plt.plot(xx_f,xx_f,'k--')
        plt.text(x_text,y_text_t,'RMSE(T) = %.02f eV/$\AA$'% (rmse_f_t))
        plt.text(x_text,y_text_v,'RMSE(V) = %.02f eV/$\AA$'% (rmse_f_v))
        plt.xlabel('$F_{DFT}$ eV/$\AA$')
        plt.ylabel('$F_{NN}$ eV/$\AA$')
        plt.savefig('parity.png',bbox_inches='tight', pad_inches=0.01)
        plt.show()

    else:
        ee = abs(e_dft-e_nn)*1000
        e_rmse = np.sqrt(np.mean(ee**2))
        e_all = np.concatenate((e_dft,e_nn))
        e_min = np.min(np.min(e_all))
        e_max = np.max(np.max(e_all))
        xx = [e_min,e_max]
        x_text = np.mean(xx)-0.05*(e_max-e_min)
        y_text = np.mean(xx)-0.3*(e_max-e_min)
        plt.figure(figsize=(10,7.5))
        plt.subplot(1, 2, 1)
        plt.plot(e_dft,e_nn,'o', color='#1f77b4')
        plt.plot(xx,xx,'--')
        plt.text(x_text,y_text,'RMSE(T) = %.02f meV/atom'% (e_rmse))
        plt.xlabel('$E_{DFT}$ eV/atom')
        plt.ylabel('$E_{NN}$ eV/atom')

        f_dft = np.concatenate(f_dft).ravel()
        f_nn = np.concatenate(f_nn).ravel()
        fe = abs(f_dft-f_nn)
        f_rmse = np.sqrt(np.mean(fe**2))

        f_all = np.concatenate((f_dft,f_nn))
        f_min = np.min(np.min(f_all))
        f_max = np.max(np.max(f_all))
        xx = [f_min,f_max]
        x_text = np.mean(xx)-0.05*(f_max-f_min)
        y_text = np.mean(xx)-0.3*(f_max-f_min)

        plt.subplot(1, 2, 2)
        plt.plot(f_dft,f_nn,'o', color='#1f77b4')
        plt.plot(xx,xx,'--')
        plt.text(x_text,y_text,'RMSE(T) = %.02f eV/$\AA$'% (f_rmse))
        plt.xlabel('$F_{DFT}$ eV/$\AA$')
        plt.ylabel('$F_{NN}$ eV/$\AA$')

        plt.savefig('parity.png')
        plt.show()

if __name__=="__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--d', help="Ref DFT trajectory", default=None)
    parser.add_argument('--n', help="NN trajectory", default=None)
    parser.add_argument('--t', help="Train trajectory", default=None)

    args = parser.parse_args()

    traj = read(args.d,':')
    traj_nn = read(args.n,':')

    if args.t:
        train = read(args.t,':')
        plot_parity(traj, traj_nn, train)
    else:
        plot_parity(traj, traj_nn)
