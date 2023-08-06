# Typing modules
import typing as typ

#External Modules
import json,math,itertools
import numpy as np                                                      # type: ignore
from copy import deepcopy

#--ase Imports
import ase                                                              # type: ignore
from ase.io import read,write                                           # type: ignore
from ase.constraints import FixAtoms                                    # type: ignore
from ase.visualize import view                                          # type: ignore
from ase.gui.images import Images                                       # type: ignore
from ase.gui.gui import GUI                                             # type: ignore

#--pymatgen Imports
import pymatgen as pmg 		                                            # type: ignore
from pymatgen.io.ase 		import AseAtomsAdaptor                      # type: ignore
from pymatgen.core.surface 	import SlabGenerator,Slab                   # type: ignore
from pymatgen.analysis.adsorption import AdsorbateSiteFinder,reorient_z # type: ignore

# Internal Modules
import catalog.data.data_solids_wPBE as soldata
import catalog.data.data_sol53_54_57_58_bm32_se30 as surfdata
from .utilities import flatten
from .print_parse import roundfloat


"""
Functions for interacting with ASE


Keld Data related
    get_keld_data
    get_expt_surf_energy

Element Lists
    nonmetal_symbs
    nonmetals
    mag_elems
    mag_nums
    paw_elems
    symbols2electrons

Atoms object manipulation
    traj_to_json
    json_to_traj
    classify_system
    make_atoms
    cell_to_param
    restore_magmom

Geometry
    angle
    dihedralz

Site Related
    get_sites


"""
################################################################################

# Keld Data Related
#-----------------
def get_keld_data(name  : str
                 ,k 	: str
                 ) -> typ.Any:
    """
    Docstring
    """

    name = name.split('_')[0] #sometimes suffix ('bulkmod') is appended to name
    try: return soldata.data[soldata.getKey[name] ][k]
    except KeyError:
        try: return soldata.data[soldata.getKey[name] ][k+' kittel'] #for 'bulkmodulus' / 'bulkmodulus kittel'
        except KeyError: return None

###########################
# Atoms object manipulation
###########################

def traj_to_json(atoms : ase.Atoms) -> str:
    """
    Serialize an Atoms object in a human readable way
    """

    atomdata = []
    const    = atoms.constraints
    if const: const_list = const[0].get_indices().tolist()
    else:     const_list = []

    atoms.wrap()
    for a in atoms: atomdata.append({'number'		: int(a.number)
                                    ,'x'			: roundfloat(a.x)
                                    ,'y'			: roundfloat(a.y)
                                    ,'z'			: roundfloat(a.z)
                                    ,'magmom'		: roundfloat(a.magmom)
                                    ,'tag'			: int(a.tag)
                                    ,'constrained'	: int(a.index in const_list)
                                    ,'index'		: int(a.index)})

    out = {'cell': [[roundfloat(x) for x in xx] for xx in atoms.get_cell().tolist()]
          ,'atomdata':atomdata}

    return json.dumps(out)




def json_to_traj(raw_json:str)->ase.Atoms:
    """
    Inverse of traj_to_json
    """

    raw_atoms = json.loads(raw_json)
    try:
        atom_data = raw_atoms['atom_data']
    except KeyError:
        atom_data = raw_atoms['atomdata']

    pos = np.array([[a[q] for a in atom_data] for q in ['x','y','z']]).T

    fix = FixAtoms([a['index'] for a in atom_data if a['constrained']])

    atoms = ase.Atoms(numbers     = [a['number'] for a in atom_data]
                     ,cell        = raw_atoms['cell']
                     ,positions   = pos
                     ,magmoms     = [a['magmom'] for a in atom_data]
                     ,tags        = [a['tag'] for a in atom_data]
                     ,constraint  = fix)
    return atoms


def cell_to_param(cell : np.array) -> typ.Tuple[float,float,float,float,float,float]:
    """
    ANGLES ARE IN RADIANS
    """
    a = np.linalg.norm(cell[0])
    b = np.linalg.norm(cell[1])
    c = np.linalg.norm(cell[2])
    alpha = angle(cell[1],cell[2])
    beta  = angle(cell[0],cell[2])
    gamma = angle(cell[0],cell[1])
    return (a,b,c,alpha,beta,gamma)

