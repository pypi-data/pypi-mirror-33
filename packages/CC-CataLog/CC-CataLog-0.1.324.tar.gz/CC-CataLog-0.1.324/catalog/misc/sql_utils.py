# Typing Modules
import typing as typ

# #External Modules
import os,json
from pprint import pformat
from time import sleep

#--sql imports
import sql                                                      # type: ignore
from sql import As,Table,Join,Flavor,Literal                    # type: ignore
from sql.operators import In,And,Or,Not,Concat,Mod,Like,NotLike # type: ignore
from sql.functions import Function,Substring,Round,Random       # type: ignore

from MySQLdb import connect,Connection,OperationalError         # type: ignore
from MySQLdb.cursors import Cursor,DictCursor                   # type: ignore

################################################################################

# ######################
# # Connection for the MySQL database
# # --------------------

localuser = os.environ["USER"]

class ConnectInfo(object):
    """MySQL connection info """
    def __init__(self
                ,host   : str = '127.0.0.1'
                ,port   : int = 3306
                ,user   : str = localuser
                ,passwd : str = localuser
                ,db     : str = 'suncat'
                ) -> None:
        self.host   = host
        self.port   = port
        self.user   = user
        self.passwd = passwd
        self.db     = db

    def __str__(self)->str:
        return pformat(self.__dict__)

    def __eq__(self,other : object)->bool:
        return self.__dict__==other.__dict__

    def mk_conn(self
               ,mk_dict : bool = False
               ,attempt : int  = 10
               ) -> Connection:
        try:
            con = connect(host   = self.host
                          ,port   = self.port
                          ,user   = self.user
                          ,passwd = self.passwd
                          ,db     = self.db
                          ,cursorclass = DictCursor if mk_dict else Cursor
                          ,connect_timeout=28800)
                          #,wait_timeout = 28800
                          #,interactive_timeout = 28800)

        except OperationalError as e:
            if attempt > 0:
                sleep(5)
                con = self.mk_conn(mk_dict,attempt-1)
            else:
                raise OperationalError(e)
        con.query('SET SESSION wait_timeout=28800')
        return con

#####################
# Auxillary Functions
#--------------------
def joiner_simple(first_table : sql.Table
                 ,dictionary  : dict
                 ) -> sql.Join:
    """
    Concisely express a join
    This function is needed because Mike's joiner breaks when your join condition
    is itself a list (i.e. joining on 2+ conditions)

    New format for specifying join type: dictionary value is a TUPLE (c,t)
    """
    output = first_table
    for t,c in dictionary.items():
        if isinstance(c,tuple):            c,typ = c
        else: typ = 'INNER'
        output=Join(output,t,condition=c,type_ = typ)
    return output

def joiner(first_table      : sql.Table
          ,subsequent_dict  : dict
          ,join_type        : str           = 'INNER'
          ) -> sql.Join:
    """
    Concisely express a join

    no longer supports 'subsequent_dict' being a list
    """
    output = first_table

    for t,c in subsequent_dict.items():
        if isinstance(c,list) and not isinstance(c,sql.operators.And) and len(c)>1:
            output=Join(output,t,condition=c[0], type_ = c[1])
        else:
            output=Join(output,t,condition=c, type_ = join_type)
    return output

def join_joins(first_join   : typ.Any
              ,second_join  : typ.Any
              ,condition    : typ.Any
              ,join_type    : str       =  'INNER'
              ) -> typ.Any:
    """
    Typing was probably done completely wrong
    """
    from catalog.misc.utilities import merge_dicts
    first_main_table, first_dictionary = unpack_joins(first_join)
    second_main_table, second_dictionary  = unpack_joins(second_join)
    new_condition = {second_main_table : [condition, join_type]}
    return joiner(first_main_table, [new_condition,first_dictionary, second_dictionary])  # type: ignore

def unpack_joins(joined_tables : typ.Any
                 ) -> typ.Any:
    """
    Turns a join statement into the input used to create it
    """
    from catalog.misc.utilities import merge_dicts
    left        = joined_tables.left
    right       = joined_tables.right
    condition   = joined_tables.condition
    join_type   = joined_tables.type_
    if isinstance(left,Table) and isinstance(right,Table):
        return [left, {right:[condition, join_type]}]
    elif isinstance(left,Table):
        output = unpack_joins(right)
        output[1] = merge_dicts([output[1], {left: [condition, join_type]}])
        return output
    else:
        output = unpack_joins(left)
        output[1] = merge_dicts([output[1], {right: [condition, join_type]}])
        return output

