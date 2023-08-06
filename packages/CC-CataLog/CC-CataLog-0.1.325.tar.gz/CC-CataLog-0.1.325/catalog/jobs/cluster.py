#Typing imports
import typing as typ
if typ.TYPE_CHECKING:
    from catalog.jobs.jobs import Job

#External imports
import subprocess,os
#--fireworks imports
from fireworks.core.fworker import FWorker                                     # type: ignore
from fireworks.user_objects.queue_adapters.common_adapter import CommonAdapter # type: ignore

#Internal Imports
from catalog.catalog_config import USER, SUNCAT_USERNAME,SHERLOCK2_USERNAME

"""
The Cluster object and its only instances are declared

NEED TO ADD:
    - SHERLOCK2
    - CORI
    - EDISON
"""
################################################################################

class Cluster(object):
    """
    Helpful docstring
    """
    def __init__(self
                ,name      : str
                ,fworker   : str
                ,hostname  : str
                ,qfunc     : typ.Callable[[int,int,int]
                                         ,typ.Dict[str,typ.Any]]
                ,qtype     : str
                ) -> None:
        self.name       = name
        self.fworker    = FWorker(fworker,query = {})
        self.qfunc      = qfunc
        self.qadapter   = CommonAdapter(qtype)
        self.hostname   = hostname

    def get_launchdir(self) -> str:
        catalog_loc_on_cluster = subprocess.check_output(['ssh', '-XY','{}@{}'.format(USER,self.hostname),'echo',"$CATALOG_LOC"]).decode().strip('\n')
        launch_dir             = os.path.join(catalog_loc_on_cluster,'fireworks','jobs')
        return launch_dir

    def __repr__(self)->str: return self.name


def printTime(floatHours : float) -> str:
    """
    docstring
    """
    intHours = int(floatHours)
    return "%02d:%02d" % (intHours,(floatHours-intHours)*60)

###########################################################################

def sherlock2Q(timeInHours  : int = 1
              ,nodes        : int = 1
              ,cores        : int = 16
              ) -> typ.Dict[str,typ.Any]:


    return {'_fw_name'       : 'CommonAdapter'
           ,'_fw_q_type'     : 'SLURM'
           ,'rocket_launch': 'rlaunch -l $CATALOG_LOC/fireworks/FW_CONFIG_DIR/my_launchpad.yaml -w $CATALOG_LOC/fireworks/FW_CONFIG_DIR/my_fworker.yaml singleshot'
           ,'nodes'          : nodes
           ,'ntasks_per_core': 1
           ,'mem'            : 64000
           ,'walltime'       : printTime(timeInHours)+':00'
           ,'queue'          : 'iric'
           ,'pre_rocket'     : 'source $CATALOG_LOC/.env/bin/activate'
           }

def sherlock2QGPAW(timeInHours : int = 1
                  ,nodes       : int = 1
                  ,cores       : int = 20
                  ) -> typ.Dict[str,typ.Any]:
    if cores is not None:
        assert nodes==1 and cores < 17
    else:
        cores = 16
    return {'_fw_name':         'CommonAdapter'
            ,'_fw_q_type':      'SLURM'
            ,'rocket_launch':   'rlaunch -l $CATALOG_LOC/fireworks/FW_CONFIG_DIR/my_launchpad.yaml -w $CATALOG_LOC/fireworks/FW_CONFIG_DIR/my_fworker.yaml singleshot'
            ,'nodes':           nodes
            ,'ntasks_per_core': 1
            ,'walltime':        printTime(timeInHours)+':00'
            ,'queue':           'iric'
            ,'pre_rocket':      'export PATH=$PATH:/scratch/users/{0}/fireworks/fireworks_env/bin/;source /scratch/PI/suncat/sw/env.bash;export OMP_NUM_THREADS=1;export PYTHONPATH=/scratch/users/{0}/gpaw/gpaw_sg15/lib/python2.7/site-packages:$PYTHONPATH;export PATH=/scratch/users/{0}/gpaw/gpaw_sg15/bin:$PATH;export GPAW_SETUP_PATH=/scratch/users/{0}/gpaw/gpaw_sg15/norm_conserving_setups'.format(USER)
            }

