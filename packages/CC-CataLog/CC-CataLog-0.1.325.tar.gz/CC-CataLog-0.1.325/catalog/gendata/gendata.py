# Typing Modules
import typing as typ

if typ.TYPE_CHECKING:
    #Type Checking Imports
    import sql                                  # type: ignore
    from catalog.jobs.jobs import Job

# External Modules
import warnings
warnings.filterwarnings("ignore", message="Moved to ase.neighborlist")
warnings.filterwarnings("ignore", message="matplotlib.pyplot")

import json,pickle,copy,inspect,itertools

import ase                                  # type: ignore
import ase.visualize as viz                 # type: ignore
from ase.build import bulk                  # type: ignore
import numpy as np                          # type: ignore
from copy import deepcopy                   # type: ignore

# Internal modules
import catalog.data.emt  as emt

import catalog.jobs.jobs                 as jobs
import catalog.gendata.surfFuncs         as surfFuncs
import catalog.gendata.interstitialFuncs as interstitialFuncs
import catalog.datalog.db_utils          as db
import catalog.fw.incomplete             as manage

from catalog.misc.sql_utils   import *
from catalog.misc.utilities   import launch,merge_dicts,flatten
from catalog.misc.print_parse import abbreviate_dict,read_on_sher
from catalog.misc.atoms       import (make_atoms,nonmetal_symbs,cell_to_param
                                      ,remove_atom,remove_atoms, fix_negative_unit_cells
                                      ,get_sites,traj_to_json,json_to_traj,collision,reorient_z_ase)
# from catalog.gendata.ads_site import AdsorbateSiteVector

from catalog.jobs.repeat      import RepeatChecker
from catalog.jobs.versions    import current_version

#Type Aliases
# filter_func_type    = typ.Callable[[typ.List['AdsorbateSiteVector']],typ.List['AdsorbateSiteVector']]
transform_func_type = typ.Callable[[dict],typ.List[dict]]

################################################################################
"""
Functions to create new jobs based on existing jobs in the database

varies
modify
bulk_modulus
vibs
bare
adsorb
interstitial
"""

dbp     = '/scratch/users/ksb/share/suncatdata.db' #default DataBasePath
repeats = RepeatChecker() # Initialize Repeat Checker when loading script

def calc_args(drop          : typ.List[str]             = []
             ,connectinfo   : ConnectInfo               = db.realDB
             ) -> typ.List[sql.Column]:
    """
    Returns list of SQL Column objects that can be used in a query
    """
    drop.append('calc_id') # always drop this one
    drop.append('calc_other_id') # always drop this one
    drop += ['kx','ky','kz'] # always drop this one
    calc_cols       = [getattr(tbl_calc,col) for col in
                db.Query(table=tbl_calc,connectinfo=connectinfo).col_names()
                if col not in drop]
    calc_other_cols = [getattr(tbl_calc_other,col) for col in
                db.Query(table=tbl_calc_other,connectinfo=connectinfo).col_names()
                if col not in drop]
    return calc_cols + calc_other_cols


#############
# Check_funcs
#-------------

def check_params(j : 'Job') -> bool:
    q = '\n\nDo the following params look right?\n\n%s\n\n(y/n)--> '%(abbreviate_dict(j.params))
    return 'y' in input(q).lower()

def check_atoms(j  : 'Job') -> bool:
    viz.view(j.atoms)
    q = 'Do the structure/params look right?\n%s\n(y/n)--> '%(abbreviate_dict(j.params))
    return 'y' in input(q).lower()
#################
# CREATE NEW JOBS
#################


# NON-gendata methods (jobs that must be built from scratch, not from DB)
def latticeopt(name                 : str
              ,structure            : str
              ,dftcode              : str
              ,pw                   : int
              ,xc                   : str
              ,psp                  : str
              ,walltime             : typ.Optional[float]   = None
              ,nodes                : typ.Optional[int]     = None
              ,clust_str            : typ.Optional[str]     = None # default submission if None
              ,kpts                 : typ.List[int]         = [8,8,8]
              ,econv                : float                 = 5e-4
              ,xtol                 : float                 = 0.005  # pretty relevant parameters
              ,fmax                 : float                 = 0.05
              ,mixing               : float                 = 0.1
              ,nmix                 : int                   = 10
              ,maxstep              : int                   = 250
              ,nbands               : int                   = -12
              ,sigma                : float                 = 0.1 # other parameters
              ,gga                  : str                   = 'PE'
              ,gamma                : int                   = 1
              ,ismear               : int                   = 0
              ,algo                 : str                   = 'normal'
              ,prec                 : str                   = 'normal'
              ,mixingtype           : str                   = 'plain'
              ,ibrion               : int                   = 2
              ,nelmdl               : int                   = -9
              ,lreal                : str                   = 'auto'
              ,lvhar                : int                   = 1
              ) -> None:
    """
    Perform lattice optization on a metal element.
    Optionally provide an associated list of structures if non-equilibrium
    structures are wanted.
    """
    assert structure in ['fcc','bcc','hcp','fcc-unit','bcc-unit','zincblende','zincblende-unit','cscl','rocksalt','cscl-unit','rocksalt-unit','triclinic']
    unit  = 'unit' not in structure
    cubic = 'cubic' in structure # not possible but maybe in future?

    crystalstructure = structure # Apply transformations to make ASE compatible?

    itraj = bulk(name, crystalstructure= crystalstructure, orthorhombic=unit, cubic=cubic)

    params = {'inittraj':traj_to_json(itraj),'structure':structure
            ,'dftcode':dftcode,'pw':pw,'xc':xc,'psp':psp,'kpts':kpts
            ,'econv':econv,'xtol':xtol,'fmax':fmax,'maxstep':maxstep
            ,'sigma':sigma,'jobkind':'latticeopt'}

    qe_dict   = {'nbands':nbands,'mixing':mixing,'nmix':nmix,'mixingtype':mixingtype}
    gpaw_dict = {'nbands':nbands,'mixing':mixing,'nmix':nmix}
    vasp_dict = {'gga':gga,'luse_vdw': 1 if xc == 'BEEF' else 0
                ,'zab_vdw':      -1.8867 if xc == 'BEEF' else None
                ,'gamma':gamma,'ismear':ismear,'algo':algo
                ,'lreal':lreal,'lvhar':lvhar,'prec':prec
                ,'ionic_steps':50 ,'ibrion':ibrion,'nelmdl':nelmdl}

    meta_dict = {'quantumespresso':qe_dict,'gpaw':gpaw_dict,'vasp':vasp_dict}
    input_dict = merge_dicts([params,meta_dict[dftcode]])       # type: ignore

    j = jobs.Job(input_dict)
    if not repeats.check_repeat(j):
        msg =  'New job, sure you want to submit the following? '+abbreviate_dict(input_dict)
        if 'y' in input(msg).lower():
            j.submit(repeats, walltime = walltime, clust_str = clust_str,nodes = nodes)
        else:
            print('No job submitted')
    else:
        print('This job is not new')

