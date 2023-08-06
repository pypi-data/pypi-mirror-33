# External modules
import typing as typ

import numpy as np                                              # type: ignore
import ase, itertools                                           # type: ignore
import pymatgen as pmg                                          # type: ignore
from ase.constraints               import FixAtoms              # type: ignore
from pymatgen.symmetry.analyzer    import SpacegroupAnalyzer    # type: ignore
from pymatgen.io.ase               import AseAtomsAdaptor       # type: ignore
from pymatgen.core.surface         import (SlabGenerator,Slab,  # type: ignore
                                          get_symmetrically_distinct_miller_indices)    # type: ignore
from pymatgen.analysis.adsorption  import AdsorbateSiteFinder,reorient_z # type: ignore
from pymatgen.core.operations      import SymmOp                           # type: ignore

from catalog.misc.utilities import flatten
################################################################################

"""
Functions to allow a user to create surfaces from completed bulk jobs
"""

#####################################
# Functions for constructing surfaces
#####################################
def make_slab(unit                      : pmg.Structure
              ,facet                    : typ.Tuple[int,int,int]
              ,num_atoms_per_layer      : int
              ,vac                      : float
              ,layers                   : int
              ,sym                      : bool
              ) -> typ.List["ase.Atoms"]:
    """
    Finds the slab thickness input necessary for SlabGenerator to produce slab with correct number of layers
    """
    x0,dx,n = 2.,0.5,0. # Angstrom


    def get_slabs(x: float) -> pmg.Structure:
                slab_gen = SlabGenerator(initial_structure     = unit
                                            ,miller_index      = facet
                                            ,min_slab_size     = x
                                            ,min_vacuum_size   = vac
                                            ,center_slab       = True
                                            ,primitive         = True
                                            ,lll_reduce        = True)
                return slab_gen.get_slabs(symmetrize=sym,repair=True)

    while n<num_atoms_per_layer*layers:
        x0+=dx
        slab_strucs = get_slabs(x0)
        if len(slab_strucs) == 0:
            n = 0
        else:
            n = len(slab_strucs[0])
        if n > 100:
            raise ValueError('over 50 atoms in primitive surface column (' +str(len(get_slabs(x0)))+') not compatible with requested # of layers ('+str(layers)+')')
        if len(slab_strucs)>1:
            print('WARNING MULTIPLE SLABS FOR FACE = {}'.format(facet))
    atoms_objs = []
    for struc in slab_strucs:
        atoms_obj = AseAtomsAdaptor.get_atoms(struc)
        atoms_obj = reindex_by_height(atoms_obj)
        while len(atoms_obj) != layers*num_atoms_per_layer:
            for ind in range(num_atoms_per_layer):
                del atoms_obj[-1]
        atoms_objs.append(atoms_obj)
    return atoms_objs

def reindex_by_height(atoms : ase.Atoms) -> ase.Atoms:
    H = [atom.position[2] for atom in atoms]
    atoms_new = atoms.copy()
    ind = np.argsort(H)
    del atoms_new[:]
    for i in ind:
        atoms_new.append(atoms[i])
    return atoms_new

def flip_atoms(atoms: ase.Atoms) -> ase.Atoms:
    flipped_atoms = atoms.copy()
    flipped_atoms.rotate(v = [1,0,0], a=180, center = 'COP')
    return flipped_atoms

def align_unit_cell(atoms: ase.Atoms) -> ase.Atoms:
    angle = np.arccos(np.dot(atoms.cell[0],[1,0,0])/np.linalg.norm(atoms.cell[0]))
    angle *= 180/np.pi
    rotated_atoms = atoms.copy()
    rotated_atoms.rotate(v = [1,0,0], a = angle, rotate_cell = True)
    return rotated_atoms


def tag_atoms(atoms                 : ase.Atoms
             ,num_layers            : int
             ,num_bins              : int       = 20
             ) -> ase.Atoms:
    # reindex the input Atoms object by height and tag using evenly placed bins
    # that divide the layers into 20
    #atoms     = AseAtomsAdaptor.get_atoms(atoms)
    atoms_new  = reindex_by_height(atoms)
    num_atoms_per_layer = len(atoms_new)/num_layers
    height     = [round(atom.position[2],4) for atom in atoms_new]
    binH       = np.digitize(height,np.linspace(min(height)*0.99,max(height)*1.01,num_bins))
    binind     = list(np.sort(list(set(binH))))
    binind.reverse()
    tag_curr = num_layers + 1
    for i in range(len(binH)):
        if i%num_atoms_per_layer==0:
            tag_curr -= 1
        atoms_new[i].tag = tag_curr
    return atoms_new

