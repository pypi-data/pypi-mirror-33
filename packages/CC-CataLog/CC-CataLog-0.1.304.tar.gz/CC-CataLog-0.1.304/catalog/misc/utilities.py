# #Typing imports
import typing as typ

#External imports
import itertools,os,math,subprocess,time

#Internal Imports
from catalog.catalog_config import HOSTNAME

"""
General functions for manipulating python objects

General
    identity

Cluster-related
    get_cluster
    get_analysis_folder
    get_sherlock_folder
    launch
    safeMkDir

String Related
    modify_time
    sub_binds
    replacer

List-related
    partition
    chunks
    lol
    flatten
    gcd
    normalize_list

Antiquated
    change_adsorbatedict_to_indice_list
"""
################################################################################

##########
# General
#---------
identity = lambda x : x
negate   = lambda x: -x
true     = lambda x : True
user     = os.environ['USER']

##################
# Cluster related
#-----------------

def running_jobs_sherlock() -> typ.List[str]:
    return subprocess.check_output(['squeue', '-u',user,'-o','%Z']).split()[1:]

def get_cluster() -> str:
    """Get the name of the cluster this command is being executed on"""
    hostname = HOSTNAME.lower() # type: ignore
    if      'sh'     in hostname: return 'sherlock2'
    elif    'gpu-15' in hostname: return 'sherlock2'
    elif    'su'     in hostname: return 'suncat' #important to distinguish suncat2 and 3?
    elif    'kris'   in hostname: return 'kris'
    elif    'local'  in hostname: return 'local'
    else: raise ValueError("was not able to identify the cluster from hostname = %s"%hostname)



def get_analysis_folder(sd : str) -> str:
    """
    Takes either the stordir or the sherlock folder and gives analysis folder
    """
    sd2 = get_sherlock_folder(sd)
    if  'suncat' in sd2: sd2=sd2.replace('suncat_jobs_copy/jobs/','analysis_suncat/')
    elif 'nersc' in sd2: sd2=sd2.replace('nersc_jobs_copy/jobs/','analysis_nersc/')
    else:              sd2=sd2.replace('jobs/','analysis_sherlock/')
    return sd2

def get_sherlock_folder(sd : str) -> str:
    """Takes a storage_directory and gives the path to its copy on sherlock"""
    replace_dict = {'/nfs/slac/g/suncatfs/ksb/share/jobs/' : '/scratch/users/ksb/share/suncat_jobs_copy/jobs/'
                   ,'/global/cscratch1/sd/krisb/share/jobs/':'/scratch/users/ksb/share/nersc_jobs_copy/jobs/'}
    return replacer(str(sd),replace_dict)


def launch() -> None:
    """Tell FireWorks to submit READY jobs to their respective queues"""
    os.system('$SCRATCH/CataLog/fw/launcher.sh')

def safeMkDir(pth     : str
             ,verbose : bool = True
             ) -> None:
    """Make directories even if they already exist"""
    try:            os.mkdir(pth)
    except OSError:
        if verbose: print('directory %s already exists ?!'%pth)

def safeMkDirForce(pth : str)->None:
    """
    Makes a nested directory, even if intermediate links do not yet exist
    """
    components = pth.split('/')
    curr_dir = [components[0]]
    for c in components[1:]:
        curr_dir.append(c)
        safeMkDir('/'+os.path.join(*curr_dir),verbose=False)

def get_hostname_from_fworker(fworker : str) -> str:
    if fworker == 'sherlock2':
        return 'login.sherlock.stanford.edu'
    elif fworker == 'suncat':
        return 'suncatls1.slac.stanford.edu'
    else:
        raise NotImplementedError('please add the fworker to catalog.misc.utilities.get_hostname_from_fworker')

def get_cluster_of_file(file : str) ->str:
    if '/u/if/' in file:
        return 'suncat'
    elif '/scratch/users/':
        return 'sherlock'
    else:
        raise NotImplementedError('Cluster not found')

def read_into_temp(file_to_read : str
                  ) -> str:
    import tempfile
    current_cluster = get_cluster()
    cluster_to_read = get_cluster_of_file(file_to_read)
    new_path        = tempfile.mkstemp()[-1]
    if cluster_to_read == current_cluster:
        return file_to_read
    if cluster_to_read == 'sherlock':
         cluster_host_name = 'login.sherlock.stanford.edu'
    elif cluster_to_read == 'suncat':
         cluster_host_name = 'suncatls1.slac.stanford.edu'
    else:
         raise NotImplementedError('Cluster not valid')
    os.system('scp -q {}@{}:{} {}'.format(user,cluster_host_name,file_to_read,new_path))
    return new_path

#############
# SQL Related
#-----------

################
# String related
#--------------
def modify_time(t          : str
               ,multiplier : float = 2.0
               ) -> str:
    def printTime(floatHours : float) -> str:
        intHours = int(floatHours)
        return "%02d:%02d" % (intHours,(floatHours-intHours)*60)

    """
    Modifies time in either HH:MM::SS or HH:MM format. Min time = 1 hr, max time = 40 hr
    """
    times = [int(x) for x in t.split(':')]
    HHMMSS = len(times) == 3
    tot = times[0]+times[1]/60.0 + (times[2]/3600.0 if HHMMSS else 0)
    return printTime(min(40,math.ceil(multiplier*tot)))+(':00' if HHMMSS else '')

def sub_binds(sql_select : typ.Any) -> None:
    """Prints a sql command in a human-readable way that can be copypasted
    into DB Browswer for SQLite."""

    keywords = ['INNER','FROM','HAVING','WHERE',"GROUP BY",", "]

    (sql_command,binds) = tuple(sql_select)
    sql_command = sql_command.replace('"','`')
    for b in binds: sql_command=sql_command.replace('%s',repr(b),1)

    replace_dict = {x:('\n\t'+x) for x in keywords}

    print('\n\t'+replacer(sql_command,replace_dict)+'\n')

def replacer(s : str
            ,replace_dict : typ.Dict[str,str]
            ) -> str:
    """Executes a series of string replacement operations, specified by a
    dictionary"""
    for k,v in replace_dict.items(): s = s.replace(k,v)
    return s

def merge_dicts(listDicts : typ.List[dict]) -> dict:
    return dict(itertools.chain.from_iterable([x.items() for x in listDicts])) #presumes no overlap in keys

##############
# List related
#-------------
def chunks(l : list, n : int) -> typ.Generator: #Yield successive n-sized chunks from l.
    for i in range(0, len(l), n): yield l[i:i + n]

def flatten(lol : typ.List[list]) -> list:
    return [item for sublist in lol for item in sublist] #flattens a List Of Lists to a list

def gcd(args : typ.List[typ.Any])->typ.Any:
    """
    Greatest common denominator of a list
    """
    if len(args) == 1:  return args[0]
    L = list(args)
    while len(L) > 1:
        a,b = L[len(L) - 2] , L[len(L) - 1]
        L = L[:len(L) - 2]
        while a:   a, b = b%a, a
        L.append(b)
    return abs(b)

def normalize_list(l : list ) -> list:
    """ [a,a,a,a,b,b,c,c] => [a,a,b,c] """
    if len(l)==0: return l
    d   = {x:l.count(x) for x in l}
    div = gcd(list(d.values()))
    norm= [[k]*(v/div) for k,v in d.items()]
    return [item for sublist in norm for item in sublist]