def table_names(joined_tables : typ.Any
                )->typ.List[str]:
    """
    Turns a join statement into the input used to create it
    """
    if isinstance(joined_tables,Table):
        return [joined_tables._name]

    left        = joined_tables.left
    right       = joined_tables.right
    if isinstance(left,Table) and isinstance(right,Table):
        return [left._name, right._name]
    elif isinstance(left,Table):
        output = table_names(right)
        output += [left._name]
        return output
    else:
        output = table_names(left)
        output += [right._name]
        return output

def concat(*args : typ.Any) -> sql.operators.Concat:
    """
    Concat a list of objects
    """
    output = Concat(*args[-2:])
    for a in reversed(args[:-2]): output=Concat(a,output)
    return output

def AND(*args : typ.Any) -> sql.operators.And:
    args = list(filter(None,args)) # type: ignore
    if len(args)==0: return None
    return And(args)

def OR(*args : typ.Any) -> sql.operators.Or:
    # args = [a for a in args if a not in [None,[]]]  # type: ignore
    # if len(args)==0: return None
    return Or(args)

#############
# Function Definitions
#------------
class UDF(Function):         __slots__ = () ; _function = 'user_defined_function'
class ABS(Function):         __slots__ = () ; _function = 'abs'
class SQRT(Function):        __slots__ = (); _function = 'sqrt'
class SUBSTR(Function):      __slots__ = () ; _function = 'substr'
class IFNULL(Function):      __slots__ = () ; _function = 'ifnull'
class GROUPCONCAT(Function): __slots__ = () ; _function = 'group_concat'
class CON(Function):      __slots__ = () ; _function = 'concat'
class DISTINCT(Function):    __slots__ = () ; _function = 'Distinct'
class IIF(Function):         __slots__ = () ; _function = 'IIF'
class FLOAT(Function):         __slots__ = () ; _function = '1.0*'

#########
# Tables
#-------
tbl_adsorbate               = Table('adsorbate')
tbl_adsorbate_composition   = Table('adsorbate_composition')
tbl_ads_triple              = Table('ads_triple')
tbl_alljob                  = Table('alljob')
tbl_atom                    = Table('atom')
tbl_bond                    = Table('bond')
tbl_bulk                    = Table('bulk')
tbl_bulkmod_job             = Table('bulkmod_job')
tbl_bulkspecies             = Table('bulkspecies')
tbl_calc                    = Table('calc')
tbl_calc_other              = Table('calc_other')
tbl_cell                    = Table('cell')
tbl_chargemol_atom          = Table('chargemol_atom')
tbl_chargemol_job           = Table('chargemol_job')
tbl_chargemol_map           = Table('chargemol_map')
tbl_dos_job                 = Table('dos_job')
tbl_element                 = Table('element')
tbl_graph                   = Table('graph')
tbl_graph_params            = Table('graph_params')
tbl_hyperparameter          = Table('hyperparameter')
tbl_yperparameter_type      = Table('yperparameter_type')
tbl_hyperparameter_value    = Table('hyperparameter_value')
tbl_keld_solids             = Table('keld_solids')
tbl_META_dependencies       = Table('META_dependencies')
tbl_ETA_transform           = Table('ETA_transform')
tbl_molecule                = Table('molecule')
tbl_molspecies              = Table('molspecies')
tbl_neb_job                 = Table('neb_job')
tbl_pure_struct             = Table('pure_struct')
tbl_ref_scheme              = Table('ref_scheme')
tbl_ref_scheme_elem         = Table('ref_scheme_elem')
tbl_ref_scheme_job          = Table('ref_scheme_job')
tbl_ref_scheme_refstruct    = Table('ref_scheme_refstruct')
tbl_ref_scheme_reqs         = Table('ref_scheme_reqs')
tbl_ref_scheme_stoich       = Table('ref_scheme_stoich')
tbl_relax_job               = Table('relax_job')
tbl_roots                   = Table('roots')
tbl_rxn                     = Table('rxn')
tbl_rxn_dataset             = Table('rxn_dataset')
tbl_rxn_dataset_element     = Table('rxn_dataset_element')
tbl_similar_struct          = Table('similar_struct')
tbl_species                 = Table('species')
tbl_species_composition     = Table('species_composition')
tbl_stoich                  = Table('stoich')
tbl_struct                  = Table('struct')
tbl_struct_adsorbate        = Table('struct_adsorbate')
tbl_struct_composition      = Table('struct_composition')
tbl_struct_dataset          = Table('struct_dataset')
tbl_truct_dataset_element   = Table('truct_dataset_element')
tbl_surface                 = Table('surface')
tbl_surfspecies             = Table('surfspecies')
tbl_traj                    = Table('traj')
tbl_trajatom                = Table('trajatom')
tbl_vib_job                 = Table('vib_job')
tbl_finaltraj               = Table('finaltraj')
tbl_job                     = Table('job')