# Gendata-creating functions (must call .submit() on the output)
def varies(field            : str
          ,rang             : typ.List[typ.Any]
          ,constraint       : typ.List[typ.Any]     = []
          ,limit            : typ.Optional[int]     = None
          ,check_func       : typ.Callable          = check_atoms
          ) -> 'GenData':
    """
    Create multiple jobs per old job by varying 'field' over range 'rang'
    """
    if field == 'delta': default_constraint = VIB_ # What other cases is it ok to vary a parameter for a non-relax/latticeopt job
    else: default_constraint = OR(LATTICEOPT_,VCRELAX_,AND(RELAX_,MOLECULE_))

    cnst = AND(default_constraint,*constraint)

    query=db.Query([As(RAW,'inittraj')]+calc_args(drop=['kpts'])+
                   [As(STRUCTURE,'structure'),JOBNAME,As(STORDIR,'parent')
                    ,As(JOBTYPE,'jobkind'),As(KPTDEN_X/2+KPTDEN_Y/2,'kptden')]
                    ,cnst,table=tbl_relaxfinal,group=JOB
                    ,limit=limit)

    return GenData(query,check_func = check_atoms
                  ,transform=[preserve_dwrat
                            ,job_name_kwargs
                            ,vary_dict(field,rang)])

def modify(modifying_dict   : typ.Dict[typ.Any,typ.Any]
          ,constraint       : typ.List[typ.Any]         = []
          ,limit            : typ.Optional[int]         = None
          ,check_func       : typ.Callable              = check_atoms
          )->'GenData':
    """
    Create 1 new job per old job (specified by constraint) by
        modifying params with a dictionary of unary functions.
    K-Point density is preserved
    """
    default_constraint = OR(LATTICEOPT_,VCRELAX_,AND(RELAX_,MOLECULE_))
    cnst               = AND(default_constraint,*constraint)

    query=db.Query([As(RAW,'inittraj')]+calc_args(drop=['kpts'])
                    +[As(STRUCTURE,'structure'),JOBNAME,As(STORDIR,'parent')
                        ,As(JOBTYPE,'jobkind')
                        ,As(KPTDEN_X/2+KPTDEN_Y/2,'kptden')]
                    ,cnst,group=JOB,table=tbl_relaxfinal_all,limit=limit)

    return GenData(query,check_func = check_atoms
                  ,transform=[print_params()
                            ,preserve_dwrat
                            ,job_name_kwargs
                            ,update_keys(modifying_dict)])


def xc_contribs(constraints          :typ.List[typ.Any]       = []
               ,limit               :int                     = 1
               ,check_func       : typ.Callable              = check_atoms
               ) -> 'GenData':
    """Get the XC contributions"""
    default_constraint = AND(LATTICEOPT_,PW_(1500),KSB_)    # type: ignore
    cnst               = AND(default_constraint,*constraints)

    query=db.Query([As(RAW,'inittraj')]+calc_args()
                    +[As(STRUCTURE,'structure'),JOBNAME,As(STORDIR,'parent')]
                    ,cnst,group=JOB,table=tbl_relaxfinal_all
                    ,limit=limit)

    return GenData(query #,check_func = check_params
                  ,transform=[insert_keys(jobkind='xc')
                            ,update_keys({'job_name':lambda x: x+'_xc_contribs'})
                            ])


def bulk_modulus(constraints         :typ.List[typ.Any]
                ,limit              :typ.Optional[int]      = None
                ,check_func       : typ.Callable              = check_params
                ) -> 'GenData':
    """
    Calculate bulk modulus
    """
    default_constraint = LATTICEOPT_
    cnst               = AND(default_constraint,*constraints)

    query=db.Query([As(RAW,'inittraj')]+calc_args(drop=['kpts'])
                    +[As(STRUCTURE,'structure'),JOBNAME,As(STORDIR,'parent')
                    ,As(JOBTYPE,'jobkind'),As(KPTDEN_X/2+KPTDEN_Y/2,'kptden')]
                    ,cnst,group=JOB,table=tbl_relaxfinal_all,limit=limit)

    return GenData(query,check_func = check_func
                  ,transform=[insert_keys(jobkind='bulkmod',strain=0.03)
                            ,update_keys({'job_name':lambda x: x+'_bulkmod'})
                            ,job_name_kwargs])

def vibs(constraints                 :typ.List[typ.Any]
        ,limit                      :typ.Optional[int]      = None
        ,check_func       : typ.Callable              = check_atoms
        ) -> 'GenData':
    """
    Calculate vibrational modes
    """
    default_constraint = RAWENG!=None
    cnst               = AND(default_constraint,*constraints)
    query=db.Query([As(RAW,'inittraj')]+calc_args(drop=['xtol','cell_dofree','cell_factor'])
                    +[As(STRUCTURE,'structure'),JOBNAME,As(STORDIR,'parent'),FACET_CATALOG,ADSORBATES
                    ,As(JOBTYPE,'jobkind')],cnst,table=tbl_relaxfinal_all
                    ,group=JOB,limit=limit)

    return GenData(query,check_func = check_func
                  ,transform=[insert_keys(jobkind='vib',delta=0.04)
                            ,update_keys({'job_name':lambda x: x+'_vib'})
                            ,vibrate_nonmetals
                            ,job_name_kwargs])