def classify_system(atoms : ase.Atoms) -> str:
    cutoff    = 6  # A
    atoms.center() # In case dealing with Nerds Rope & Co.
    minx,miny,minz,maxx,maxy,maxz = 1000,1000,1000,-1000,-1000,-1000
    for a in atoms:
        if a.position[0] < minx: minx =  a.position[0]
        if a.position[1] < miny: miny =  a.position[1]
        if a.position[2] < minz: minz =  a.position[2]
        if a.position[0] > maxx: maxx =  a.position[0]
        if a.position[1] > maxy: maxy =  a.position[1]
        if a.position[2] > maxz: maxz =  a.position[2]

    cell_abc  = list(map(np.linalg.norm,atoms.get_cell()[:3]))
    thickness = [maxx-minx,maxy-miny,maxz-minz]
    pbc       = [cell_abc[i]-thickness[i] < cutoff for i in [0,1,2]]

    if   all(pbc): return 'bulk'
    elif any(pbc): return 'surface'
    else:          return 'molecule'

def make_atoms(*args : str) -> ase.Atoms:
    n,p_t,c,m,cs = list(map(json.loads,args))
    return ase.Atoms(numbers=n,positions=list(zip(*p_t))
            ,cell=c,magmoms=m
            ,constraint=FixAtoms(np.nonzero(cs)[0]))

def remove_atom(atoms_obj       : ase.Atoms
               ,index_to_delete : int
               )->ase.Atoms:
    atoms_obj_watom_removed = atoms_obj.copy()
    fixed_inds              = get_list_of_fixed_indices(atoms_obj)
    fixed_inds              = [x if x<=index_to_delete else x-1 for x in fixed_inds]
    del atoms_obj_watom_removed[:]
    for ind,atom_obj in enumerate(atoms_obj):
        if not ind == index_to_delete:
            atoms_obj_watom_removed.append(atom_obj)
    atoms_obj_watom_removed.set_constraint(FixAtoms(indices=fixed_inds))
    return atoms_obj_watom_removed

def remove_atoms(atoms_obj         : ase.Atoms
                ,indices_to_delete : typ.List[int]
                )-> ase.Atoms      :
    atoms_obj_watoms_removed     = atoms_obj.copy()
    for ind in sorted(indices_to_delete,reverse = True):
        atoms_obj_watoms_removed = remove_atom(atoms_obj_watoms_removed,ind)
    return atoms_obj_watoms_removed

def get_list_of_fixed_indices(atoms_obj : ase.Atoms)->list:
    constraints          = atoms_obj.constraints
    fixed_inds           = [] # type: list
    for constraint in constraints:
        if isinstance(constraint,FixAtoms):
            fixed_inds += list(constraint.get_indices())
    return fixed_inds

def fix_negative_unit_cells(atoms_obj : ase.Atoms)-> ase.Atoms:
    cell = atoms_obj.cell
    signs = np.sign(np.sum(cell,axis = 1))
    for i, sign in enumerate(signs):
        cell[i] *= sign
    new_atoms_obj = atoms_obj.copy()
    new_atoms_obj.set_cell(cell)
    new_atoms_obj.wrap(pbc = [True,True,True])
    return new_atoms_obj

##########
# Geometry
##########
def angle(v1 : np.array
         ,v2 : np.array
         ) -> float:
    return np.arccos(np.dot(v1,np.transpose(v2))/(np.linalg.norm(v1)*np.linalg.norm(v2)))
def dihedral(v1 : np.array
            ,v2 : np.array
            ,v3 : np.array
            ) -> float:
    """
    http://azevedolab.net/resources/dihedral_angle.pdf
    """
    x12 = np.cross(v1,v2)
    x23 = np.cross(v2,v3)
    n1  = x12/np.linalg.norm(x12)
    n2  = x23/np.linalg.norm(x23)
    u1  = n2
    u3  = v2/np.linalg.norm(v2)
    u2  = np.cross(u3,u1)
    cos_theta = np.dot(n1,u1)
    sin_theta = np.dot(n1,u2)
    theta = -math.atan2(sin_theta,cos_theta)
    return theta