# ######################
# # Table Joins
# # --------------------
tbl_relaxfinal = joiner(tbl_relax_job,{
                         tbl_job                 : tbl_job.job_id                     == tbl_relax_job.job_id
                        ,tbl_finaltraj           : tbl_finaltraj.job_id               == tbl_relax_job.job_id
                        ,tbl_struct              : tbl_struct.struct_id               == tbl_finaltraj.struct_id
                        ,tbl_calc                : tbl_relax_job.calc_id              == tbl_calc.calc_id
                        ,tbl_calc_other          : tbl_relax_job.calc_other_id        == tbl_calc_other.calc_other_id
                        })

tbl_relaxfinal_surface   = joiner(tbl_relaxfinal,{
                         tbl_surface : tbl_struct.struct_id == tbl_surface.struct_id
                         })

tbl_relaxfinal_bulk      = joiner(tbl_relaxfinal,{
                         tbl_bulk : tbl_struct.struct_id == tbl_bulk.struct_id
                         })

tbl_relaxfinal_molecule  = joiner(tbl_relaxfinal,{
                         tbl_molecule : tbl_struct.struct_id == tbl_molecule.struct_id
                         })

tbl_relaxfinal_all       = joiner(tbl_relaxfinal,{
                          tbl_molecule : [tbl_struct.struct_id == tbl_molecule.struct_id, 'LEFT']
                         ,tbl_bulk     : [tbl_struct.struct_id == tbl_bulk.struct_id, 'LEFT']
                         ,tbl_surface  : [tbl_struct.struct_id == tbl_surface.struct_id, 'LEFT']
                         })

# ######################
# # Adsorption Query
# # --------------------
T       = Table('ads_triple')
BF      = Table('finaltraj')
CF      = Table('finaltraj')
BR      = Table('relax_job')
CR      = Table('relax_job')
BJ      = Table('job')
CJ      = Table('job')
BS      = Table('struct')
CS      = Table('struct')
BC      = Table('calc_other')
CC      = Table('calc_other')
A       = Table('ads_eng')
AF      = Table('finaltraj')
AS      = Table('struct')
AJ      = Table('job')
AC      = Table('calc_other')

tbl_eads       = joiner(T, {
                        BF : BF.job_id           == T.bare_id
                       ,CF : CF.job_id           == T.complex_id
                       ,BR : BR.job_id           == T.bare_id
                       ,CR : CR.job_id           == T.complex_id
                       ,BJ : BJ.job_id           == T.bare_id
                       ,CJ : CJ.job_id           == T.complex_id
                       ,BS : BS.struct_id        == BF.struct_id
                       ,CS : CS.struct_id        == CF.struct_id
                       ,BC : BC.calc_other_id    == BR.calc_other_id
                       ,CC : CC.calc_other_id    == CR.calc_other_id
                       ,A  : And([A.adsorbate_id == T.adsorbate_id, A.calc_id == T.calc_id])
                       ,AJ : AJ.job_id           == A.job_id
                       ,AC : AC.calc_other_id    == A.calc_other_id
                       ,AF : AF.job_id           == AJ.job_id
                       ,AS : AS.struct_id        == AF.struct_id
                       })

eads_columns_inner  = [T.bare_id
                      ,T.complex_id
                      ,T.delta_e_surf
                      ,As(CJ.job_name,'complex_name')
                      ,As(BJ.job_name,'bare_name')
                      ,A.name
                      ,A.ref_scheme_id
                      ,A.energy_norm
                      ,A.coef
                      ,A.number
                      ,A.element_id
                      ,A.component
                      ,As(GROUPCONCAT(A.job_id),'jobs')]

eads_group_by_inner = [A.ref_scheme_id
                      ,A.calc_id
                      ,A.adsorbate_id
                      ,A.element_id
                      ,A.component_id
                      ,T.complex_id
                      ,T.bare_id]

