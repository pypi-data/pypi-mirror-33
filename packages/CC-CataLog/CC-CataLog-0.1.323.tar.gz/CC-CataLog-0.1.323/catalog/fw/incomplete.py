# Typing modules
import typing as typ

#External modules
import os,subprocess,datetime,json,datetime,types,glob,time
import numpy as np                           # type: ignore
import fireworks,prettytable                 # type: ignore
from fireworks.core.firework import FWAction # type: ignore
from prettytable import PrettyTable          # type: ignore

#Internal Modules
import catalog.jobs.jobs        as jobs
import catalog.jobs.cluster     as cluster
from catalog.jobs.cluster       import cluster_dict
from catalog.misc.print_parse   import ask
from catalog.misc.utilities     import launch, merge_dicts,modify_time, get_cluster,get_cluster_of_file
from catalog.catalog_config     import USER, LAUNCHPAD_YAML

################################################################################

try:
    lpad = fireworks.LaunchPad.from_file(LAUNCHPAD_YAML) #lpad = fireworks.LaunchPad.auto_load() -- only works if in fireworks directory
except:
    pass

def detect() -> None:
    lpad.detect_unreserved(expiration_secs=3600*24*7, rerun=True)                # False positive: job has been sitting in queue for over a week
    lost,_,_ = lpad.detect_lostruns(3600*24, fizzle=True)                           # max_runtime=???,min_runtime=???) # False positive: job has not updated electronic step in 24 hours
    for fwid in lost:
        store_error_on_fwid(fwid,'timeout')