##############
# Element lists
###############
nonmetal_symbs   = ['H','C','N','P','O','S','Se','F','Cl','Br','I','At','He','Ne','Ar','Kr','Xe','Rn']
nonmetals        = [ase.data.chemical_symbols.index(x) for x in nonmetal_symbs]

relevant_atoms = [1,3,4,6,7,8,9,11,12,13,14,16,17] \
                    + list(range(19,36))+list(range(37,52))+[55,56]+list(range(72,80))

relevant_nonmetals = list(set(nonmetals) & set(relevant_atoms))

mag_elems        = ['Fe','Mn','Cr','Co','Ni']
mag_nums         = [24,25,26,27,28]
paw_elems        = ['Li','Be','Na','Mg','K','Ca','Rb','Sr','Cs','Ba','Zn']

def symbols2electrons(symbols : typ.List[str]
                     ,psp 	  : str ='gbrv'
                     ) -> int : # added Be, Cd on my own
    symbdict = {'gbrv':{'Ag':19,'Al':3,'As':5,'Au':11,'Ba':10,'Br':7,'B':3,'Be':4,'Ca':10,'Cd':12,'Co':17,'Cr':14,'Cs':9,'C':4,'Cu':19,'Fe':16,'F':7,'Ga':19,'Ge':14,'Hf':12,'Hg':12,'H':1,'In':13,'Ir':15,'I':7,'K':9,'La':11,'Li':3,'Mg':10,'Mn':15,'Mo':14,'Na':9,'Nb':13,'Ni':18,'N':5,'Os':16,'O':6,'Pb':14,'Pd':16,'Pt':16,'P':5,'Rb':9,'Re':15,'Rh':15,'Ru':16,'Sb':15,'Sc':11,'Se':6,'Si':4,'Sn':14,'Sr':10,'S':6,'Ta':13,'Tc':15,'Te':6,'Ti':2,'Tl':13,'V':13,'W':14,'Y':11,'Zn':20,'Zr':12}}
    return sum([symbdict[psp][x] for x in symbols])

#############
# Site Related
###############
def make_pmg_slab(a : ase.Atoms,facet : typ.List[int]) -> pmg.Structure:
    species             = a.get_chemical_symbols()
    coords              = a.get_positions()
    miller_index        = facet
    oriented_unit_cell  = AseAtomsAdaptor.get_structure(a)
    shift               = 0    #???????
    scale_factor        = None #???????
    return Slab(oriented_unit_cell.lattice, species, coords, miller_index,oriented_unit_cell, shift, scale_factor,coords_are_cartesian=True)

def reorient_z_ase(a : ase.Atoms,facet : typ.List[int]) -> ase.Atoms:
    slab                     = make_pmg_slab(a,facet)
    slab                     = reorient_z(slab)
    out_atoms_obj            = AseAtomsAdaptor.get_atoms(slab)
    out_atoms_obj.cell[2,:2] = 0.
    return out_atoms_obj

def get_sites(a 		  : ase.Atoms
             ,facet 	  : typ.List[int]
             ,site_type   : str  		 	= 'all'
             ,symm_reduce : float 			= 0.0
             ,height 	  : float 			= 0.9
             ) -> typ.Any:
    assert site_type in ['all','bridge','ontop','hollow'], 'Please supply a valid site_type'

    slab  = make_pmg_slab(a,facet)
    slab  = reorient_z(slab)
    sites = AdsorbateSiteFinder(slab,height = height).find_adsorption_sites(symm_reduce=symm_reduce, distance = 0)[site_type]
    return sites