###############
# Col shortcuts
# -------------
#--job table
JOB                         = tbl_job.job_id
USER                        = tbl_job.user
JOBCODE                     = tbl_job.code
DELETED                     = tbl_job.deleted
JOBNAME                     = tbl_job.job_name
JOBTYPE                     = tbl_job.job_type
LOGFILE                     = tbl_job.logfile
STORDIR                     = tbl_job.stordir
TIMESTAMP                   = tbl_job.timestamp
WORKDIR                     = tbl_job.working_directory
ADSORBATES                  = tbl_job.ads_catalog
STRUCTURE                   = tbl_job.structure_catalog

#--relax_job table
RELAX_JOB                   = tbl_relax_job.job_id
RELAX_CALC                  = tbl_relax_job.calc_id
RELAX_CALC_OTHER            = tbl_relax_job.calc_other_id
REFERENCE                   = tbl_relax_job.calc_other_id

#--traj table
TRAJ                        = tbl_traj.traj_id
TRAJ_JOB                    = tbl_traj.job_id
TRAJ_STRUCT                 = tbl_traj.struct_id
FINAL                       = tbl_traj.final
RAWENG                      = tbl_finaltraj.energy
KPTDEN_X                    = tbl_traj.kptden_x
KPTDEN_Y                    = tbl_traj.kptden_y
KPTDEN_Z                    = tbl_traj.kptden_z

#--struct table
STRUCT                      = tbl_struct.id
STRUCT_CELL                 = tbl_struct.cell_id
RAW                         = tbl_struct.raw
SYSTYPE                     = tbl_struct.system_type
NATOMS                      = tbl_struct.n_atoms
NELEMS                      = tbl_struct.n_elems
# struct columns to be aliased
#                           = tbl_struct.composition
#                           = tbl_struct.composition_norm
#                           = tbl_struct.metal_comp
#                           = tbl_struct.str_symbols
#                           = tbl_struct.str_constraints
#                           = tbl_struct.symmetry
#                           = tbl_struct.pure_struct_id
#                           = tbl_struct.species_id
#                           = tbl_struct.spacegroup
#                           = tbl_struct.geo_graph
#                           = tbl_struct.elemental
#                           = tbl_struct.pure_struct_id_catalog
#                           = tbl_struct.rawhash

#--surface table
SURFACE                     = tbl_surface.struct_id
VACUUM                      = tbl_surface.vacuum
SURFACE_PURE_STRUCT         = tbl_surface.pure_struct_id
H                           = tbl_surface.facet_h
K                           = tbl_surface.facet_k
L                           = tbl_surface.facet_l
SURFACE_PURE_STRUCT_CATALOG = tbl_surface.pure_struct_id_catalog
H_CATALOG                   = tbl_surface.facet_h_catalog
K_CATALOG                   = tbl_surface.facet_k_catalog
L_CATALOG                   = tbl_surface.facet_l_catalog
FACET                       = CON('[',H,',',K,',',L,']')
FACET_CATALOG               = CON('[',H_CATALOG,',',K_CATALOG,',',L_CATALOG,']')


#--pure_struct table
PURE_STRUCT                 = tbl_pure_struct.pure_struct_id
NAME                        = tbl_pure_struct.name
SPACEGROUP                  = tbl_pure_struct.spacegroup
FREE                        = tbl_pure_struct.free
NICKNAME                    = tbl_pure_struct.nickname



#--calc table
CALC                = tbl_calc.id
DFTCODE             = tbl_calc.dftcode
XC                  = tbl_calc.xc
PW                  = tbl_calc.pw
PSP                 = tbl_calc.psp

#--calc_other table
CALC_OTHER          = tbl_calc_other.calc_other_id
KX                  = tbl_calc_other.kx
KY                  = tbl_calc_other.ky
KZ                  = tbl_calc_other.kz
FMAX                = tbl_calc_other.fmax
ECONV               = tbl_calc_other.econv
XTOL                = tbl_calc_other.xtol
STRAIN              = tbl_calc_other.strain
DW                  = tbl_calc_other.dw
SIGMA               = tbl_calc_other.sigma
NBANDS              = tbl_calc_other.nbands
MIXING              = tbl_calc_other.mixing
NMIX                = tbl_calc_other.nmix
GGA                 = tbl_calc_other.gga
LUSE_VDW            = tbl_calc_other.luse_vdw
ZAB_VDW             = tbl_calc_other.zab_vdw
NELMDL              = tbl_calc_other.nelmdl
GAMMA               = tbl_calc_other.gamma
DIPOL               = tbl_calc_other.dipol
ALGO                = tbl_calc_other.algo
IBRION              = tbl_calc_other.ibrion
PREC                = tbl_calc_other.prec
IONIC_STEPS         = tbl_calc_other.ionic_steps
LREAL               = tbl_calc_other.lreal
LVHAR               = tbl_calc_other.lvhar
DIAG                = tbl_calc_other.diag
SPINPOL             = tbl_calc_other.spinpol
DIPOLE              = tbl_calc_other.dipole
MAXSTEP             = tbl_calc_other.maxstep
DELTA               = tbl_calc_other.delta
MIXINGTYPE          = tbl_calc_other.mixingtype
BONDED_INDS         = tbl_calc_other.bonded_inds
ENERGY_CUTOFF       = tbl_calc_other.energy_cut_off
STEP_SIZE           = tbl_calc_other.step_size
SPRINGS             = tbl_calc_other.springs



