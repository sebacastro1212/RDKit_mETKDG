from rdkit import Chem
import sys
from rdkit import DistanceGeometry
from itertools import product
from rdkit.Chem import AllChem
import pandas as pd
import os
import multiprocessing
import numpy as np
import cpeptools
import copy
import glob

def gen_confs(mol, num_conf, path):
    mol_copy = copy.deepcopy(mol)
    if not os.path.exists(path):
        os.makedirs(path)
    params = AllChem.ETKDG()

    print("Generating {} Conformers for {}".format(num_conf, path))
    params = AllChem.ETKDG()
    params.useRandomCoords = True

    AllChem.EmbedMultipleConfs(mol, num_conf, params)
    Chem.MolToPDBFile(Chem.RemoveHs(mol, updateExplicitCount = True), path + "conf.pdb")
    mol.RemoveAllConformers()



num_conformers = 1
try:
    num_conformers = int(sys.argv[1])
except:
    pass
path_list = []
num_conf_list = []
mol_list = []

tmp = sys.argv[0][:-3]
tmp = tmp.split(".")[-1]
folder = "./" +  tmp  #remove the number at the beginning for folder names, this way scripts all starts with number, while folders do not


df = pd.read_csv("../reference/smiles.tsv", sep = "\t", comment = "%")


mol_dict = {name : Chem.MolFromSmiles(val) for name, val in zip(df.Name, df.Smiles)}
for name in mol_dict:
    print(name)
    rsize = len(cpeptools.get_largest_ring(mol_dict[name]))
    ref = mol_dict[name] #ref is mol from smiles
    mol = ref
    try:
        mol  = Chem.AddHs(mol)
    except ValueError:
        print("cannot add H to {}".format(name))
        continue

    mol.UpdatePropertyCache()
    Chem.GetSymmSSSR(mol)
    mol_list.append(mol)
    path = folder + "/" +  str(name) + "/"
    path_list.append(path)

    # this code generates different number of conformers given then ring size
    """
    if rsize < 15:
        num_conf_list.append(540)
    elif rsize >= 15 and rsize < 30:
        num_conf_list.append(1800)
    elif rsize >= 30 :
        num_conf_list.append(5400)
    """
    num_conf_list.append(num_conformers)



for i in zip(mol_list, num_conf_list, path_list):
    gen_confs(i[0], i[1],i[2])
# if you want to do parallelise things, try to modify code below
"""
cores = int(sys.argv[2])
print("Number of cores : {}".format(cores))
if cores == 1:
    for i in zip(mol_list, num_conf_list, path_list):
        gen_confs(i[0], i[1],i[2])
else:
    with multiprocessing.Pool(processes=cores) as pool:
        pool.starmap(gen_confs, zip(mol_list, num_conf_list, path_list))
"""
