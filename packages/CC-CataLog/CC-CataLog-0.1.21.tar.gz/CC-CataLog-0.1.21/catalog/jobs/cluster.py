#Typing imports
import typing as typ
if typ.TYPE_CHECKING:
    from catalog.jobs.jobs import Job

#External imports

#Internal Imports
from catalog.catalog_config import USER, SHERLOCK2_USERNAME, SUNCAT_USERNAME

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
                ,launchdir : str
                ,qfunc     : typ.Callable[[int,int,int]
                                         ,typ.Dict[str,typ.Any]]
                ) -> None:
        self.name       = name
        self.fworker    = fworker
        self.qfunc      = qfunc
        self.launchdir  = launchdir

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


    return {'_fw_name'        : 'CommonAdapter'
            ,'_fw_q_type'     : 'SLURM'
            ,'rocket_launch'  : 'cd /scratch/users/{0}/fireworks;rlaunch singleshot'.format(SHERLOCK2_USERNAME)
            ,'nodes'          : nodes
            ,'ntasks_per_core': 1
            ,'mem'            : 64000
            ,'walltime'       : printTime(timeInHours)+':00'
            ,'queue'          : 'iric'
            ,'pre_rocket'     : 'source /scratch/users/{0}/CataLog/.env/bin/activate'.format(SHERLOCK2_USERNAME)
            ,'logdir'         : '/scratch/users/{0}/fireworks/logs/'.format(SHERLOCK2_USERNAME)}

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
            ,'rocket_launch':   'python /scratch/users/{0}/fireworks/fireworks_env/lib/python2.7/site-packages/fireworks/scripts/rlaunch_run.py -w /scratch/users/{0}/fireworks/my_fworker.yaml -l /scratch/users/{0}/fireworks/my_launchpad.yaml  singleshot'.format(SHERLOCK2_USERNAME)
            ,'nodes':           nodes
            ,'ntasks_per_core': 1
            ,'walltime':        printTime(timeInHours)+':00'
            ,'queue':           'iric'
            ,'pre_rocket':      'export PATH=$PATH:/scratch/users/{0}/fireworks/fireworks_env/bin/;source /scratch/PI/suncat/sw/env.bash;export OMP_NUM_THREADS=1;export PYTHONPATH=/scratch/users/{0}/gpaw/gpaw_sg15/lib/python2.7/site-packages:$PYTHONPATH;export PATH=/scratch/users/{0}/gpaw/gpaw_sg15/bin:$PATH;export GPAW_SETUP_PATH=/scratch/users/{0}/gpaw/gpaw_sg15/norm_conserving_setups'.format(SHERLOCK2_USERNAME)
            ,'logdir':          '/scratch/users/{0}/fireworks/logs/'.format(SHERLOCK2_USERNAME)}

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
            ,'rocket_launch':  'rlaunch -w /nfs/slac/g/suncatfs/{0}/fireworks/my_fworker.yaml -l /nfs/slac/g/suncatfs/{0}/fireworks/my_launchpad.yaml singleshot'.format(SUNCAT_USERNAME)
            ,'ntasks':         ntasks
            ,'walltime':       printTime(timeInHours)
            ,'queue':          'suncat'
            ,'pre_rocket':     'source /u/if/{0}/CataLog/.env/bin/activate'.format(SUNCAT_USERNAME)
            ,'logdir':         '/nfs/slac/g/suncatfs/{0}/fireworks/logs/'.format(SUNCAT_USERNAME)}
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
            ,'rocket_launch': 'python /nfs/slac/g/suncatfs/{0}/fireworks/fireworks_virtualenv/lib/python2.7/site-packages/fireworks/scripts/rlaunch_run.py -w /nfs/slac/g/suncatfs/{0}/fireworks/my_fworker.yaml -l /nfs/slac/g/suncatfs/{0}/fireworks/my_launchpad.yaml singleshot'.format(SUNCAT_USERNAME)
            ,'ntasks':        ntasks
            ,'walltime':      printTime(timeInHours)
            ,'queue':         'suncat2'
            ,'pre_rocket':    'source /nfs/slac/g/suncatfs/sw/py2.7.13/env.bash'#'unset LS_COLORS;source /nfs/slac/g/suncatfs/sw/espv20/setupenv;setenv PYTHONPATH /nfs/slac/g/suncatfs/ksb/fireworks/fireworks_virtualenv/lib/python2.7/site-packages:${PYTHONPATH};setenv PATH /afs/slac.stanford.edu/package/lsf/9.1.2/linux2.6-glibc2.3-x86_64/bin:${PATH}'
            ,'logdir':        '/nfs/slac/g/suncatfs/{0}/fireworks/logs/'.format(SUNCAT_USERNAME)}

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

###########################################################################
###########################################################################
sherlock2        = Cluster('sherlock2',  'sherlock2',   '/scratch/users/{0}/fireworks/jobs/'.format(SHERLOCK2_USERNAME),       sherlock2Q)
sherlock2gpaw    = Cluster('sherlock2',  'sherlock2',   '/scratch/users/{0}/fireworks/jobs/'.format(SUNCAT_USERNAME),       sherlock2QGPAW)

suncat          = Cluster('suncat',     'suncat',      '/nfs/slac/g/suncatfs/{0}/fireworks/jobs/'.format(SUNCAT_USERNAME), suncatQ)
suncat2         = Cluster('suncat2',    'suncat',      '/nfs/slac/g/suncatfs/{0}/fireworks/jobs/'.format(SUNCAT_USERNAME), suncat2Q)

cori            = Cluster('cori',       'cori',        '/global/cscratch1/sd/krisb/fireworks/jobs/',            coriQ)
cori_debug      = Cluster('cori-debug', 'cori',        '/global/cscratch1/sd/krisb/fireworks/jobs/',            coriDBQ)
edi_debug       = Cluster('edi-debug',  'edison',      '/scratch1/scratchdirs/krisb/fireworks/jobs/',           ediDBQ)

cluster_dict = {x.name:x for x in [sherlock2,suncat, suncat2]}

def str2Cluster(job : typ.Any
               ,s : str
               ,n : int
               ) -> typ.List[Cluster]:
    assignDict = {'sherlock2': {'gpaw':sherlock2gpaw
                               ,'quantumespresso':sherlock2}
                    ,'suncat': {'quantumespresso':suncat}
                    ,'suncat2': {'quantumespresso':suncat2}
                 ,'cori':
                    {'vasp':cori_debug}#cori
                 ,'edison':
                    {'vasp':edi_debug}
                 }

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