ADSID               = tbl_atom.adsorbate_id
ADSID_CATALOG       = tbl_atom.adsorbate_id_catalog
ATOM                = tbl_atom.atom_id
CONSTRAINED         = tbl_atom.constrained
ATOM_TO_ELEMENT     = tbl_atom.element_id
LAYER               = tbl_atom.layer
MAGMOM              = tbl_atom.magmom
ATOM_TO_PURE_STRUCT = tbl_atom.pure_struct_id
ATOM_STRUCT_ID      = tbl_atom.struct_id
X                   = tbl_atom.x
Y                   = tbl_atom.y
Z                   = tbl_atom.z

# ######################
# # Constraint shortcuts
# # --------------------
JOB_          = lambda x: JOB       == x
JOB_IN_       = lambda x: In(JOB,x)
JOBNAME_      = lambda x: JOBNAME   == x
JOBNAME_LIKE_ = lambda x: Like(JOBNAME,x)

ATOM_         = lambda x: ATOM      == x
STRUCT_       = lambda x: STRUCT    == x
CALC_         = lambda x: CALC      == x
STRUCTURE_    = lambda x: STRUCTURE == x
STORDIR_      = lambda x: STORDIR == x                      # type: ignore
JOBNAME_      = lambda x: JOBNAME == x                      # type: ignore
#
USER_    = lambda x: USER == x                              # type: ignore
KSB_     = USER_('ksb')                                     # type: ignore
MSTATT_  = USER_('mstatt')                                  # type: ignore
AAYUSH_  = USER_('aayush')                                  # type: ignore

def JOBTYPE_(x): return JOBTYPE == x                        # type: ignore
LATTICEOPT_ = JOBTYPE_('latticeopt')                        # type: ignore
BULKMOD_    = JOBTYPE_('bulkmod')                           # type: ignore
VIB_        = JOBTYPE_('vib')                               # type: ignore
VCRELAX_    = JOBTYPE_('vcrelax')                           # type: ignore
RELAX_      = JOBTYPE_('relax')                             # type: ignore
DOS_        = JOBTYPE_('dos')                               # type: ignore
NEB_        = JOBTYPE_('neb')                               # type: ignore
XCCONTRIBS_ = JOBTYPE_('xc')                                # type: ignore

RELAXORLAT_  = OR(LATTICEOPT_,VCRELAX_,RELAX_)

def NATOMS_(x): return NATOMS == x                          # type: ignore
PW_ = lambda x: PW==x                                       # type : ignore
def XC_(x : str) -> bool: return XC == x                    # type : ignore
PBE_   = XC_('PBE')                                         # type : ignore
RPBE_  = XC_('RPBE')                                        # type : ignore
BEEF_  = XC_('BEEF')                                        # type : ignore
MBEEF_ = XC_('mBEEF')                                       # type : ignore

def DFTCODE_(x): return DFTCODE==x                          # type: ignore
GPAW_ = DFTCODE_('gpaw')                                    # type: ignore
QE_ = DFTCODE_('quantumespresso')                           # type: ignore
VASP_ = DFTCODE_('vasp')                                    # type: ignore

def NICKNAME_(x): return NICKNAME == x                    # type: ignore
HCP_     = NICKNAME_('hexagonal')                          # type: ignore
FCC_     = NICKNAME_('fcc')                                # type: ignore
BCC_     = NICKNAME_('bcc')                                # type: ignore
DIAMOND_ = NICKNAME_('diamond')                            # type: ignore
#
def SYSTYPE_(x): return SYSTYPE == x                        # type: ignore
SURFACE_     = SYSTYPE_('surface')                          # type: ignore
BULK_        = SYSTYPE_('bulk')                             # type: ignore
MOLECULE_    = SYSTYPE_('molecule')                         # type: ignore