def repeat_traj(constraints       : typ.List[typ.Any]
               ,repeat            : typ.Tuple[int,int,int]
               ,fix_cell_problems : bool = True
               ,adjust_kpts       : bool = True
               ,limit             : typ.Optional[int] = None
               ,verbose           : bool = True
               ,check_func       : typ.Callable              = check_atoms
               ) -> 'GenData':
    default_constraint     = AND(RELAXORLAT_,SURFACE_)
    cnst                   = AND(default_constraint,*constraints)

    q_args = ( [As(RAW,'inittraj')]
             + calc_args(drop=['xtol'])
             + [As(STRUCTURE,'structure'),JOBNAME,As(ADSORBATES,'adsorbates'),As(STORDIR,'parent')
               ,As(JOBTYPE,'jobkind'),As(FACET_CATALOG,'facet')])

    query=db.Query(cols=q_args,constraints=cnst,group=JOB
                    ,table=tbl_relaxfinal_all,limit=limit, verbose = True)

    return GenData(query,check_func = check_func
                  ,transform=[repeat_atoms(repeat            = repeat
                                          ,fix_cell_problems = fix_cell_problems
                                          ,adjust_kpts       = adjust_kpts)
                            ,job_name_kwargs]
                  , verbose= verbose)

def bare_all_facets(constraints : typ.List[typ.Any]
                   ,xy          : typ.Tuple[int,int]
                   ,layers      : int
                   ,symmetric   : bool
                   ,vacuum      : float
                   ,kpts        : typ.List[int]
                   ,max_index   : int = 1
                   ,constrained : typ.Optional[typ.List[int]] = None
                   ,limit       : typ.Optional[int] = None
                   ,check_func  : typ.Callable[[typ.Any],bool] = check_atoms
                   ,verbose     : bool = True
                   ) -> 'GenData':
    """Generate all facets of a bare surface with a max miller index equal to max_index"""
    default_constraint = AND(RAWENG!=None,BULK_)
    cnst               = AND(default_constraint,*constraints)

    query=db.Query([As(RAW,'inittraj')]+calc_args(drop=['xtol','kpts','kptden','dipole','cell_dofree','cell_factor'])
                    +[As(STRUCTURE,'structure'),JOBNAME,As(STORDIR,'parent')
                        ,As(JOBTYPE,'jobkind')]
                    ,cnst,group=JOB,table=tbl_relaxfinal_all,limit=limit)
    if constrained is None:
        constrained = list(range(int(layers/2+1),layers+1))

    return GenData(query,check_func = check_func
                  ,transform=[insert_keys(jobkind='relax',adsorbates='[]')
                             ,print_params()
                             ,insert_keys(kpts=kpts)
                             ,make_bare_all_facets(max_index,xy,layers,constrained,symmetric,vacuum)
                             ,job_name_kwargs
                             ,print_params()], verbose= verbose)

def bare(constraints : typ.List[typ.Any]
        ,xy          : typ.Tuple[int,int]          = (1,1)
        ,layers      : int                         = 1
        ,symmetric   : bool                        = False
        ,vacuum      : float                       = 10.
        ,kpts        : typ.List[int]               = (4,4,1)
        ,facet       : typ.Tuple[int,int,int]      = (0,0,1)
        ,constrained : typ.Optional[typ.List[int]] = None
        ,limit       : typ.Optional[int]           = None
        ,verbose     : bool                        = True
        ,check_func  : typ.Callable                = check_atoms
        ) -> 'GenData':
    """Generate a bare surface"""
    default_constraint = AND(RAWENG!=None,BULK_)
    cnst               = AND(default_constraint,*constraints)

    query=db.Query([As(RAW,'inittraj')]+calc_args(drop=['xtol','kpts','kptden','dipole','cell_dofree','cell_factor'])
                    +[As(STRUCTURE,'structure'),JOBNAME,As(STORDIR,'parent')
                        ,As(JOBTYPE,'jobkind')]
                    ,cnst,group=JOB,table=tbl_relaxfinal_all,limit=limit)
    if constrained is None:
        constrained = list(range(int(layers/2+1),layers+1))

    return GenData(query,check_func = check_func
                  ,transform=[insert_keys(jobkind='relax',adsorbates='[]',facet=json.dumps(facet))
                             ,print_params()
                             ,insert_keys(kpts=kpts)
                             ,update_keys({'job_name':bare_name(facet,xy,layers)})
                             ,make_bare_slab(facet,xy,layers,constrained,symmetric,vacuum)
                             ,job_name_kwargs
                             ,print_params()], verbose= verbose)


def adsorb(constraints          : typ.List[typ.Any] = []
          ,adsname              : str               = 'H'
          ,ads_filter_list      : list              = []
          ,slab_constraint_dict : dict              = {}
          ,ads_constraint_dict  : dict              = {}
          ,height               : float             = 2.0
          ,limit                : typ.Optional[int] = None
          ,verbose              : bool              = True
          ,check_func       : typ.Callable              = check_atoms
          ) -> 'GenData':
    """
    adsfilterlist is a list of functions [(Ads,Site,Vector)] -> [(Ads,Site,Vector)]
    """
    from catalog.misc.sql_utils import AND
    from adsorber import filter_functions as ff
    from adsorber.objects.adsorbate import get_ads

    default_constraint     = AND(RELAXORLAT_,SURFACE_)
    cnst                   = AND(default_constraint,*constraints)
    ads_list = list(map(get_ads,adsname.split())) # Adsorbate class

    q_args = ( [As(RAW,'inittraj')]
             + calc_args(drop=['xtol','cell_dofree','cell_factor'])
             + [As(STRUCTURE,'structure'),JOBNAME,As(ADSORBATES,'adsorbates'),As(STORDIR,'parent')
               ,As(JOBTYPE,'jobkind'),As(FACET_CATALOG,'facet')])

    query=db.Query(cols=q_args,constraints=cnst,group=JOB
                    ,table=tbl_relaxfinal_all,limit=limit, verbose = verbose)

    return GenData(query,check_func = check_func
                  ,transform=[constrain_slab(slab_constraint_dict)
                            ,add_adsorbates(ads_list,ads_filter_list, constraint_dict = ads_constraint_dict,height = height)
                            ,job_name_kwargs], verbose = verbose)