def cancel_job(fwid : int) -> None:
    reservation_id  = lpad.get_reservation_id_from_fw_id(fwid)
    if reservation_id == None:
        print('Job has no reservation_id')
        return
    fworker = lpad.get_fw_dict_by_id(fwid)['spec']['_fworker']
    import logging
    if fworker in ['suncat','suncat2']:
        subprocess.Popen(['ssh','{0}@suncatls1.slac.stanford.edu'.format(USER), 'bkill %s'%(reservation_id)], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        logging.info('Canceled Suncat Job: {0}'.format(reservation_id))
    elif fworker =='sherlock2' and get_cluster() == 'sherlock':
        subprocess.Popen(['scancel','%s'%(reservation_id)], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        logging.info('Canceled Sherlock2 Job: {0}'.format(reservation_id))
    elif fworker =='sherlock2':
        subprocess.Popen(['ssh','{0}@login.sherlock.stanford.edu'.format(USER),'scancel','%s'%(reservation_id)], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        logging.info('Canceled Sherlock2 Job: {0}'.format(reservation_id))
    else: raise NotImplementedError('new cluster?')

def fizzle_invalid_reservation_ids() -> None:
    """
    Check RUNNING and RESERVED jobs to see if their reservation_id is actually
    currently running on its assumed cluster. If not, it will fizzle the firework

    only works on sherlock2 and suncat
    """
    #Get the launched jobs and the currently valid reservation_ids
    launched_fwids           = runningFWIDS()+reservedFWIDS()
    actual_reservation_ids   = get_reservation_ids()

    def check_if_job_not_running(fwid : int) -> bool:
        """Returns True if the reservation_id is not actually running/pending"""
        cluster                = lpad.get_fw_dict_by_id(fwid)['spec']['_fworker']
        assumed_reservation_id = lpad.get_reservation_id_from_fw_id(fwid)
        return not assumed_reservation_id in actual_reservation_ids[cluster]

    #Filter out the fwids with valid reservation_ids
    fwids_with_inv_res_ids             = filter(check_if_job_not_running,launched_fwids)
    #Filter out fwids that are timed-out (they are checked elsewhere)
    fwids_with_inv_res_ids_no_timeouts = filter(lambda fwid: not getTimeout(fwid), fwids_with_inv_res_ids)
    #Fizzle the fireworks with invalid reservation_ids
    for fwid in fwids_with_inv_res_ids_no_timeouts:
        fizzle(fwid)

def get_reservation_ids() -> typ.Dict[str,str]:
    """
    Gets the reservation ids for reserved and running jobs on suncat and sherlock
    """
    reservation_ids = {}

    #Get Sherlock2 reservation_ids
    ssh_command                  = ['ssh','{0}@login.sherlock.stanford.edu'.format(USER)]
    command                      = ['squeue', '-u',USER,'-o','"%.18i"']
    proc                         = subprocess.Popen(ssh_command+command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, _                       = proc.communicate()
    reservation_ids['sherlock2'] = out.decode().replace('"','').split()[1:]

    #Get suncat reservation_ids
    ssh_command               = ['ssh','{0}@suncatls1.slac.stanford.edu'.format(USER)]
    command                   = ['bjobs','|','awk',"'{print $1}'",'|','grep','-v','suncat','|','grep','-v','JOBID']
    proc                      = subprocess.Popen(ssh_command+command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, _                    = proc.communicate()
    reservation_ids['suncat'] = out.decode().split()
    return reservation_ids

##################
# Helper functions
#-----------------
def fizzle(fwid             : int
          ,force_cancel     : bool = False
          ) -> None:
    fw_dict = lpad.get_fw_dict_by_id(fwid)
    state   = fw_dict['state']
    fworker = fw_dict['spec']['_fworker']
    reservation_id = lpad.get_reservation_id_from_fw_id(fwid)
    if force_cancel:
        cancel_job(fwid)
        store_error_on_fwid(fwid,'canceled')

    if state in ['RUNNING','RESERVED']:
        last_launch_id       = fw_dict['launches'][-1]['launch_id']
        lpad.mark_fizzled(last_launch_id)
        time.sleep(2)
    else:
        print('cannot fizzle FWID %d if it has status %s'%(fwid,state))


def filterError(keywords : typ.List[str]
               ) -> typ.List[int]:
    """
    List of job ids with a traceback containing one of a set of target words
    """
    output = []
    for i in fizzledFWIDS():
        err = getErr(i)
        if err is not None:
            if any([k in err for k in keywords]): output.append(i)
    return output

def archive_by_fwid(fwid : int) -> None:
    if lpad.get_reservation_id_from_fw_id(fwid):
        cancel_job(fwid)
    lpad.archive_wf(fwid)

def store_error_on_fwid(fwid      : int
                       ,traceback : str
                       ) ->None:
    fwdict             = lpad.get_fw_dict_by_id(fwid)
    last_launch_id     = fwdict['launches'][-1]['launch_id']
    last_launch        = lpad.get_launch_by_id(last_launch_id)
    current_action     = last_launch.action
    current_action     = current_action if not current_action == None else FWAction()
    current_action.stored_data.update({'_exception':{'_traceback':traceback}})
    last_launch.action = current_action
    lpad.launches.find_one_and_replace({'launch_id':last_launch.launch_id}
                                      ,last_launch.to_db_dict())


##################
# Lists of fwids
#-----------------
def allFWIDS() -> typ.List[int] :
    return lpad.get_fw_ids()
def defusedFWIDS() -> typ.List[int]:
    return lpad.get_fw_ids({'state':'DEFUSED'})
def fizzledFWIDS() -> typ.List[int]:
    return lpad.get_fw_ids({'state':'FIZZLED'})
def completeFWIDS() -> typ.List[int]:
    return lpad.get_fw_ids({'state':'COMPLETED'})
def archivedFWIDS() -> typ.List[int]:
    return lpad.get_fw_ids({'state':'ARCHIVED'})
def readyFWIDS() -> typ.List[int]:
    return lpad.get_fw_ids({'state':'READY'})
def reservedFWIDS() -> typ.List[int]:
    return lpad.get_fw_ids({'state':'RESERVED'})
def runningFWIDS() -> typ.List[int]:
    return lpad.get_fw_ids({'state':'RUNNING'})
def incompleteFWIDS() -> typ.List[int]:
    return lpad.get_fw_ids({'state':{'$in':['FIZZLED','DEFUSED','RESERVED','RUNNING','READY']}})
def runningTimeout()-> typ.List[int]:
    return [i for i in runningFWIDS() if getTimeout(i)]

def FWIDS_with_error(err : str) -> typ.List[int]: raise NotImplementedError
def unknownFWIDS()-> typ.List[int]: raise NotImplementedError

def noErrors()-> typ.List[int]:
    return [i for i in fizzledFWIDS() if getErr(i) is None]

def jobsSinceXhours(x : float)-> typ.List[int]:
    output = []
    for i in allFWIDS():
        t = timeSince(i)
        if t is not None and t < x: output.append(i)
    return output

def jobs_created_since_X_hours(x : float)-> typ.List[int]:
    output = []
    for i in allFWIDS():
        t = time_since_creation(i)
        if t is not None and t < x: output.append(i)
    return output


def fwid2status(fwid : int) ->str:
    fwdict = lpad.get_fw_dict_by_id(fwid)
    state = fwdict['state']
    return state2status(state, fwid)

def state2status(state : str
                ,fwid  : int
                ) -> str:
    if state in ['ARCHIVED','COMPLETED','RESERVED','READY','DEFUSED','PAUSED','WAITING']:
        return state
    elif state =='RUNNING':
        if getTimeout(fwid):
            fizzle(fwid)
            store_error_on_fwid(fwid,'timeout')
            return 'TIMED-OUT'
        else: return 'RUNNING'
    else: # fizzled
        err = getErr(fwid)
        if err is None:
            store_error_on_fwid(fwid,'canceled')
            return 'CANCELLED'
        else:
            err_message = sortErrLog(err)
            return err_message


##############
# Known Errors
#-------------

errorDict = {'TIMED-OUT'  : ['TIME','time','User defined signal 2','DUE TO TIME LIMIT']
            ,'CANCELED'   : ['canceled','KeyboardInterrupt']
            ,'kohnsham'   : ['KohnShamConvergenceError']
            ,'stres_vdw'  : ['ValueError: Extra data:']
            ,'scf'        : ['Error in routine stres_vdW_DF']
            ,'diagonalize': ['RuntimeError: SCF calculation failed']
            ,'mismatch'   : ['Mismatch of Atoms objects']
            ,'unpack'     : ['need more than 2 values to unpack']
            ,'EOFError'   : ['EOFError']}

def sortErrLog(err : typ.Optional[str]
              ) -> str:
    """
    Helpful docstring
    """
    if err is None:
        return 'no error'
    for e in errorDict.keys():
        if any([x in err for x in errorDict[e]]):
            return e
    return 'unknown'



##########################
# Things to get from a job
#-------------------------
def timeSince(fwid:int)->typ.Optional[float]:
    try:
        fwdict      = lpad.get_fw_dict_by_id(fwid)
        states      = fwdict['launches'][-1]['state_history']

        starttime   = [state['created_on'] for state in states if state['state']=='RUNNING'][0]

        format      = '%Y-%m-%dT%H:%M:%S.%f'
        start       = datetime.datetime.strptime(starttime,format)
        now         = datetime.datetime.utcnow()
        delta       = (now - start).total_seconds()/3600.

        return delta
    except (TypeError,KeyError,IndexError) as e:
        return None

def time_since_creation(fwid : int)->typ.Optional[float]:
    try:
        fwdict      = lpad.get_fw_dict_by_id(fwid)
        starttime   = fwdict['created_on']
        format      = '%Y-%m-%dT%H:%M:%S.%f'
        start       = datetime.datetime.strptime(starttime,format)
        now         = datetime.datetime.utcnow()
        delta       = (now - start).total_seconds()/3600.

        return delta
    except (TypeError,KeyError,IndexError) as e:
        return None

def getTimeout(fwid : int) -> bool:
    try:
        fwdict      = lpad.get_fw_dict_by_id(fwid)
        #print 'fwdict ',fwdict
        lastlaunch  = fwdict['launches'][-1]
        starttime   = lastlaunch['time_start']
        format      = '%Y-%m-%dT%H:%M:%S.%f'
        start       = datetime.datetime.strptime(starttime,format)
        now         = datetime.datetime.utcnow()

        delta       = (now - start).total_seconds()

        walltime    = fwdict['spec']['_queueadapter']['walltime']
        walltimelist= walltime.split(':')
        wallseconds = sum([int(x)*y for x,y in zip(walltimelist,[3600,60,1])])  # HH:MM or HH:MM:SS

        #print 'delta ',delta,' wallseconds ',wallseconds

        if delta > wallseconds: return True
        else: return False
    except TypeError: return False

def getErr(fwid:int)->str:
    try:
        return lpad.get_fw_dict_by_id(fwid)['launches'][-1]['action']['stored_data']['_exception']['_traceback']
    except:
        return ''
    # ld = lpad.get_launchdir(fwid)
    # user = os.environ['USER']
    # if 'scratch' in ld:
    #         d   = subprocess.Popen(['ssh','{0}@login.sherlock.stanford.edu'.format(user), 'cat %s/*.error'%ld], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    #         dout, err = d.communicate()
    #         dout = dout.decode()
    #         if len(dout)==0: return ''
    #         else:            return dout
    # elif 'nfs' in ld:
    #         # return ''
    #         d   = subprocess.Popen(['ssh','{0}@suncatls1.slac.stanford.edu'.format(user), 'cat %s/*.error'%ld], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    #         dout, err = d.communicate()
    #         dout = dout.decode()
    #         if len(dout)==0: return ''
    #         else:            return dout
    # raise NotImplementedError('new cluster?')



def modify(fwid       : int
          ,specKey    : str
          ,updateFunc : typ.Callable
          ) -> None:
    """
    CANNOT USE ON RUNNING JOBS
    """
    spec = lpad.get_fw_dict_by_id(fwid)['spec']
    new = updateFunc(spec[specKey])
    lpad.update_spec([fwid],{specKey:new})

def multiply_time(qadapt     : dict
                 ,multiplier : float = 2.0
                 ) -> dict:
    qadapt['walltime'] =  modify_time(qadapt['walltime'], multiplier)

    if qadapt['walltime'][:2] == '40':
        print('warning, 40h job')

    return qadapt

def multiply_nodes(qadapt     : dict
                  ,multiplier : int     = 2
                  ) -> dict:
    """
    Docstring
    """
    if qadapt['_fw_q_type']=='SLURM': qadapt['nodes']*=multiplier
    if qadapt['_fw_q_type']=='LoadSharingFacility': qadapt['ntasks']*=multiplier
    return qadapt

def improve_conv(params : dict) -> dict:
    #params['mixing']*=0.25
    #params['econv']*=0.5
    params['nmix'] = 1
    return params

def switchCluster(fwid              : int
                 ,from_cluster_str  : str
                 ,to_cluster_str    : str
                 ) -> None:
    """
    UNTESTED: only goes from sherlock <--> suncat
    """
    assert from_cluster_str in cluster_dict.keys() and to_cluster_str in cluster_dict.keys(), \
    'Please give valid cluster string. Valid strings in {0}'.format(cluster_dict.keys())
    from_cluster           = cluster_dict[from_cluster_str]
    to_cluster             = cluster_dict[to_cluster_str]
    fw_dict                = lpad.get_fw_dict_by_id(fwid)
    fw_spec                = fw_dict['spec']
    fworker                = fw_spec['_fworker']
    walltime               = int(fw_spec['_queueadapter']['walltime'].split(':')[0])
    nodes                  = fw_spec['_queueadapter']['nodes'] if fworker=='sherlock' else 1
    timestamp              = '_'+datetime.datetime.now().strftime('%Y_%m_%d_%H_%M_%S')
    time.sleep(2)
    jobkind                = fw_spec['params']['jobkind']
    old_launchdir          = lpad.get_launchdir(fwid)
    new_launch_dir         = to_cluster.get_launchdir()+jobkind+timestamp
    job_has_prior_launches = len(fw_dict.get('launches',[]))>0
    if fworker == from_cluster_str and not to_cluster_str == fworker:
        if job_has_prior_launches:
            fizzle(fwid, force_cancel = True)
        if fworker=='sherlock':                    # if switching FROM sherlock
            assert fw_spec['params']['dftcode']!='gpaw' # then DFTcode cannot be GPAW
        modify(fwid,'_fworker', 	 lambda x: to_cluster.fworker.name)
        modify(fwid,'_queueadapter', lambda x: to_cluster.qfunc(walltime,nodes))
        if not (fworker in ['sherlock','sherlock2'] and to_cluster_str in ['sherlock','sherlock2']):
            modify(fwid,'_launch_dir', 	 lambda x: new_launch_dir)
        print(from_cluster_str,to_cluster)
        if job_has_prior_launches and from_cluster_str in ['sherlock2','sher2','suncat'] and to_cluster_str in ['sherlock2','sher2','suncat']:
            transfer_directories_between_clusters(old_launchdir,new_launch_dir)
    else:
        print('FWID #{0} already on {1} cluster'.format(fwid, from_cluster_str))

def transfer_directories_between_clusters(source_dir : str
                                         ,dest_dir   : str
                                         )->None:
    """
    Transfers launch directories for a firework that is rerun on a new cluster

    Copies the contents of the launch directory on the original cluster to the
    new cluster. Currently only works for Sherlock2 <-> Suncat. See
    catalog.misc.utilities.get_cluster_of_file to guess the cluster of each
    directory

    Parameters
    ----------
    source_dir : str
        absolute directory of the original launch
    dest_dir   : str
        absolute directory of the new launch

    """

    import tempfile
    hostname_dict = {'sherlock':'login.sherlock.stanford.edu','suncat':'suncatls1.slac.stanford.edu'}
    if not source_dir[-1]=='/':
        source_dir += '/'
    if not dest_dir[-1]=='/':
        dest_dir += '/'
    from_cluster = get_cluster_of_file(source_dir)
    to_cluster   = get_cluster_of_file(dest_dir)
    if get_cluster() == 'local':
        tempdir = tempfile.mkdtemp()
        get_folder_cmd  = 'rsync -r {}@{}:{} {}'.format(USER,hostname_dict[from_cluster],source_dir,tempdir+'/')
        send_folder_cmd = 'rsync -a --rsync-path="mkdir -p {} && rsync" -r {} {}@{}:{}'.format(dest_dir,tempdir+'/',USER,hostname_dict[to_cluster],dest_dir)
        remove_cmd      = 'rm -r {}'.format(tempdir)
        print(get_folder_cmd,send_folder_cmd)
        [os.system(cmd) for cmd in [get_folder_cmd,send_folder_cmd,remove_cmd]]


#########################
# More complicated things
#------------------------
def modifier(spec_key : str)->typ.Any:
    """
    For a given field of a FW's spec (specified by 'spec_key'):
        - Feed a FWID and dictionary of keys to that field with values of:
            - literal values to replace the value of that field
            - unary functions to update the value of that field
        - updates the FWID, returns nothing
    """
    def f(fwid : int,kwargs : dict)->None:
        q = lpad.get_fw_dict_by_id(fwid)['spec'][spec_key]
        for k,v in kwargs.items():
            if hasattr(v,'__call__'): q[k] = v(q[k]) # update
            else:                     q[k] = v       # replace
        lpad.update_spec([fwid],{spec_key:q})
    return f

def time_modifier(multiplier : int  = 2
                 ,time_set   : typ.Optional[int]  = None
                 )->typ.Any:
    def f(current_time : str)->str:
            def printTime(floatHours : float) -> str:
                intHours = int(floatHours)
                return "%02d:%02d" % (intHours,(floatHours-intHours)*60)

            """
            Modifies time in either HH:MM::SS or HH:MM format. Min time = 1 hr, max time = 40 hr
            """
            times = [int(x) for x in current_time.split(':')]
            HHMMSS = len(times) == 3
            tot = times[0]+times[1]/60.0 + (times[2]/3600.0 if HHMMSS else 0)
            if time_set is None:
                return printTime(min(72,np.ceil(multiplier*tot)))+(':00' if HHMMSS else '')
            else:
                return printTime(time_set)+(':00' if HHMMSS else '')
    return f

modify_q = modifier('_queueadapter')
modify_p = modifier('params')

def relaunch_fwids(list_of_fwids : typ.List[int]
                  ,q_dict        : dict    = {}
                  ,p_dict        : dict    = {}
                  )->None:
    for fwid in list_of_fwids:
        modify_q(fwid,q_dict)
        modify_p(fwid,p_dict)
        lpad.rerun_fw(fwid)

def time_to_caldate(x : str)->str:
    """
    """
    if isinstance(x,str):
        ll = datetime.datetime.strptime(x, "%Y-%m-%dT%H:%M:%S.%f")
    else:
        ll = x
    return '%d/%d'%(ll.month,ll.day)

def table_fireworks(cols : typ.List[str] = ['cluster','queue','Time','nodes','job_name','created_on','updated_on','_launch_dir']
                   ,fwidlist  : typ.Optional[typ.List[int]] = None
                   ) -> None:
    """
    A Janky Function to print out useful information about incomplete jobs from fireworks
    """
    #Merge the fireworks spec dictionary with the params for easy access
    if fwidlist is None: fwidlist = incompleteFWIDS()
    if len(fwidlist)==0:
        print('no incomplete jobs!')
        return None

    fwidlist        = sorted(fwidlist)
    dict_array      = [[fw,fw['spec']['params'],fw['spec']] for fw in  map(lpad.get_fw_dict_by_id, fwidlist)]
    status_array    = list(map(lambda x: state2status(x['state'],x['fw_id']),list(zip(*dict_array))[0]))
    full_dict_array = list(map(merge_dicts,dict_array))
    def get(f:typ.Callable)->list:
        return list(map(f,full_dict_array))

    #Iterate through the supplied table columns to generate pretty table rows
    col_array = []
    for key in cols:
        #Job Name requires unpacking as it is stored in the kwargs dictionary
        if key =='job_name':
            def getJobName(dict_curr : dict) -> str:
                kwargs = dict_curr.get('kwargs')
                if kwargs is None:
                    return dict_curr.get('job_name','')
                else:
                    return json.loads(kwargs).get('job_name','')
            col_array.append(get(getJobName))
        elif key in ['created_on','updated_on']:
            def get_time(d_c : dict)->str: return time_to_caldate(d_c[key])
            col_array.append(get(get_time))
        elif key == 'queue':
            def get_queue(d_c:dict)->str: return d_c['_queueadapter']['queue'].replace(',','\n')
            col_array.append(get(get_queue))
        elif key == 'Time':
            def get_queuetime(dict_curr:dict)->str:
                if dict_curr['state']=='RESERVED':
                    last_launch = dict_curr['updated_on']#dict_curr['launches'][-1]['state_history'][-1]['created_on']
                    if isinstance(last_launch,str):
                        ll = datetime.datetime.strptime(last_launch, "%Y-%m-%dT%H:%M:%S.%f")
                        return  str(round((datetime.datetime.utcnow()-ll).total_seconds()/3600,1))
                    elif isinstance(last_launch,datetime.datetime):
                        return  str(round((datetime.datetime.utcnow()-last_launch).total_seconds()/3600,1))
                    else:
                        raise ValueError('last_launch is not a string or datetime.datetime object')
                elif dict_curr['state']=='RUNNING':
                    walltime_str = dict_curr['_queueadapter']['walltime']
                    walltime = sum([int(a)*b for a,b in zip(walltime_str.split(':'),[60,1,0])])/60.
                    last_launch = dict_curr['launches'][-1]['state_history'][-1]['created_on']
                    ll = datetime.datetime.strptime(last_launch, "%Y-%m-%dT%H:%M:%S.%f")
                    elapsed_time =round((datetime.datetime.utcnow()-ll).total_seconds()/3600,1)
                    return '%g/%g'%(elapsed_time,walltime)
                else: return ''
            col_array.append(get(get_queuetime))
        elif key == 'nodes':
            def get_nodes(dict_curr:dict)->int:
                q = dict_curr['_queueadapter']
                if dict_curr['_fworker'] in ['sherlock','sherlock2','cori']: return q['nodes']
                else:
                    node_dict = {'suncat':8,'suncat2':12}
                    return q['ntasks']/node_dict[q['queue']]
            col_array.append(get(get_nodes))
        elif key == 'cluster':
            def get_cluster(d_c:dict)->str:
                return d_c['_fworker'].replace('lock','')
            col_array.append(get(get_cluster))
        elif key == '_launch_dir':
            def get_ld(d_c:dict)->str:
                launch_dir = d_c.get('_launch_dir','')
                # launch_dir = launch_dir.replace('/scratch/users/{}'.format(user),'$SCRATCH')
                # launch_dir = launch_dir.replace('/nfs/slac/g/suncatfs/{}'.format(user),'$SCRATCH')
                return launch_dir
            col_array.append(get(get_ld))
        else:
            col_array.append(get(lambda d_c: d_c[key]))
    # Build and print the pretty table
    table = prettytable.PrettyTable() #type: ignore
    for col_name, col_data in zip(['fwid','status']+cols,[fwidlist, status_array]+col_array): #type: ignore
        table.add_column(col_name, col_data)
    print(table.get_string(sortby="status",reversesort=True))
    print('TOTAL: %d'%len(full_dict_array))

def table_data(cols : typ.List[str] = ['status','cluster','queue','Time','nodes','job_name','created_on','updated_on','_launch_dir']
              ) -> list:
    """
    A Janky Function to print out useful information about incomplete jobs from fireworks
    """
    #Merge the fireworks spec dictionary with the params for easy access
    fwidlist = incompleteFWIDS()
    if len(fwidlist)==0:
        print('no incomplete jobs!')
        return None

    fwidlist        = sorted(fwidlist)
    dict_array      = [[fw,fw['spec']['params'],fw['spec']['_queueadapter'],fw['spec']] for fw in  map(lpad.get_fw_dict_by_id, fwidlist)]
    full_dict_array = list(map(merge_dicts,dict_array))

    def process_row(d_c : dict) -> list:
        #List of keys that are simple dictionary lookups
        simple_keys    = ['Cluster','Queue','Nodes','Job Name','Launch Dir']
        simple_key_map = {'cluster'    : '_fworker'
                         ,'Queue'      : 'queue'
                         ,'Nodes'      : 'nodes'
                         ,'Job Name'   : 'job_name'
                         ,'Launch Dir' : '_launch_dir'
                         }
        state = d_c['state']

        col_values = [d_c['fw_id']]
        for key in cols:
            if key in simple_keys:
                col_values.append(d_c.get(simple_key_map[key],''))
            elif key == 'Time':
                if state =='RESERVED':
                    last_launch = d_c['updated_on']
                    if isinstance(last_launch,str):
                        ll = datetime.datetime.strptime(last_launch, "%Y-%m-%dT%H:%M:%S.%f")
                        col_values.append(str(round((datetime.datetime.utcnow()-ll).total_seconds()/3600,1)))
                    elif isinstance(last_launch,datetime.datetime):
                        col_values.append(str(round((datetime.datetime.utcnow()-last_launch).total_seconds()/3600,1)))
                    else:
                        raise ValueError('last_launch is not a string or datetime.datetime object')
                elif state =='RUNNING':
                    walltime_str = d_c['_queueadapter']['walltime']
                    walltime = sum([int(a)*b for a,b in zip(walltime_str.split(':'),[60,1,0])])/60.
                    last_launch = d_c['launches'][-1]['state_history'][-1]['created_on']
                    ll = datetime.datetime.strptime(last_launch, "%Y-%m-%dT%H:%M:%S.%f")
                    elapsed_time =round((datetime.datetime.utcnow()-ll).total_seconds()/3600,1)
                    col_values.append('%g/%g'%(elapsed_time,walltime))
                else: col_values.append('')
            elif key in ['created_on','updated_on']:
                col_values.append(time_to_caldate(d_c[key]))
            elif key == 'status':
                col_values.append(state2status(state,d_c['fw_id']))
            else:
                col_values.append(d_c.get(key,''))

        return col_values

    output = list(map(process_row,full_dict_array))
    return output


def fill_incomplete_jobs_txt_file(fwidlist  : typ.Optional[typ.List[int]] = None)  -> None:
    """
    A Janky Function to print out useful information about incomplete jobs from fireworks
    """
    #Merge the fireworks spec dictionary with the params for easy access
    if fwidlist is None: fwidlist = incompleteFWIDS()
    if len(fwidlist)==0:
        print('no incomplete jobs!')
        return None

    fwidlist        = sorted(fwidlist)
    dict_array      = [[fw,fw['spec']['params'],fw['spec']] for fw in  map(lpad.get_fw_dict_by_id, fwidlist)]
    status_array    = list(map(lambda x: state2status(x['state'],x['fw_id']),list(zip(*dict_array))[0]))
    full_dict_array = list(map(merge_dicts,dict_array))

    file_name = '/scratch/users/{}/.launch_dirs_tmp.txt'.format(os.environ['USER'])

    if os.path.exists(file_name):
        open(file_name,'w').close()
    with open(file_name,'w') as file:
        for d_c in full_dict_array:
            launch_dir = d_c.get('_launch_dir','')+'\n'

            file.write(launch_dir)

if __name__ == '__main__':
    import sys
    cols = sys.argv[1:]
    print(table_data(cols))

###############
#Archived Code
###############


#
# def errFWIDS(err : str) -> typ.List[int]:
#     """
#     Get list of FWIDs that have a particular type of error (defined in errorDict)
#     """
#     return filterError(errorDict[err])

# def errReport() -> None:
#     """
#
#     """
#     fizz = fizzledFWIDS()
#     rto  = runningTimeout()
#     lFizz = len(fizz)
#     lReady,lRes,lRun,lArch,lComp,lTot,lrTO = map(len,[readyFWIDS(),reservedFWIDS(),runningFWIDS(),archivedFWIDS(),completeFWIDS(),lpad.get_fw_ids(),rto])
#
#     resSherlock = len(lpad.get_fw_ids({'state':'RESERVED','spec._fworker':'sherlock'}))
#     runSherlock = len([fw for fw in lpad.get_fw_ids({'state':'RUNNING','spec._fworker':'sherlock'}) if fw not in rto])
#
#     print("\nStatus of all fireworks...")
#     x = PrettyTable(['Ready','Reserved (sherlock)','Reserved (suncat)','Running (sherlock)','Running (suncat)']) # type: ignore
#     x.add_row([      lReady,resSherlock,lRes-resSherlock,runSherlock,lRun-lrTO-runSherlock])
#
#     x2 = PrettyTable(['Running (timed out)','Fizzled','Archived','Completed','Total']) # type: ignore
#     x2.add_row([lrTO,lFizz,lArch,lComp,lTot])
#
#     if len(fizz)>0:
#         print('\nDiagnosis of fizzled fireworks')
#         ekeys = list(errorDict.keys())
#         unknowns,countDict = [],{x:0 for x in ekeys+['unknown','no error']}
#         for i in fizz:
#             n = countDict['unknown']
#             err = getErr(i)
#             if err is None:
#                 countDict['no error']+=1
#             else:
#                 countDict[sortErrLog(err)]+=1 # type: ignore
#             if countDict['unknown']>n:
#                 unknowns.append(i)
#
#         cD = {k:v for k,v in countDict.items() if v != 0}
#         y = PrettyTable(cD.keys()) # type: ignore
#         y.add_row(cD.values())
#         print('\n',y)
#         if len(unknowns) > 0:
#             print("unknown FWIDS ",' '.join(map(str,unknowns)))

# def switchSherlock(fwid_low  : int
#                   ,fwid_high : typ.Optional[int] =None
#                   ) -> None:
#     """
#     Give a range of fwids that are queued on sherlock.
#     Switch them so that they can be launched on sherlock2
#     """
#     if fwid_high is None: fwid_high = fwid_low+1
#     resSherlock = lpad.get_fw_ids({'state':'RESERVED','spec._fworker':'sherlock'})
#     redSherlock = lpad.get_fw_ids({'state':'READY','spec._fworker':'sherlock'})
#     for fwid in resSherlock + redSherlock:
#         if fwid in range(fwid_low,fwid_high+1):
#             if fwid in resSherlock:
#                 fizzle(fwid)
#                 lpad.rerun_fw(fwid)
#             modify(fwid,'_fworker', lambda x: 'sherlock2')
#             modify(fwid,'_queueadapter',   sherQtosher2Q)
#     print('log into sherlock2 and launch')
#
# def sherQtosher2Q(q : dict) -> dict:
#     """
#
#     """
#     q = q.copy()
#     q['queue']           = 'suncat,iric'
#     q['qos']             = 'normal'
#     q['ntasks_per_node'] = 16
#     q['nodes']           = 1
#     return q


# def relaunch(timeout_q    : dict  = {},    timeout_p  : dict    = {}
#             ,unknown_q    : dict  = {},    unknown_p  : dict    = {}
#             ,noerror_q    : dict  = {},    noerror_p  : dict    = {}
#             ,ready_q      : dict  = {},    ready_p    : dict    = {}
#             ,unconverged_q: dict  = {},    unconverged_p : dict  = {}
#             )->None:
#     """
#     Relaunch with optionally modified queueadapter or params
#         - specify which keys to modify (and how) partitioned by kind of error
#     """
#     # Get FWID lists
#     detect()
#     timeouts       = runningTimeout()+errFWIDS('timeout')
#     readys         = readyFWIDS()
#     unconvergeds   = errFWIDS('kohnsham')
#     unknowns,noerr = fizzledFWIDS(), noErrors()
#
#     # Prepare Questions
#     tQuestion     = "Do you want to relaunch %d timed out runs?"%len(timeouts)
#     unkQuestion   = "Do you want to relaunch %d unknown error runs?"%len(unknowns)
#     uQuestion     = "Do you want to relaunch %d unconverged jobs?"%len(unconvergeds)
#     rQuestion     = "Do you want to relaunch %d ready jobs?"%len(readys)
#     nQuestion     = "Do you want to relaunch %d no-error jobs?"%len(noerr)
#
#     # Set defaults
#     #if not timeout_q: timeout_q = {'walltime': multiply_time(2)} BROKEN
#     if not unconverged_p: unconverged_p = {}
#
#     # Apply to each class of fizzled jobs
#     if ask(tQuestion):
#         for fwid in timeouts:
#             fizzle(fwid)  # needed for the spuriously RUNNING jobs
#             modify_q(fwid,timeout_q)
#             modify_p(fwid,timeout_p)
#             lpad.rerun_fw(fwid)
#
#     if ask(unkQuestion):
#         for fwid in unknowns:
#             modify_q(fwid,unknown_q)
#             modify_p(fwid,unknown_p)
#             lpad.rerun_fw(fwid)
#
#     if ask(nQuestion):
#         for fwid in noerr:
#             modify_q(fwid,noerror_q)
#             modify_p(fwid,noerror_p)
#             lpad.rerun_fw(fwid)
#
#     if ask(rQuestion):
#         for fwid in readys:
#             modify_q(fwid,ready_q)
#             modify_p(fwid,ready_p)
#             lpad.rerun_fw(fwid)
#
#     if ask(uQuestion):
#         for fwid in unconvergeds:
#             modify_q(fwid,unconverged_q)
#             modify_p(fwid,unconverged_p)
#             lpad.rerun_fw(fwid)
#
#     # launch()
#
# def get_running_jobs(fworker : str) -> typ.List[str]:
#     assert fworker in ['sherlock','sherlock2']
#     user = os.environ['USER']
#
#     if fworker == 'sherlock2' and get_cluster() == 'sherlock':
#         proc = subprocess.Popen(['squeue', '-u',user,'-o','"%.18i"'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
#         out, _ = proc.communicate()
#         reservation_ids = out.decode().replace('"','').split()[1:]
#     elif fworker == 'sherlock':
#         proc = subprocess.Popen(['ssh','{0}@sherlock.stanford.edu'.format(user),'squeue', '-u',user,'-o','"%.18i"'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
#         out, _ = proc.communicate()
#         reservation_ids = out.decode().replace('"','').split()[1:]
#     return reservation_ids