###########################################################################
def suncatQ(timeInHours : int               = 1
           ,nodes       : int               = 1
           ,cores       : typ.Optional[int] = None
           ) -> typ.Dict[str,typ.Any]:

    if cores is not None:
        assert nodes==1 and cores < 9
        ntasks = cores
    else:
        ntasks = 8*nodes

    return {'_fw_name':        'CommonAdapter'
            ,'_fw_q_type':     'LoadSharingFacility'
            ,'rocket_launch': 'rlaunch -l $CATALOG_LOC/fireworks/FW_CONFIG_DIR/my_launchpad.yaml -w $CATALOG_LOC/fireworks/FW_CONFIG_DIR/my_fworker.yaml singleshot'
            ,'ntasks':         ntasks
            ,'walltime':       printTime(timeInHours)
            ,'queue':          'suncat'
            ,'pre_rocket':     'source $CATALOG_LOC/.env/bin/activate'
            }
###########################################################################
def suncat2Q(timeInHours : int
            ,nodes       : int
            ,cores       : typ.Optional[int] = None
            ) -> typ.Dict[str,typ.Any]:

    if cores is not None:
        assert nodes==1 and cores < 13
        ntasks = cores
    else:
        ntasks = 12*nodes

    return {'_fw_name':       'CommonAdapter'
            ,'_fw_q_type':    'LoadSharingFacility'
            ,'rocket_launch': 'rlaunch -l $CATALOG_LOC/fireworks/FW_CONFIG_DIR/my_launchpad.yaml -w $CATALOG_LOC/fireworks/FW_CONFIG_DIR/my_fworker.yaml singleshot'
            ,'ntasks':        ntasks
            ,'walltime':      printTime(timeInHours)
            ,'queue':         'suncat2'
            ,'pre_rocket':    'source $CATALOG_LOC/.env/bin/activate'
            }

def coriQ(timeInHours : int = 1
         ,nodes       : int = 1
         ,cores       : int = 32
         ) -> typ.Dict[str,typ.Any]:

    return {'_fw_name':         'CommonAdapter'
            ,'_fw_q_type':      'SLURM'
            ,'rocket_launch':   'cd /global/cscratch1/sd/krisb/fireworks;rlaunch singleshot'.format(USER)
            ,'nodes':           nodes
            ,'ntasks_per_node': cores
            ,'walltime':        printTime(timeInHours)+':00'
            ,'queue':           'regular'
            ,'qos':             'normal'
            ,'pre_rocket':      ''
            ,'constraint':      'haswell'
            ,'logdir':          '/global/cscratch1/sd/krisb/fireworks/logs/'}

def coriDBQ(timeInHours : int = 1
           ,nodes       : int = 1
           ,cores       : int =32
           ) -> typ.Dict[str,typ.Any]:

    return {'_fw_name':         'CommonAdapter'
            ,'_fw_q_type':      'SLURM'
            ,'rocket_launch':   'cd /global/cscratch1/sd/krisb/fireworks;rlaunch singleshot'.format(USER)
            ,'nodes':           nodes
            ,'ntasks_per_node': cores
            ,'walltime':        printTime(min(0.5,timeInHours))+':00'
            ,'queue':           'debug'
            ,'qos':             'normal'
            ,'pre_rocket':      ''
            ,'constraint':      'haswell'
            ,'logdir':          '/global/cscratch1/sd/krisb/fireworks/logs/'}

def ediDBQ(timeInHours : int = 1
          ,nodes       : int = 1
          ,cores       : int = 32
          ) -> typ.Dict[str,typ.Any]:

    return {'_fw_name':         'CommonAdapter'
            ,'_fw_q_type':      'SLURM'
            ,'rocket_launch':   'cd /scratch1/scratchdirs/krisb/fireworks;rlaunch singleshot'.format(USER)
            ,'nodes':           nodes
            ,'ntasks_per_node': cores
            ,'walltime':        printTime(min(0.5,timeInHours))+':00'
            ,'queue':           'debug'
            ,'qos':             'normal'
            ,'pre_rocket':      ''
            ,'logdir':          '/scratch1/scratchdirs/krisb/fireworks/logs/'}

###########################################################################
#Get the location of the CataLog folder on each of the clusters to find the launchdirs
#All jobs get launched in the $CATALOG_LOC/jobs folder
###########################################################################
###########################################################################