def vacancy(constraints : typ.List[typ.Any] = []
           ,limit       : typ.Optional[int] = None
           ,verbose     : bool              = True
           ,check_func       : typ.Callable              = check_atoms
           ) -> 'GenData':
    """
    adsfilterlist is a list of functions [(Ads,Site,Vector)] -> [(Ads,Site,Vector)]
    """
    from catalog.misc.sql_utils import AND
    default_constraint     = AND(RELAXORLAT_)
    cnst                   = AND(default_constraint,*constraints)

    q_args = ( [As(RAW,'inittraj')]
             + calc_args(drop=['xtol','cell_dofree','cell_factor'])
             + [As(STRUCTURE,'structure'),JOBNAME,As(STORDIR,'parent')
               ,As(JOBTYPE,'jobkind'),As(FACET_CATALOG,'facet')])

    query=db.Query(cols=q_args,constraints=cnst,group=JOB
                    ,table=tbl_relaxfinal_all,limit=limit)

    return GenData(query
                  ,check_func = check_func
                  ,transform=[select_vacancy_index()
                             ,job_name_kwargs]
                  , verbose = verbose)


def fbl(constraint     : typ.List[typ.Any]           = []
       ,bonded_inds    : typ.Optional[typ.List[int]] = None
       ,step_size      : typ.Optional[float]         = None
       ,energy_cut_off : typ.Optional[float]         = None
       ,fix            : typ.Optional[float]         = None
       ,limit          : typ.Optional[int]           = None
       ,check_func     : typ.Callable                = check_params
       ) -> 'GenData':

    if step_size is None: step_size = 0.1
    if energy_cut_off is None: energy_cut_off = 10.
    if fix is None: fix = 0.5

    default_constraint     = AND(RELAX_)
    cnst                   = AND(default_constraint,*constraint)
    q_args = ( [As(RAW,'inittraj')]
             + calc_args(drop=['xtol','cell_dofree','cell_factor'])
             + [As(STRUCTURE,'structure'),JOBNAME,As(STORDIR,'parent')
               ,As(JOBTYPE,'jobkind'),ADSORBATES, As(FACET_CATALOG,'facet')])

    query=db.Query(cols=q_args,constraints=cnst,group=JOB
                    ,table=tbl_relaxfinal_all,limit=limit)

    return GenData(query,check_func = check_params
                  ,transform=[insert_keys(jobkind='fbl',step_size=step_size, energy_cut_off=energy_cut_off, fix = fix)
                            ,select_bonded_inds()
                            ,job_name_kwargs])
#################################################################################

class GenData(object):
    """
    Use an existing database to generate new data by creating Jobs objects
    Its value lies in its only public method: submit
    """
    def __init__(self
                ,query      : db.Query
                ,transform  : typ.List[transform_func_type]
                ,check_func : typ.Callable[[typ.Any],bool]  = lambda x: True
                ,verbose    : bool                          = True
                ) -> None:
        """
        Args:

            constraint :: String
                - Raw SQL to be inserted in the WHERE clause.
                - Determines which subset of existing jobs are used to generate new jobs

            table :: String
                Table used for SQL query
                If one wants to use a job's initial atoms, one join job on initatoms

            limit :: Int
                Restrict number of jobs that meet the query

            transform :: [Dict -> Either Dict [Dict]]
                - Apply transformations to the full row returned from the SQL query
                - Optionally 'branch' by returning a list of dictionaries
                - effects of transformations compose to finally produce Job input

            atoms_to_dicts :: ase.Atoms -> [Dict]
            calc_to_dicts  :: Dict      -> [Dict]
                - These functions are used to modify the previous job
                - If a list greater than length 1 is returned, multiple jobs will be created
                - All combinations of the [Atoms] and [calcDict] will be created
                - To remove a calc parameter (e.g. creating surface slab from latticeopt job)
                    it is enough to do: def c_2_c(xtol,**kwargs): return [kwargs]
            name_to_name :: String -> String
                apply some constant transformation to the previous job_name
            params_to_params :: Dict -> Either Dict [Dict]
                Before the Job is created, apply a final transformation to params
                This is a less restrained function. More powerful, less shareable.

            check_func :: Job -> Bool
                Ask for user input or do some other check to approve of a Job

            kptden :: Bool
                Replace kpt with kptden (average of kptden_x and kptden_y)

            emttol :: Float
                Used for a filter [Dict]->[Dict] that tries to remove redundant
                jobs by removing those with near-identical EMT energy.
                Use a negative number to turn off the filter
        """
        self.query      = query
        self.verbose    = verbose
        self.transform  = transform
        self.check_func = check_func

    def submit(self
              ,walltime           : typ.Optional[float]        = None
              ,clust_str          : typ.Optional[str]          = None
              ,nodes              : typ.Optional[int]          = None
              ) -> typ.Any:
        query_results  = self.query.query_dict()
        n,sub          = len(query_results),None
        if n == 0:
             print('No jobs meet your query: ')
             print(self.query.last_command)
        else:
            question = 'Do you want to modify %d jobs? \n(y/n)--> '%len(query_results)
            if not self.verbose or self._ask(question):
                made_jobs    = self._make_jobs(query_results)
                checked_jobs = list(filter(self.check_func,made_jobs))
                n            = len(checked_jobs)
                question     = 'Do you want to launch %d new jobs?\n(y/n)---> '%n
                if (not self.verbose) or (n < 50 and self._ask(question)) or (n >=50 and self._hard_ask(n)):
                    sub = {}
                    for j in checked_jobs:
                        print('not using graphs for equality checking')
                        sub.update(j.submit(repeats,walltime=walltime,clust_str=clust_str,nodes = nodes)) # USE GRAPH FOR EQUALITY TESTING
                    print('Launch with: catalog.misc.utilities.launch()')
                    return sub # return output of add_wf for last launch
                else: print('No jobs submitted')
            else: print('No jobs submitted')

    def _make_jobs(self
                  ,query_results        : typ.List[dict]
                  ) -> typ.List['Job']:
        ps = query_results #initialize with length 1 list of dictionaries
        for t in self.transform: ps = self._flatten(list(map(t,ps)))
        return [j for j in map(current_version.process_dict,ps) if not repeats.check_repeat(j)]

    def _ask(self, s : str) -> bool:      return 'y' in input(s).lower()
    def _hard_ask(self, n : int) -> bool: return input('Type {0} to launch {0} new jobs: '.format(n)) == str(n)
    def _flatten(self, lst : typ.List[typ.List[dict]])->typ.List[dict]:
        """
        Flatten a list of list of dictionaries. If there are non-list elements, treat them like singleton lists
        """
        output  = []
        for l in lst:
            if isinstance(l,list) and len(l)>0 and isinstance(l[0],dict): output.extend(l)
            elif len(l)==0: continue
            elif isinstance(l,dict): output.append(l)
            else: raise ValueError('transform functions should return Dict or [Dict]')
        return output

