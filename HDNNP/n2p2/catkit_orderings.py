#!/usr/bin/env python

"""catkit_orderings.py: Script to generate different ordering of adsorbate on surafce for given coverage range."""
__author__      = "Vaidish Sumaria"
__copyright__   = " "

from catkit.gen.surface import SlabGenerator
from ase.build import bulk
from ase.visualize import view
from ase import Atom, Atoms
from catkit.gen.adsorption import AdsorptionSites
from catkit.gen.adsorption import Builder
from catkit.build import molecule
from ase.io.trajectory import TrajectoryWriter
from itertools import combinations
import numpy as np
from ase.neighborlist import neighbor_list, natural_cutoffs, NeighborList
from pygcga2.checkatoms import CheckAtoms
import itertools

def check_nbr(atoms):
    """
    Check if C-C atoms are not too close to each other
    """
    C_ndx = [atom.index for atom in atoms if atom.symbol == 'C']
    nat_cut = natural_cutoffs(atoms, mult=1.2)
    nl = NeighborList(nat_cut, self_interaction=False, bothways=True)
    nl.update(atoms)
    flag=0
    for c_ndx in C_ndx:
        indices, offsets = nl.get_neighbors(c_ndx)
        x = np.intersect1d(indices, C_ndx)
        if len(x)!=0:
            flag=1
    return flag

def rot_trans_ads(ads, normal, coordinate, h):
    """
    Function to rotate the CO molecules along the normal and translate it to the adsorption site
    ads = adsorabate molecule
    normal = normal to the site to rotate molecule there
    coordinate = coodinates of site
    h = height of the adsorbing molecule
    """
    ads.rotate([0, 0, 1], normal, center=[0,0,0])
    coordinate = np.array(coordinate)
    normal = np.array(normal)
    c_ads = coordinate + (normal*h)
    ads.translate(c_ads)
    return ads

def add_island_ads(slab, island_ndx):
  """
  Function to add CO  on-top site of the island/step edge site -- known information about the system.
  """
    pos = slab.get_positions()
    t = slab.copy()
    for i in island_ndx:
        coordinate = pos[i,:]
        normal = [0,0,1]
        d_CO = 1.158
        h = 1.848
        ads_copy = Atoms('CO',positions=[(0, 0, 0), (0, 0, d_CO)],cell=[[0,0,0],[0,0,0],[0,0,0]])
        ads1 = rot_trans_ads(ads_copy, normal, coordinate, h)
        t.extend(ads1)
    return t

def orderings(n_sites, cnt, normals, coordinates, slab, island_ndx, trajw):
  """
  Function that generates all the possible orderings of CO on various symmetric sites  at a given coverage "cnt" - no. of CO here
  n_sites = number of sites
  cnt = no. of CO molecules
  normals = normal to the sites
  coordinates = coordinate of the sites
  slab = slab on which you want to adsorb things
  island_ndx = on-top site of the island/step edge site
  trajw = ASE TrajectoryWriter object to write the generated data
  """
    atoms_stack=[]
    d_CO = 1.158
    h = 1.848
    bond_range={}
    for v in itertools.product(['Pt', 'C', 'O'], repeat=2):
        bond_range[v]=[1,10]
    bond_range[('Pt','O')] = [2,10]
    bond_range[('C','C')] = [1.8,10]

    comb = combinations(np.arange(n_sites), cnt)

    for cm in comb:
        t = slab.copy()
        for i in cm:
            ads_copy = Atoms('CO',positions=[(0, 0, 0), (0, 0, d_CO)],cell=[[0,0,0],[0,0,0],[0,0,0]])
            ads1 = rot_trans_ads(ads_copy, normals[i], coordinates[i], h)
            t.extend(ads1)

        f = check_nbr(t)
        if f==0:
            inspector=CheckAtoms(bond_range=bond_range)
            if inspector.is_good(t, quickanswer=True):
                if island_ndx==[]:
                    trajw.write(t)
                else:
                    t2 = add_island_ads(t, island_ndx)
                    trajw.write(t2)

def gen_struc(slab, nCO, min_nCO, surf_ndx, island_ndx, trajw):
"""
Function that generates all the possible orderings of CO on various symmetric sites for coverage between [min_nCO and nCO]
"""
    bond_range={}
    for v in itertools.product(['Pt', 'C', 'O'], repeat=2):
        bond_range[v]=[1,10]
    # bond_range[('Pt','O')] = [2,10]

    sites = AdsorptionSites(slab, surface_atoms=surf_ndx)
    coordinates = sites.get_coordinates(unique=False)
    connectivities = sites.get_connectivity(unique=False)
    normals = sites.get_adsorption_vectors(unique=False)

# You can remove certain sites based on it's connectivity like this:
#     remove hollow sites -- we know should be be present
#     del_ndx = np.where(connectivities==4)[0]
#     coordinates = np.delete(coordinates,del_ndx,0)
#     normals  = np.delete(normals,del_ndx,0)
#     connectivities = np.delete(connectivities, del_ndx,0)

    n_sites = len(coordinates)
    d_CO = 1.158
    h = 1.848

    # remove sites that generate irrelevant strucutres ==> this can be some strucutres that put CO 
    # molecules too close to step/ O-Pt distance is too small
    # trajw_check = TrajectoryWriter('CHECK.traj','a')
    del_=[]
    comb = combinations(np.arange(n_sites), 1)
    for cnt, cm in enumerate(comb):
        t = slab.copy()
        for i in cm:
            ads_copy = Atoms('CO',positions=[(0, 0, 0), (0, 0, d_CO)],cell=[[0,0,0],[0,0,0],[0,0,0]])
            ads1 = rot_trans_ads(ads_copy, normals[i], coordinates[i], h)
            t.extend(ads1)
            t2 = add_island_ads(t, island_ndx)
            # trajw_check.write(t2)
            f = check_nbr(t2)
            if f==0:
                continue
            else:
                del_.append(cnt)

    coordinates = np.delete(coordinates,del_,0)
    normals  = np.delete(normals,del_,0)
    connectivities = np.delete(connectivities, del_, 0)
    n_sites = len(coordinates)

    print(n_sites)

    for cnt in range(nCO+1):

        #ignore 0 coverage region
        if cnt<min_CO:
            continue

        orderings(n_sites, cnt, normals, coordinates, slab, island_ndx, trajw)

# Make a test slab ==> this should work on any given slab though. 
atoms = bulk('Pt', 'fcc', cubic=True, a=3.985)
gen = SlabGenerator(
    atoms,
    miller_index=(4, 1, 0),
    layers=8,
    vacuum=10)

trajw = TrajectoryWriter('col.traj','a')
slab0 = gen.get_slab()
slab1 = slab0.repeat([3,1,1])
# slab1.write('clean.traj')

pos = slab1.get_positions()
posz = pos[:,2]

terrace_ndx = [i for i,p in enumerate(posz) if p>16 and p<17.5]
step_ndx = [16, 33, 50]

gen_struc(slab1, nCO = 8, min_nCO = 7, terrace_ndx, step_ndx, trajw)