def constrainAtoms(atoms              : ase.Atoms
                  ,constrained_layers : typ.List[int]
                  ,sym                : bool
                  ) -> ase.Atoms:
    # maxTag = max([a.tag for a in atoms])
    # if sym:
    #     if maxTag%2 != nConstrained%2: raise ValueError('Impossible to have symmetric slab with %d layers and %d fixed'%(maxTag,nConstrained))
    #     else:     skip = (maxTag - nConstrained) / 2 #should be integer
    # else: skip = 0
    # constrainedLayers = range(maxTag-nConstrained+1-skip,maxTag+1-skip)
    constrained_atoms = []
    for i,a in enumerate(atoms):
        if a.tag in constrained_layers: constrained_atoms.append(i)
    return constrained_atoms

def is_symmetric_in_z(slab : pmg.Structure) -> bool:
        symmops = SpacegroupAnalyzer(slab).get_symmetry_operations()
        rotation_matrices = [op.rotation_matrix for op in symmops]
        x = np.array([[1.,0.,0.],[0.,-1.,0.],[0.,0.,-1.]])
        return any([(x == rot_mat).all() for rot_mat in rotation_matrices])

def get_unique_facets(atoms     : ase.Atoms
                     ,max_index : int
                     ) -> typ.List[typ.Tuple[int,int,int]]:
    bulkstruct = AseAtomsAdaptor.get_structure(atoms) #Converts ASE atoms to PyMatgen structures (atom -> sites)
    sga = SpacegroupAnalyzer(bulkstruct, 0.1) #Find crystal structure
    bulkstruct = sga.get_conventional_standard_structure()
    return get_symmetrically_distinct_miller_indices(bulkstruct,max_index)

def get_emt_energy(atoms        : ase.Atoms) -> float:
    import emt  # type: ignore
    atoms.set_calculator(emt.EMT())
    return atoms.get_potential_energy()

##############
# Main Scripts
##############

def makeSlab(ase_atoms  : ase.Atoms
            ,facet      : typ.Tuple[int,int,int]
            ,lay        : int
            ,sym        : bool
            ,xy         : typ.Tuple[int,int]
            ,vac        : float
            )->typ.List[pmg.Structure]:
    """
    helpful docstring
    """
    pmg_a    = AseAtomsAdaptor.get_structure(ase_atoms)
    sga      = SpacegroupAnalyzer(pmg_a,symprec=0.1)
    unit     = sga.get_conventional_standard_structure()
    num_atoms_per_layer = len(sga.get_primitive_standard_structure())
    atoms_objs = make_slab(unit,facet,num_atoms_per_layer,vac,lay,sym)
    slabs = [AseAtomsAdaptor.get_structure(atoms_obj) for atoms_obj in atoms_objs]
    slabs = list(map(reorient_z,slabs))
    return slabs

def bulk2surf(bulk              : ase.Atoms
             ,facet             : typ.Tuple[int,int,int]
             ,xy                : typ.Tuple[int,int]
             ,layers            : int
             ,constrained       : typ.List[int]
             ,symmetric         : bool
             ,vacuum            : float
             ,turn_on_magmoms   : bool      = False
             ) -> dict:
    """
    helpful docstring
    """
    magmomInit              = 3
    magElems                = ['Fe','Mn','Cr','Co','Ni']
    bare_slabs              = makeSlab(bulk,facet,layers,symmetric,xy,vacuum)
    bare_ase_objs_tops      = list(map(AseAtomsAdaptor.get_atoms, bare_slabs))
    symm_slab_list          = list(map(is_symmetric_in_z,bare_slabs))
    bare_ase_objs_bottoms   = []
    for bare_ase, symm_slab in zip(bare_ase_objs_tops,symm_slab_list):
        if not symm_slab:
            bare_ase_objs_bottoms.append(flip_atoms(bare_ase))

    output_dict = {'top':bare_ase_objs_tops,'bottom':bare_ase_objs_bottoms}
    for side, atoms_list in output_dict.items():
        for i, atoms_curr in enumerate(atoms_list):
            atoms_curr = tag_atoms(atoms_curr, layers)
            constrain_inds = constrainAtoms(atoms_curr,constrained,symmetric)
            atoms_curr.set_constraint(FixAtoms(indices=constrain_inds))
            if turn_on_magmoms:
                magmoms      = [magmomInit if (magmomInit and e in magElems) else 0 for e in atoms_curr.get_chemical_symbols()]
                atoms_curr.set_initial_magnetic_moments(magmoms)
            atoms_curr.set_pbc((True, True, False))
            atoms_curr.center()
            atoms_curr.cell[2,0] = 0
            atoms_curr.cell[2,1] = 0
            atoms_curr = align_unit_cell(atoms_curr)
            atoms_curr*=[xy[0],xy[1],1]
            atoms_curr.__setattr__('side',side)
            atoms_curr.wrap()
            atoms_list[i] = atoms_curr
    return output_dict