#################################################################################
# TRANSFORM FUNCS
#################################################################################

###################
# General utilities
#------------------
def identity(x:typ.Any) -> typ.Any : return x

def print_params(message : str ='printing params') -> transform_func_type:
    def f(d : dict) -> typ.List[dict]:
        print('\n\n%s\n\n%s\n\n'%(message,abbreviate_dict(d)))
        return [d]
    return f

def update_keys(modifying_dict : dict) -> transform_func_type:
    """update dictionary with dictionary of unary functions"""
    def f(d : dict) -> typ.List[dict]:
        return [{k:modifying_dict.get(k,identity)(v) for k,v in d.items()}]
    return f

def insert_keys(**kwargs : typ.Any) -> transform_func_type:
    """Insert/overwrite keys based on keyword arguments"""
    def f(d : dict) -> typ.List[dict]:
        return [merge_dicts([d,kwargs])]
    return f

def vary_dict(k     : str
             ,vs    : typ.List[typ.Any]
             ) -> transform_func_type:
    """create transform function to vary a parameter k over range vs"""
    if not isinstance(vs,list): vs=[vs]
    def f(d : dict) -> typ.List[dict]:
        ds  = []
        for v in vs:
            d[k]=v
            ds.append(d.copy())
        return ds
    return f


#####################
# Basic substitutions
#-------------------
def assign_parent(d : dict) -> typ.List[dict]:
    d['parent']=d.pop('storage_directory')
    return [d]

def job_name_kwargs(d : dict) -> typ.List[dict]:
    d['kwargs']=json.dumps({'job_name':d['job_name']})
    return [d]

def preserve_dwrat(d : dict) -> typ.List[dict]:
    if d.get('dw') is not None: d['dwrat']=d.pop('dw')/d['pw']
    return [d]

def preserve_kptden(d : dict) -> typ.List[dict]:
    d['kptden'] = np.mean([d.pop('kptden_x'),d.pop('kptden_y')])
    del d['kpts']
    return [d]


##################
# Create new trajs
#-----------------


def make_bare_slab(facet            : typ.Tuple[int,int,int]
                  ,xy               : typ.Tuple[int, int]
                  ,layers           : int
                  ,constrained      : typ.List[int]
                  ,symmetric        : bool
                  ,vacuum           : float
                  ) -> transform_func_type:
    def make(d : dict) -> typ.List[dict]:
        # AD HOC WARNING
        fudge_factor = 0.5 if d['structure'] in ['hcp','hexagonal'] else 1
        # AD HOC WARNING

        bulk = json_to_traj(d.pop('inittraj'))
        surface_dict = surfFuncs.bulk2surf(bulk,facet,xy,int(layers*fudge_factor),constrained,symmetric,vacuum)
        base_job_name = d['job_name']
        output_params = []
        for side,surf_ase_objs in surface_dict.items():
            for i, surf in enumerate(surf_ase_objs):
                d_curr = deepcopy(d)
                d_curr['inittraj'] = traj_to_json(surf)
                d_curr['job_name'] = base_job_name+'_{}'.format(surf.side)
                if len(surf_ase_objs)>1:
                    d_curr['job_name'] = d_curr['job_name']+'_{}'.format(i)
                output_params.append(d_curr)
        return output_params
    return make

def make_bare_all_facets(max_index        : int
                   ,xy               : typ.Tuple[int, int]
                   ,layers           : int
                   ,constrained      : typ.List[int]
                   ,symmetric        : bool
                   ,vacuum           : float
                   ) -> transform_func_type:
    def make(d : dict) -> typ.List[dict]:
        # AD HOC WARNING
        fudge_factor = 0.5 if d['structure'] in ['hcp','hexagonal'] else 1
        # AD HOC WARNING

        bulk = json_to_traj(d.pop('inittraj'))
        facets = surfFuncs.get_unique_facets(bulk,max_index)
        output_params = []
        for facet in facets:
            surface_dict = surfFuncs.bulk2surf(bulk,facet,xy,int(layers*fudge_factor),constrained,symmetric,vacuum)
            base_job_name = bare_name(facet,xy,layers)(d['job_name'])
            for side,surf_ase_objs in surface_dict.items():
                for i, surf in enumerate(surf_ase_objs):
                    d_curr              = deepcopy(d)
                    d_curr['facet']     = json.dumps(facet)
                    d_curr['inittraj']  = traj_to_json(surf)
                    d_curr['job_name']  = base_job_name+'_{}'.format(surf.side)
                    if len(surf_ase_objs)>1:
                        d_curr['job_name'] = d_curr['job_name']+'_{}'.format(i)
                    output_params.append(d_curr)
        return output_params
    return make