def get_mic_distance(p1       : np.array
                    ,p2 	  : np.array
                    ,cell     : np.array
                    ,pbc 	  : typ.List[int]
                    ,dis_ind  : str = 'xyz'
                    ) -> float:
    """ This method calculates the shortest distance between p1 and p2
         through the cell boundaries defined by cell and pbc.
         This method works for reasonable unit cells, but not for extremely
         elongated ones.
    """
    ct = cell.T
    pos = np.mat((p1, p2))
    scaled = np.linalg.solve(ct, pos.T).T
    for i in range(3):
        if pbc[i]:
            scaled[:, i] %= 1.0
            scaled[:, i] %= 1.0
    P = np.dot(scaled, cell)

    pbc_directions = [[-1, 1] * int(direction) + [0] for direction in pbc]
    translations = np.mat(list(itertools.product(*pbc_directions))).T
    p0r = np.tile(np.reshape(P[0, :], (3, 1)), (1, translations.shape[1]))
    p1r = np.tile(np.reshape(P[1, :], (3, 1)), (1, translations.shape[1]))
    dp_vec = p0r + ct * translations
    if dis_ind == 'xyz':
        squared_dis = np.power((p1r - dp_vec), 2).sum(axis=0)
    elif dis_ind =='xy':
        squared_dis = np.power((p1r - dp_vec)[0:2], 2).sum(axis=0)
    else:
        raise ValueError('Please provide valid direction to include in distance \'xy\' or \'xyz\'')
    d = np.min(squared_dis)**0.5
    return d

def collision(position           : np.array
             ,atom               : ase.Atom
             ,cell               : np.array
             ,pbc                : typ.List[int]
             ,dis_ind            : str   = 'xyz'
             ,collision_distance : float = 2.
             )->bool:
    distance = get_mic_distance(position,atom.position,cell,pbc)
    print (distance)
    return distance < (ase.data.covalent_radii[atom.number])*2/1.124 or distance<collision_distance

def get_mic_vector(p1      : np.array
                  ,p2 	   : np.array
                  ,cell    : np.array
                  ,pbc 	   : typ.List[int]
                  ,dis_ind : str = 'xyz'
                  )-> np.array:
    """ This method calculates the shortest distance between p1 and p2
         through the cell boundaries defined by cell and pbc.
         This method works for reasonable unit cells, but not for extremely
         elongated ones.
    """
    ct = cell.T
    pos = np.mat((p1, p2))
    scaled = np.linalg.solve(ct, pos.T).T
    for i in range(3):
        if pbc[i]:
            scaled[:, i] %= 1.0
            scaled[:, i] %= 1.0
    P = np.dot(scaled, cell)
    pbc_directions = [[-1, 1] * int(direction) + [0] for direction in pbc]
    translations = np.mat(list(itertools.product(*pbc_directions))).T
    p0r = np.tile(np.reshape(P[0, :], (3, 1)), (1, translations.shape[1]))
    p1r = np.tile(np.reshape(P[1, :], (3, 1)), (1, translations.shape[1]))
    dp_vec = p0r + ct * translations
    if dis_ind == 'xyz':
        squared_dis = np.power((p1r - dp_vec), 2).sum(axis=0)
    elif dis_ind =='xy':
        squared_dis = np.power((p1r - dp_vec)[0:2], 2).sum(axis=0)
    else:
        raise ValueError('Please provide valid direction to include in distance \'xy\' or \'xyz\'')
    d = np.min(squared_dis)**0.5
    return d


def delete_atom(atoms_obj : ase.Atoms
               ,ind : int
               ) -> ase.Atoms:
    """
    Returns a new Atoms object with an atom removed at the index
    """
    new_atoms_obj = atoms_obj.copy()
    del new_atoms_obj[ind]
    return new_atoms_obj

def delete_vacancy(parent_atoms_obj : ase.Atoms
                  ,child_atoms_obj  : ase.Atoms
                  ) -> ase.Atoms:
    """
    Docstring
    """
    vac_pos, vac_ind = get_vacancy_pos(parent_atoms_obj, child_atoms_obj)
    return delete_atom(parent_atoms_obj,vac_ind)

def delete_adsorbates(atoms_obj 		: ase.Atoms
                     ,adsorbates_list   : typ.List[typ.List[int]]
                     ) -> ase.Atoms:
    """
    Helpful docstring
    """
    new_atoms_obj = atoms_obj.copy()
    reverse_ordered_adsorbate_list = np.sort(flatten(adsorbates_list))[::-1]
    for ind in reverse_ordered_adsorbate_list:
        new_atoms_obj = delete_atom(new_atoms_obj, ind)
    return new_atoms_obj