def facet(x): return FACET == json.dumps(x)                 # type: ignore
F111_ = facet([1,1,1])                                      # type: ignore
F110_ = facet([1,1,0])                                      # type: ignore
F001_ = facet([0,0,1])                                      # type: ignore


# ######################
# # Archived Scripts
# # --------------------

# #################
# # Join conditions
# #---------------
# atom__job           = atom.atoms_id == job.finalatoms
# atom__atoms         = atom.atoms_id == atoms.id
# atom__refstoich     = atom.number   == refstoich.reference_element
# atom__element       = atom.number   == element.id
#
# calc__job           = calc.id       == job.calc_id
# calc__refeng        = calc.id       == refeng.calc_id
#
# atoms__job          = atoms.id      == job.finalatoms
# atoms__cell         = cell.id       == atoms.cell_id
# atom__refeng        = atom.number   == refeng.element_id
#
# atoms__composition  = atoms.id               == composition.atoms_id
# composition__job    = composition.atoms_id   == job.finalatoms
# composition__refeng = composition.element_id == refeng.element_id
#
# init_or_finalatoms  = OR(job.finalatoms  == atoms.id, job.initatoms   == atoms.id)
# init_or_finalatoms2 = OR(job.finalatoms  == atom.atoms_id
#                         ,job.initatoms   == atom.atoms_id)
#
# atom__composition   = AND(atom.atoms_id  == composition.atoms_id
#                          ,atom.number    == composition.element_id)
#
# Columns to be aliased
# = tbl_atom.struct_adsorbate_id
# = tbl_atom.struct_adsorbate_id_catalog
# = tbl_atom.tag
# = tbl_atom.v10
# = tbl_atom.v3
# = tbl_atom.v4
# = tbl_atom.v5
# = tbl_atom.v6
# = tbl_atom.v7
# = tbl_atom.v8
# = tbl_atom.v9

# CALC_ID     = tbl_job.calc_id
# INITATOMS   = tbl_job.initatoms
# FINALATOMS  = tbl_job.finalatoms
####

# KPTDEN_X    = tbl_job.kptden_x
# KPTDEN_Y    = tbl_job.kptden_y
# KPTDEN_Z    = tbl_job.kptden_z
# PARENT      = tbl_job.parent
# BULKMODULUS = tbl_job.bulk_modulus
# ADSORBATES  = tbl_job.adsorbates
# STRJOB_EXACT = tbl_job.strjob_exact
# STRJOB_GRAPH = tbl_job.strjob_graph
#
# CHARGEMOL   = tbl_job.chargemol
# GRAPH       = tbl_job.graph
# FWID        = tbl_job.fwid
# BLANK       = tbl_job.blank
# RAWENG      = tbl_job.raw_energy
# SURFENG     = tbl_job.surface_energy
# RAWG        = tbl_job.raw_g
# REFJOB      = tbl_job.refjob
# EFORM       = tbl_job.eform
# GFORM       = tbl_job.gform
# EADS        = tbl_job.e_ads
# GADS        = tbl_job.g_ads
# VIBFREQS    = tbl_job.vib_freqs
####################
#
# ATOM        = atom.id
# IND         = atom.ind
# NUMBER      = atom.number
# X           = atom.x
# Y           = atom.y
# Z           = atom.z
# CONSTRAINED = atom.constrained
# MAGMOM      = atom.magmom
# TAG         = atom.tag
# ATOMSID     = atom.atoms_id
# ADSORBATE   = atom.adsorbate
# ####
# COORDNUM    = atom.coordination_number
# Q4          = atom.q4
# Q6          = atom.q6



#
# ####################




# ###
# NATOMS      = atoms.natoms
# NATOMS_CONSTRAINED = atoms.natoms_constrained
# SYSTYPE     = atoms.system_type
# POINTGROUP  = atoms.pointgroup
# SPACEGROUP  = atoms.spacegroup
# STRUCTURE   = atoms.structure
# FACET       = atoms.facet
# SURFACEAREA = atoms.surface_area
# VOLUME      = atoms.volume
# HAS_ADS     = atoms.has_ads
# SYMSLAB     = atoms.sym_slab
# ADS_NELEMS  = atoms.ads_nelems
# NELEMS      = atoms.nelems


