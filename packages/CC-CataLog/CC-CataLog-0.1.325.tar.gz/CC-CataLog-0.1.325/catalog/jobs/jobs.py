#External Modules
import typing as typ
if typ.TYPE_CHECKING:
    from catalog.jobs.repeat       import RepeatChecker
    import catalog.jobs.repeat,catalog.jobs.scripts
import time,random,json,os,math,pickle
import datetime as d    # type: ignore
import ase              # type: ignore
import numpy as np      # type: ignore
import fireworks as fw  # type:ignore
# Internal Modules
import catalog.jobs.cluster as clust
from catalog.jobs              import scripts
from catalog.misc.sql_utils    import *
from catalog.misc.print_parse  import np_to_str
from catalog.misc.atoms        import json_to_traj
# User-required files
import catalog.catalog_config as config # type: ignore

"""
Notes: ?
"""

class Job(object):
    """
    Class for all DFT calculations.
    """


    def __init__(self
                ,params : typ.Dict[str,typ.Any]
                ) -> None:

        assert all([isinstance(k,str) for k in params])

        ##############################################
        # store some params as fields for a 'shortcut'
        #---------------------------------------------
        self.jobkind    = params['jobkind']
        self.dftcode    = params['dftcode']

        #For old jobs, to_string is a useful method for the database
        #These jobs have pickletrajs still so the below try/except will catch both
        #In future old jobs will need their pickle_trajs converted to jsons
        try:
            self.atoms      = json_to_traj(params['inittraj'])
        except KeyError:
            print('FOUND JOB WITH PICKLE TRAJ')
            self.atoms      = pickle.loads(params['inittraj_pckl'].encode('latin1'), encoding='latin1')
        self.finalatoms = params.get('finaltraj')

        self.params = params



    def __str__(self) -> str: return self.to_string('exact')

    def _str_calc(self) -> str:
        calc_keys = ['dftcode','xc','pw','kpts','fmax','psp','econv','xtol'
                    ,'strain','dw','sigma','nbands','mixing','nmix','gga'
                    ,'luse_vdw','zab_vdw','nelmdl','gamma','dipol','algo'
                    ,'ibrion','prec','ionic_steps','lreal','lvhar','diag'
                    ,'spinpol','dipole','maxstep','delta','mixingtype'
                    ,'bonded_inds','energy_cut_off','step_size','springs'
                    ,'hund']

        return '_'.join(['%s=%s'%(k,str(self.params.get(k))) for k in calc_keys])

    def to_string(self
                 ,granularity : str = 'exact'
                 ) -> str:
        """
        Represent the job with a string that can be checked for equality
        """
        s = self._str_calc()
        s += '__'+self._traj_to_str(granularity)
        # for nebs, add traj_to_str of finalatoms?
        return s

    def _traj_to_str(self
                    ,granularity : str
                    ) -> str:
        """Represent an Atoms object with a string: two levels of granularity"""

        # Convert constraints to a string
        #--------------------------------
        cnst = str(self.atoms.constraints)

        if granularity == 'exact': #FULL INFORMATION
            p = np_to_str(self.atoms.get_positions())
            c = np_to_str(self.atoms.get_cell())
            n = json.dumps(self.atoms.get_atomic_numbers().tolist())
            m = np_to_str(self.atoms.get_initial_magnetic_moments(),matrix=False)

            return '_'.join([n,p,c,cnst,m])

        elif granularity == 'graph': #LOSE PRECISE POSITION + CELL INFO, LOSE MAGMOM INFO
            # raise NotImplementedError
            return ''
            #from catalog.structure.graphatoms import GraphMaker
            #return GraphMaker(jmol=True).make_unweighted_canonical(atoms=self.atoms)

        else:
            raise NotImplementedError('Granularity not supported '+granularity)
            return ''

    def submit(self
              ,repeat_checker : "RepeatChecker"
              ,walltime       : typ.Optional[float]          = None
              ,clust_str      : typ.Optional[str]            = None
              ,nodes          : typ.Optional[int]            = None
              ,cores          : typ.Optional[int]            = None
              ) -> int:
        """
        Submit the job described by params to Fireworks
        """


        if clust_str is None:  cluster  = clust.cluster_dict[config.allocate(self,1)[0]]             # For now we assume every workflow has only one firework
        else:                  cluster  = clust.str2Cluster(self,clust_str,1)[0] # we pass in a string for Cluster
        if walltime is None:   walltime = config.guessTime(self)
        if nodes    is None:   nodes    = config.guessNodes(self)



        if not repeat_checker.check_repeat(self):
            repeat_checker.add_incomplete_job(self) # Modify RepeatChecker object
            launchpad     = fw.LaunchPad.from_file(config.LAUNCHPAD_YAML)
            wflow         = self._wflow(walltime, cluster, nodes, cores)
            time.sleep(2) # folder names = timestamp to nearest second
            return launchpad.add_wf(wflow)
        else:
            return 0

    def _standard_script(self) -> typ.Any:
        """
        Helpful docstring
        """
        if self.dftcode == 'vasp': key = 'vasp'
        else:                      key = self.jobkind
        return scripts.script_dict[key]

    def _wflow(self
              ,walltime  : int
              ,cluster   : clust.Cluster
              ,nodes     : int
              ,cores     : int
              ) -> "fw.WorkFlow":
        """
        Create a fireworks workflow
        """

        #Check if any non-default values for job submission are selected
        #If one is not specified the catalog_config functions will be used

        timestamp = '_'+d.datetime.now().strftime('%Y_%m_%d_%H_%M_%S')

        print("Submited to {0} for {1} Hours".format(cluster.name, walltime))

        fw1 = fw.Firework([self._standard_script()]
                        ,name = self.jobkind
                        ,spec = {'params':          self.params
                                ,'_fworker':        cluster.fworker.name
                                ,'_queueadapter':   cluster.qfunc(walltime,nodes,cores)
                                ,'_launch_dir':     os.path.join(cluster.get_launchdir(),self.jobkind+timestamp)})

        return fw.Workflow([fw1],name=self.jobkind)