################################################################
################################################################
################################################################
################################################################
################################################################
################################################################

####################
# Modify input trajs
#-------------------
def repeat_atoms(repeat            : typ.Tuple[int,int,int]
                ,fix_cell_problems : bool = False
                ,adjust_kpts       : bool = True
                ) -> transform_func_type:

    """ Helpful doc string"""
    def f(p : dict) -> typ.List[dict]:

        surface       = json_to_traj(p['inittraj'])
        if fix_cell_problems:
            surface       = fix_negative_unit_cells(surface)
            facet         = json.loads(p.get('facet'))
            surface       = reorient_z_ase(surface,facet)
        surface       *= repeat
        p['inittraj'] = traj_to_json(surface)

        #Adjust kpts if user specifies it
        if adjust_kpts:
            kpts          = json.loads(p['kpts'])
            kpts          = [int(k/rep) for rep,k in zip(repeat,kpts)]
            p['kpts']     = json.dumps(kpts)
        return [p]
    return f

def add_adsorbates(ads_list             : list
                  ,list_of_filter_funcs : typ.List[typ.Any] = []
                  ,constraint_dict      : dict              = {}
                  ,emttol               : float             = 0.001
                  ,site_type            : str               = 'all'
                  ,symm_reduce          : float             = 0.0
                  ,height               : float             = 2.0
                  ) -> transform_func_type:
    """ Helpful doc string"""
    from adsorber import filter_functions as ff
    from adsorber.objects.site import Site
    from adsorber.objects.asv import AdsorbateSiteVector

    if not isinstance(ads_list, list): ads = [ads_list]
    default_filters       = [ff.manual_filter(),ff.emt_filter(emttol=emttol)]
    list_of_filter_funcs += default_filters
    def f(p : dict) -> typ.List[dict]:
        import itertools
        new_params          = []
        surface             = json_to_traj(p['inittraj'])
        # surface             = fix_negative_unit_cells(surface)
        facet               = json.loads(p['facet'])
        # surface             = reorient_z_ase(surface,facet)


        #Remove the existing adsorbates to accurately find remaining adsorbate sites
        adsorbates          = json.loads(p['adsorbates']) if not p.get('adsorbates') is None else []
        ads_inds            = flatten(adsorbates)
        current_ads         = [surface[ind] for ind in ads_inds]
        surface_without_ads = remove_atoms(surface.copy(),ads_inds)

        #Get sites from pymatgen AdsorbateSiteFinder
        site_locs           = get_sites(surface_without_ads,facet, site_type = site_type, symm_reduce = symm_reduce, height = height)
        #remove any site within 2 covalent radii or 2 Angstroms of existing adsorbates
        site_locs           = filter(lambda pos: not any([collision(pos,atom,surface.cell,[1,1,1],dis_ind = 'xy') for atom in current_ads]),site_locs)
        sites               = map(lambda s: Site(surface_without_ads.copy(),s,facet),site_locs)
        #Create the AdsorbateSiteVector objects
        ads_site_pairs = itertools.product(ads_list,sites)
        asv_list = flatten([[AdsorbateSiteVector(a,s,v,constraint_dict = constraint_dict,additional_ads = current_ads) for v in s.vectors()] for a,s in ads_site_pairs])

        #Apply the filter functions to the sites
        print('Job Name: {0}'.format(p['job_name']))
        print('Applying Filter Functions to Adsorbate Structures:')
        for filter_func in list_of_filter_funcs:
            asv_list = filter_func(asv_list) # APPLY FILTERS

        #Get the modified param dicts from each of the remaining ASV objects
        for asv in asv_list:
            new_params.append(asv.get_modified_param_dict(p))
        return new_params
    return f

def constrain_slab(slab_constraint_dict : dict
                  ) -> transform_func_type:
    """
    apply a constraint to the inittraj in the params dictionary
    slab_constraint_dict :: dict
    the dictionary needs 3 fields
        'type'      :: ASE Constraint Function (i.e. ase.constraints.FixAtoms)
        'mask'      :: a function that takes in an Atom object and returns a boolean
        'inputs'    :: a dictionary with the inputs to the specific constraint (ie. {'direction': [0,0,1]} for FixedLine)
    """

    def get_atom_constraint(constraint_dict : dict
                           ,atom            : ase.Atom
                           ) -> typ.List[typ.Any]:
        if constraint_dict == {}:
            return []
        if constraint_dict['mask'](atom):
            if constraint_dict['type'].__name__ in ['FixedLine','FixedPlane']:
                return [constraint_dict['type'](a = atom.index, **constraint_dict['input'])]
            elif constraint_dict['type'].__name__ in ['FixAtoms']:
                return [constraint_dict['type'](indices = [atom.index])]
        return []

    def merge_FixAtoms_constraint(atoms : ase.Atoms) -> ase.Atoms:
        import ase.constraints as acon  # type: ignore
        other_constraints   = []        # type: list
        fixed_atom_indices  = []        # type: list
        for constraint in atoms.constraints:
            if 'FixAtoms' in constraint.__repr__():
                fixed_atom_indices = np.append(fixed_atom_indices,constraint.get_indices())
            else:
                other_constraints.append(constraint)
        unique_fixed_atom_indices = list(set(fixed_atom_indices))
        atoms.set_constraint([acon.FixAtoms(indices = unique_fixed_atom_indices)]+other_constraints)
        return atoms

    def f(p : dict) -> typ.List[dict]:
        #Check to see if any constraints need to be applied
        if slab_constraint_dict == None:
            return [p]
        bare      = json_to_traj(p['inittraj'])
        num_atoms = len(bare)
        con_bare  = bare.copy()
        #Constrain each atom if it matches the mask in slab_constraint_dict
        for atom in con_bare:
            con_bare.set_constraint(con_bare.constraints+get_atom_constraint(slab_constraint_dict, atom))
        #Merge the FixAtoms constraints together
        con_bare          = merge_FixAtoms_constraint(con_bare)
        p_new             = p.copy()
        p_new['inittraj'] = traj_to_json(con_bare)
        return [p_new]

    return f