# ####################
# CELL  = cell.id
# AX    = cell.ax
# AY    = cell.ay
# AZ    = cell.az
# BX    = cell.bx
# BY    = cell.by
# BZ    = cell.bz
# CX    = cell.cx
# CY    = cell.cy
# CZ    = cell.cz
# ####################
# #####
# ELEMENT       = element.id
# REFSPACEGROUP = element.reference_spacegroup
# REFENG        = refeng.id
# ALL_EREF      = refeng.all_eref
# ALL_GREF      = refeng.all_gref
# EREF          = refeng.eref
# GREF          = refeng.gref
# EATOM         = refeng.eatom
# GATOM         = refeng.gatom
# #############
# REFSTOICH     = refstoich.id
# REF_ELM       = refstoich.reference_element
# COMPONENT_ELM = refstoich.component_element
# COMPWEIGHT    = refstoich.component_weight
# TOT_COMPS     = refstoich.total_components
# ########
# COMPOSITION   = composition.id
# HAS           = composition.has
# CONST_HAS     = composition.const_has
# COUNT         = composition.count
# CONST_COUNT   = composition.const_count
# ADS_COUNT     = composition.ads_count
# FRAC          = composition.frac
# CONST_FRAC    = composition.const_frac
#
#


# NUMBER_    = lambda x: NUMBER    == x
#
# ADSORBATE_ = lambda x: ADSORBATE == x
# ADSORBATES_ = lambda x: ADSORBATES == x
# BARE_ = ADSORBATES_('[]') # type: ignore
#
# FWID_    = lambda x: FWID == x
# FWIDS_   = lambda xs: In(FWID,tuple(xs))
#
# STRJOB_EXACT_ = lambda x: STRJOB_EXACT == x
# STRJOB_GRAPH_ = lambda x: STRJOB_GRAPH == x
# GRAPH_        = lambda x: GRAPH == x

# def NATOMS_CONSTRAINED_(x): return NATOMS_CONSTRAINED == x  # type: ignore
#

#
# def PSP_(x): return PSP == x                                # type: ignore
# SG15_   = PSP_('sg15')                                      # type: ignore
# GBRV_   = PSP_('gbrv15pbe')                                 # type: ignore
# PAW_    = PSP_('paw')                                       # type: ignore
# OLDPAW_ = PSP_('oldpaw')                                    # type: ignore
#
# KPTS_    = lambda x: KPTS==x                                # type: ignore
# KPTLOW_  = KPTDEN_X < 4
# KPTHIGH_ = Not(KPTLOW_)
#
# ECONV_ = lambda x: ECONV == x
# MIXING_ = lambda x: MIXING == x
# NMIX_   = lambda x: NMIX == x
# FMAX_   = lambda x: FMAX == x
# SPINPOL_ = lambda x: SPINPOL==x
# PARENT_  = lambda x: PARENT == x

#
# cp = {FCC_:F111_, BCC_:F110_, HCP_:F001_}
#
# CLOSEPACKED_ = Or([And([st,f]) for st,f in cp.items()])
#
#
# relevent_atoms = [1,3,4,6,7,8,9,11,12,13,14,16,17] \
#                     + list(range(19,36))+list(range(37,52))+[55,56]+list(range(72,80))
#
# H2_ = REFJOB == 1
# LI_ = REFJOB == 3
# BE_ = REFJOB == 4
# CO_ = REFJOB == 6
# N2_ = REFJOB == 7
# H2O_= REFJOB == 8
# F2_ = REFJOB == 9
# NA_ = REFJOB == 11
# MG_ = REFJOB == 12
# AL_ = REFJOB == 13
# SI_ = REFJOB == 14
# CL2_= REFJOB == 17
# K_  = REFJOB == 19
# CA_ = REFJOB == 20
# SC_ = REFJOB == 21
# TI_ = REFJOB == 22
# V_  = REFJOB == 23
# CR_ = REFJOB == 24
# MN_ = REFJOB == 25
# FE_ = REFJOB == 26
# CO_ = REFJOB == 27
# NI_ = REFJOB == 28
# CU_ = REFJOB == 29
# ZN_ = REFJOB == 30
# GE_ = REFJOB == 32
# BR2_= REFJOB == 35
# RB_ = REFJOB == 37
# SR_ = REFJOB == 38
# Y_  = REFJOB == 39
# ZR_ = REFJOB == 40
# NB_ = REFJOB == 41
# MO_ = REFJOB == 42
# TC_ = REFJOB == 43
# RU_ = REFJOB == 44
# RH_ = REFJOB == 45
# PD_ = REFJOB == 46
# AG_ = REFJOB == 47
# SN_ = REFJOB == 50
# CS_ = REFJOB == 55
# BA_ = REFJOB == 56
# W_  = REFJOB == 74
# RE_ = REFJOB == 75
# OS_ = REFJOB == 76
# IR_ = REFJOB == 77
# PT_ = REFJOB == 78
# AU_ = REFJOB == 79
#
#
# ###################
# # cell_arg = As(concat('[[',AX,',',AY,',',AZ,'],['
# #                          ,BX,',',BY,',',BZ,'],['
# #                          ,CX,',',CY,',',CZ,']]'),'cell')
# #
# # atoms_args = [As(concat('[',GROUPCONCAT(NUMBER),']'),'numbers')             # numbers
# #               ,As(concat('[[',GROUPCONCAT(X),'],['
# #                           ,GROUPCONCAT(Y),'],['
# #                           ,GROUPCONCAT(Z),']]'),'posT')                     # positions (transpose)
# #               ,cell_arg # cell
# #               ,As(concat('[',GROUPCONCAT(MAGMOM),']'),'magmoms')            # magmoms
# #               ,As(concat('[',GROUPCONCAT(CONSTRAINED),']'),'constrained')]  # constrained
# #
#
# def RAND_(x : float) -> typ.Any:
#     """Random fraction of data, chosen by Bool(id + <number> % <number>)"""
#     x = round(x,2)
#     r = random.randint(0,100000)
#     assert 0 <= x <= 1
#
#     if   x==1:         return '1'
#     elif x==0:         return 'not 1'
#     elif x < 0.5:   LOW = True
#     else:
#      x      = 1 - x
#      LOW = False
#
#     harmonic = map(lambda y: 1./y,range(1,105))
#
#     error = float('inf')
#     for i,h in enumerate(harmonic):
#         diff = x-h
#         if abs(diff)>error:
#             if LOW: return Not(Mod(JOB+r,i))
#             else:   return Mod(JOB+r,i)
#         else: error = abs(diff)
#     raise ValueError('Pick a more reasonable value for RAND than'+str(x))
#
#
# ##Misc Joins#
# atoms_tables = joiner(struct,{atoms:atom__atoms,cell:atoms__cell})