sherlock2        = Cluster('sherlock2',  'sherlock2',   'login.sherlock.stanford.edu',       sherlock2Q,'SLURM')
sherlock2gpaw    = Cluster('sherlock2',  'sherlock2',   'login.sherlock.stanford.edu',       sherlock2QGPAW,'SLURM')


suncat          = Cluster('suncat',     'suncat',      'suncatls1.slac.stanford.edu', suncatQ, 'LoadSharingFacility')
suncat2         = Cluster('suncat2',    'suncat',      'suncatls1.slac.stanford.edu', suncat2Q,'LoadSharingFacility')

# cori            = Cluster('cori',       'cori',        '/global/cscratch1/sd/krisb/fireworks/jobs/',            coriQ,'SLURM')
# cori_debug      = Cluster('cori-debug', 'cori',        '/global/cscratch1/sd/krisb/fireworks/jobs/',            coriDBQ,'SLURM')
# edi_debug       = Cluster('edi-debug',  'edison',      '/scratch1/scratchdirs/krisb/fireworks/jobs/',           ediDBQ,'SLURM')

cluster_dict = {x.name:x for x in [sherlock2,suncat, suncat2]}

def str2Cluster(job : typ.Any
               ,s : str
               ,n : int
               ) -> typ.List[Cluster]:
    assignDict = {'sherlock2': {'gpaw':sherlock2gpaw
                               ,'quantumespresso':sherlock2}
                    ,'suncat': {'quantumespresso':suncat}
                    ,'suncat2': {'quantumespresso':suncat2}
                 }
                 # ,'cori':
                 #    {'vasp':cori_debug}#cori
                 # ,'edison':
                 #    {'vasp':edi_debug}
                 # }

    return [assignDict[s.lower()][job.params['dftcode']]]*n

###################
#Archived Scripts
###################
# ###########################################################################
#
# def sherlockQ(timeInHours : int = 1
#              ,nodes       : int = 1
#              ,cores       : int = 16
#              ) -> typ.Dict[str,typ.Any]:
#     if cores is not None:
#         assert nodes==1 and cores < 17
#     else:
#         cores = 16
#     return {'_fw_name':         'CommonAdapter'
#             ,'_fw_q_type':      'SLURM'
#             ,'rocket_launch':   'cd /scratch/users/{0}/fireworks;rlaunch singleshot'.format(user)
#             ,'nodes':           nodes
#             ,'ntasks_per_core': 1
#             ,'mem'            : 64000
#             ,'walltime':        printTime(timeInHours)+':00'
#             ,'queue':           'iric,owners'
#             ,'pre_rocket':      'source {0}/.env/bin/activate'.format(CataLogPath)#'source /scratch/PI/suncat/sw/env.bash' #
#             ,'logdir':          '/scratch/users/{0}/fireworks/logs/'.format(user)}
#
# def sherlockQGPAW(timeInHours : int = 1
#                  ,nodes       : int = 1
#                  ,cores       : int = 16
#                  ) -> typ.Dict[str,typ.Any]:
#     if cores is not None:
#         assert nodes==1 and cores < 17
#     else:
#         cores = 16
#     return {'_fw_name':         'CommonAdapter'
#             ,'_fw_q_type':      'SLURM'
#             ,'rocket_launch':   'cd /scratch/users/{0}/fireworks;rlaunch singleshot'.format(user)
#             ,'nodes':           nodes
#             ,'ntasks_per_node': cores
#             ,'walltime':        printTime(timeInHours)+':00'
#             ,'queue':           'iric'
#             ,'qos':             'iric'
#             ,'pre_rocket':      ';'.join(["source /scratch/PI/suncat/sw/env.bash"
#                                         ,"source ~/scripts/rc/RCsher.sh"
#                                         ,"export OMP_NUM_THREADS=1"
#                                         ,"export PYTHONPATH=/scratch/users/{0}/gpaw/ggafirst/install/lib/python2.7/site-packages:/scratch/users/{0}/gpaw/gpaw_sg15/lib/python2.7/site-packages:$PYTHONPATH".format(user)
#                                         ,"export PATH=/scratch/users/{0}/gpaw/ggafirst/install/bin:$PATH".format(user)
#                                         ,"export GPAW_SETUP_PATH=/scratch/users/{0}/gpaw/gpaw_sg15/norm_conserving_setups".format(user)])
#             ,'logdir':             '/scratch/users/{0}/fireworks/logs/'.format(user)}
#
###########################################################################