def select_bonded_inds() -> transform_func_type:
    from ase.visualize import view
    import time
    def f(p : dict) -> typ.List[dict]:
        atoms_obj            = json_to_traj(p['inittraj'])
        view(atoms_obj)
        time.sleep(3)
        p_new                = p.copy()
        bonded_inds          = ask_for_inds(atoms_obj,'fbl',p)
        p_new['bonded_inds'] = json.dumps(bonded_inds)
        p_new['job_name']    = p['job_name'] + '_'.join(['','fbl',str(bonded_inds)])
        return [p_new]
    return f

def select_vacancy_index() -> transform_func_type:
    from ase.visualize import view
    import time
    def f(p : dict) -> typ.List[dict]:
        atoms_obj                 = json_to_traj(p['inittraj'])
        view(atoms_obj)
        time.sleep(3)
        output = []
        answer = 'y'
        while answer in 'y':
            p_new                = p.copy()
            vac_index            = ask_for_inds(atoms_obj,'vacancy',p_new)[0]
            p_new['vacancy_pos'] = json.dumps(list(atoms_obj[vac_index].position))
            p_new['inittraj']    = traj_to_json(remove_atom(atoms_obj,vac_index))

            #Modify the name of the job OLDNAME_SYMBOLvac_[X-Y-Z]
            #SYMBOL is chemical symbol of vacancy
            #X,Y,Z are the coordinates of vacancy atom
            vac_pos_str          = '['+'-'.join(map(str,list(atoms_obj[vac_index].position)))+']'
            symbol_str           = atoms_obj[vac_index].symbol+'vac'
            job_name_suffix      = '_'.join([symbol_str,vac_pos_str])
            p_new['job_name']    = '_'.join([p_new['job_name'],job_name_suffix])
            output.append(p_new)
            answer = input('Create another vacancy job (y/n)? ')
            while answer.lower() not in ['y','n']:
                answer = input('Create another vacancy job (y/n)? ')
        return output
    return f

def ask_for_inds(atoms_obj  : ase.Atoms
                ,job_type   : str
                ,p          : dict) -> typ.List[int]:
    assert job_type in ['fbl','vacancy']

    job_type_dict    = {'fbl'    :'Please use the atoms object shown to select the bonded indices'
                       ,'vacancy':'Please use the atoms object shown to select atom to delete'}

    number_to_select = {'fbl'    : 2
                       ,'vacancy': 1}

    question_dict    = {'fbl'    :'Please type the index of the {} bonded index: '
                       ,'vacancy':'Please type the index of the atom you want to delete: '}

    index_str = ['first','second','third','fourth']
    print('##############################################################')
    print('Job Name: {0}'.format(p['job_name']))
    print(job_type_dict[job_type])
    selected_inds = []
    for index in range(number_to_select[job_type]):
        answer        = -1
        while answer not in range(len(atoms_obj)):
            answer_str = input(question_dict[job_type].format(index_str[index]))
            try:
                answer = int(answer_str)
            except ValueError:
                answer = -1
                print('Please input an index in the atoms object')
        print('{0} selected as {1} index'.format(answer, index_str[index]))
        selected_inds.append(answer)
    print('{0} are the selected indices'.format(selected_inds))
    print('##############################################################')
    return selected_inds


################################################################
################################################################
################################################################



#######
# Other
#------
def get_vibids_if_needed(d : dict) -> typ.List[dict]:
    """Needs to be used before include_keys and rename_keys"""
    if d['job_type']!='vib':
        return [d]
    else:
        res = read_on_sher(d['storage_directory']+'/result.json')
        d['vibids']= json.loads(res)['vibids']
        return [d]

def vibrate_nonmetals(d : dict) -> typ.List[dict]:
    a = json_to_traj(d['inittraj'])
    nonmetal_inds = [i for i,x in enumerate(a.get_chemical_symbols()) if x in nonmetal_symbs]
    d['vibids']=json.dumps(nonmetal_inds)
    return [d]






##########################################
# Dictionaries for 'update_keys'
#---------------------------------------
def bare_name(facet     : typ.Tuple[int,int,int]
             ,xy        : typ.Tuple[int,int]
             ,layers    : int
             ) -> typ.Callable[[typ.Any],typ.Any]:
    s_f,s_xyz = map(str,facet),map(str,list(xy)+[layers])
    return lambda n: '_'.join([n,'-'.join(s_f),'x'.join(s_xyz)])

def replicate(x : int
             ,y : int
             ,z : int) -> typ.Callable[[typ.Any],typ.Any]:
    return lambda itp: pickle.dumps(pickle.loads(itp).repeat([x,y,z]))

#############################
# Interstital Method Archive
#############################

# def make_traj(d : dict) -> typ.List[dict]:
#     n,p_t,c,m,cs = list(map(d.pop,['numbers','posT','cell','magmoms','constrained']))
#     d['inittraj']= traj_to_json(make_atoms(n,p_t,c,m,cs))
#     return [d]