################
#OLD STUFF NEED TO REWRITE UNCOMMENT AND FIX AS NEEDED
#################
# atom2       = Table('atom')
# atoms2      = Table('atoms')
# cell2       = Table('cell')
# calc2       = Table('calc')
# job2        = Table('job')
# element2    = Table('element')
# refstoich2  = Table('refstoich')
# refeng2     = Table('refeng')
#
# final_table_joins = {calc  : calc.id  == job.calc_id
#
#                     finalatoms          = Table('toms : atoms.id == job.finalatoms')
#                     ,cell  : cell.id  == atoms.cell_id}
#
# finalatom_table_joins = {calc  : calc.id  == job.calc_id
#                         ,atoms : atoms.id == job.finalatoms
#                         ,cell  : cell.id  == atoms.cell_id
#                         ,atom  : atom.atoms_id == job.finalatoms}
#
#
# final_table      = joiner(job,final_table_joins)
# final_atom_table = joiner(job,finalatom_table_joins)
#
# #Parent Child Table
# parent_job          = Table('job')
# parent_atoms        = Table('atoms')
# parent_cell         = Table('cell')
# parent_calc         = Table('calc')
#
#
# parent_child_table  = joiner(
#                             joiner(
#                                 joiner(job
#                                 ,{parent_job          : [job.parent      == parent_job.storage_directory, 'LEFT']})
#                                 ,{calc                : [calc.id         == job.calc_id,                  'INNER']
#                                 ,atoms                : [atoms.id        == job.finalatoms,               'INNER']
#                                 ,cell                 : [cell.id         == atoms.cell_id,                'INNER']
#                                 ,parent_calc          : [parent_calc.id  == parent_job.calc_id,            'LEFT']
#                                 ,parent_atoms         : [parent_atoms.id == parent_job.finalatoms,         'LEFT']}
#                                 )
#                             ,{parent_cell          : [parent_cell.id   == parent_atoms.cell_id, 'LEFT']}
#                         )
#
# def get_table_names(joined_tables : sql.Join) -> typ.List[str]:
#     left = joined_tables.left
#     right = joined_tables.right
#     if isinstance(left,sql.Table) and isinstance(right,sql.Table):
#         return [left._name, right._name]
#     elif isinstance(left,sql.Table):
#         return [left._name]+get_table_names(right)
#     else:
#         return get_table_names(left)+[right._name]
#
# td = {'atom':atom,'atoms':atoms,'cell':cell,'calc':calc,'job':job # TABLE
#      ,'refeng':refeng,'composition':composition}                                            # DICTIONARY
#