def did_it_restructure(atoms_1 				: ase.Atoms
                      ,atoms_2				: ase.Atoms
                      ,restructure_criteria : int 		 = 1
                      ) -> bool:
    """
    Docstring explaining how this algorithm works
    """
    distances_1 = np.linalg.norm(atoms_1.positions, axis = 1)
    distances_2 = np.linalg.norm(atoms_2.positions, axis = 1)
    max_dis = np.max(np.abs(distances_2-distances_1))
    vert_dis = np.max(atoms_1.positions[:,2] - atoms_2.positions[:,2])
    return np.max(np.abs(distances_2-distances_1))>restructure_criteria

def get_vacancy_pos(parent : ase.Atoms
                   ,child  : ase.Atoms
                   ) -> typ.Tuple[np.array,int]:
    """
    Returns the list of length three indicating the location of the vacancy
    position on the slab using the bare_slab parent indicated in the database.
    The parent should be the atoms object of the relaxed bare slab with no
    """
    if len(parent) < len(child): raise ValueError("can't get a vacancy when len(parent)=%d and len(child)=%d"%(len(parent) , len(child)))
    #Find the distances between each atom in the parent object and each of the atoms in the child object
    #Returns list with a length equal to that of the parents object
    distances = map(lambda pos: map(np.linalg.norm,(pos-child.positions)), parent.positions)
    #Find the nearest neighbor between the parent atom and the child atoms
    min_dis = map(np.min, distances)
    #the atom with the largest distance between the parent and child atoms is assumed to be
    # at the location of the vacancy
    return parent.positions[np.argmax(min_dis)], np.argmax(min_dis)

def restore_magmom(trajjson : str) -> str:
    """
    docstring
    """
    traj = json_to_traj(trajjson)
    try:
        mags = traj.get_magmoms()
        if any([x>0 for x in mags]): traj.set_initial_magnetic_moments([3 if e in mag_elems else 0 for e in traj.get_chemical_symbols()])
    except:
        pass
    return traj_to_json(traj)


def smart_view(traj_file : str
              ,expr      : str   = ''
              ) -> None:
    images = Images(images = read(traj_file,':'))
    gui = GUI(images = images, expr= expr)
    gui.run()
    return gui.images[-1]

import os
import subprocess
import sys
import tempfile


def new_view(atoms  : ase.Atoms
            ,data   : typ.Any                = None
            ,viewer : str                    = 'ase'
            ,graph  : str                    = ""
            ,repeat : typ.Tuple[int,int,int] = None
            ,block  : bool                   = False):
    # Ignore for parallel calculations:

    vwr = viewer.lower()

    if vwr == 'ase':
        format = 'traj'
        command = sys.executable + ' -m ase gui'
        if repeat is not None:
            command += ' --repeat={},{},{}'.format(*repeat)
            repeat = None
        command += ' --graph={}'.format(graph)


    fd, filename = tempfile.mkstemp('.' + format, 'ase-')
    if repeat is not None:
        atoms = atoms.repeat()
    if data is None:
        write(filename, atoms, format=format)
    else:
        write(filename, atoms, format=format, data=data)
    if block:
        subprocess.call(command.split() + [filename])
        os.remove(filename)
    else:
        subprocess.Popen(command.split() + [filename])
        subprocess.Popen(['sleep 60; rm {0}'.format(filename)], shell=True)



###################
#Archived Scripts
###################
#
# def get_expt_surf_energy(name : str) -> typ.Optional[float]:
#     if 'x' not in name or '_' not in name: return None
#
#     metal,crystal = name.split('_')[0].split('-')
#     facet = name.split('_')[1].replace(',','')
#
#     if crystal=='hcp' and facet == '001':
#         facet = '0001'
#     try:
#         #convert J/m^2 to eV/A^2
#         return surfdata.get_exp_surface_energy(metal+facet)[1]*0.0624 # type: ignore
#     except KeyError:
#         return None
# def show_sites(a 	 	   : ase.Atoms
#               ,facet 	   : typ.List[int]
#               ,site_type   : str   = 'all'
#               ,symm_reduce : float = 0.01
#               ,height 	   : float = 1.0
#               )-> typ.Any:
#     slab = make_pmg_slab(a,facet)
#     plot_slab(slab,plt.gca(),repeat=3,site_type = site_type, symm_reduce=symm_reduce, height = height)
#     plt.show() # user looks, closes plot to continue