# def interstitial(constraint         : typ.List[typ.Any]     = []
#                 ,interstitial       : str                   = 'H'
#                 ,num                : int                   = 2
#                 ,limit              : typ.Optional[int]     = None
#                 ,emttol             : float                 =0.2
#                 ) -> GenData:
#     """
#     Specify an interstitial and the number (up to which) you want to add them to the cell
#     Filter duplicates via EMT-calculated energy (stipulate a tolerance)
#     Assume final structure is triclinic
#     """
#
#     default_constraint  = AND(LATTICEOPT_,QE_)
#     cnst               = AND(default_constraint,*constraint)
#     query=db.Query(make_traj+calc_args(drop=['xtol','kpts'])+[NICKNAME_CATALOG,JOBNAME
#                     ,As(STORDIR,'parent'),As(JOBTYPE,'jobkind')
#                     ,As(KPTDEN_X/2+KPTDEN_Y/2,'kptden')]
#                     ,cnst,group=JOB,table=tbl_relaxfinal_all,limit=limit)
#
#     return GenData(query,check_func = check_atoms
#                     ,transform=[insert_keys(jobkind='vcrelax',structure='triclinic')
#                                 ,make_traj
#                                 ,print_params()
#                                 ,interstitial_branch(interstitial,num)])
#
# def emt_filter(list_of_dictionaries : typ.List[dict]
#               ,tol                  : float             = 0.01
#               ) -> None:
#     """
#     Return *this* instead of a list_of_dictionaries at the end of
#     a transform function to filter out those with similar 'inittraj_pckl'
#     """
#     def extract(dic : dict) -> typ.Tuple[typ.Any,dict]:
#         atoms = pickle.loads(dic['inittraj_pckl'])
#         atoms.set_calculator(emt.EMT())
#         return (atoms.get_potential_energy(),dic)
#
# def interstitial_branch(inter           : str
#                        ,num             : int
#                        ,emttol          : float     = 0.2
#                        ) -> transform_func_type:
#     """
#     Given an interstitial (and how many), generate all structures
#     up to the number of desired interstitials
#     """
#     def f(p : dict) -> dict:
#         inittraj = pickle.loads(p['inittraj_pckl'])
#         name     = p['job_name']
#         spnpl    = any([x>0 for x in inittraj.get_initial_magnetic_moments()])
#         trajs = [[(inittraj,'')]] # initial state
#
#         for i in range(num):
#             lastround = trajs[-1]                # for all structures with n - 1 interstitials (note: initially there is only one, with 0 interstitials)
#             trajs.append([])                     # initialize container for all new structures with n interstitials
#             for inputtraj,strname in lastround:
#                 for newtraj,newname in interstitialFuncs.getInterstitials(inputtraj,inter,spnpl):
#                     trajs[-1].append((newtraj,strname+newname)) # add all new trajs found for all previous structures (append suffix to name)
#
#         def modParams(par : dict
#                      ,trj : ase.Atoms
#                      ,nam : str
#                      ) -> dict:                        # For a given new traj and name, create input parameters
#             p = copy.deepcopy(par)                     # All parameters common to all of these jobs
#             p['job_name']       += nam                 # Unique job name
#             p['inittraj_pckl']  = pickle.dumps(trj)    # Initial structure
#             return p
#
#         onelevel = [modParams(p,item[0],item[1]) for sublist in trajs[1:] for item in sublist] #collapse list of lists to a single list of input parameters
#
#         return emt_filter(onelevel)
#     return f






# def multiplyJSONlist(multiplier : float
#                     ) -> typ.Callable[[typ.Any],typ.Any]:
#     return {'kpts': lambda x: json.dumps(map(lambda y: multiplier*y,json.loads(x)))}
#

# Archived
# def multiplyMagmoms(multiplier : float):
#     def modTrajPckl(trajpckl : typ.Any) -> typ.Any:
#         atoms = pickle.loads(trajpckl)
#         atoms.set_initial_magnetic_moments(multiplier* atoms.get_initial_magnetic_moments())
#         return pickle.dumps(atoms)
#     return {'inittraj_pckl':modTrajPckl}

# def multiplyVacuum(val):
#     def modTrajPckl(trajpckl):
#         atoms = pickle.loads(trajpckl)
#         cellparams = cell_to_param(atoms.get_cell())
#         cellparams[2]*=val
#         atoms.set_cell(cellparams)
#         return pickle.dumps(atoms)
#     return {'inittraj_pckl':modTrajPckl}
#testing sync

# gpaw2QE = {'dftcode':lambda x: 'quantumespresso'
#             ,'psp':  lambda x: 'gbrv15pbe'
#             ,'xc':   lambda x: 'BEEF'
#             ,'dwrat':lambda x: 10}
#
# qe2VASP  = {'dftcode':lambda x: 'vasp'
#             ,'psp':  lambda x: '{}'
#             ,'xc':   lambda x: 'PBE'
#             } #ALL OTHER VASP PARAMTERS AT DEFAULT VALUES?


################################################################################
################################################################################

#
# def testNeb():
#     """
#     Does not fit into GenData paradigm, maybe use a superclass
#     """
#     from ase.io import read
#     params = {'inittraj_pckl': pickle.dumps(read('/scratch/users/ksb/test/initial.traj'))
#             ,'finaltraj_pckl': pickle.dumps(read('/scratch/users/ksb/test/final.traj'))
#             ,'jobkind':'neb','k': 0.3,'images':5,'structure':'triclinic'
#             ,'kwargs':json.dumps({'job_name':'vibTest'})
#             ,'parent': '/scratch/.../'
#             ,'parent2':'/scratch/...'
#             ,'dftcode':'quantumespresso' ,'xc':'PBE' ,'pw':500,'psp':'gbrv15pbe'
#             ,'kpts':json.dumps([6,6,6])
#             ,'fmax':0.05,'mixing':0.05,'nmix':10,'sigma':0.15,'nbands':-12,'dw':4000,'maxstep':400,'econv':0.0005,'mixingtype':'plain'}
#     jobs.Job(params).submit(repeats,walltime=1,nodes=5)
#     launch()

################################################################################
################################################################################
