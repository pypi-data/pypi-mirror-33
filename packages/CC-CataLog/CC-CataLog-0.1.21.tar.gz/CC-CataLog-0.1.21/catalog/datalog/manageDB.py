# # Typing Modules
#
#
# #External Modules
# import json,subprocess,os,shutil,itertools,pickle,glob,time
# import fireworks # type: ignore
# #Internal Modules
# import catalog.datalog.db_utils     as db
# # import catalog.detail.detail        as dt
# # import catalog.datalog.scrape       as scrape
#
# from catalog.misc.sql_utils  import *
# from catalog.misc.utilities     import flatten,merge_dicts,replacer
# from catalog.misc.print_parse   import (ask,print_sleep,abbreviate_dict
#                                        ,read_on_sher)
# ##########################
#
# """
# Functions for maintaining, updating, and creating a database for DFT calculations
#
# ### Database Maintenance
# - backup
# - delete
# - duplicates
#
# ### Updating
# - sync_suncat
# - update_db
#
# ### Database startup/generation
# - load_new
# - reset_all
# - load_jobs
# """
#
# ######################
# # Environment Variables
# # --------------------
# user   = os.environ['USER']
# try:
#     lpad    = fireworks.LaunchPad.from_file(os.environ.get('LAUNCHPAD_YAML'))
# except:
#     lpad    = None
# dbroot = '/scratch/users/ksb/share/'
# realdb = dbroot + 'suncatdata.db'
# tempdb = dbroot + 'temp.db'
#
# ######################
# # Database maintanence
# # --------------------
#
# def backup(force : bool = False) -> None:
#     root = dbroot+'backup/'
#     now  = time.time()
#
#     def getDaysSinceLastBackup(folderName : str) -> float:
#         return (now - os.path.getmtime(root+folderName+'/jobs'))/(24*3600)
#
#     def makeBackup(folderName : str) -> None :
#         print('backing up %s on sherlock'%folderName)
#         os.system('rsync  -rtqvu /scratch/users/ksb/share/jobs/ %s/jobs/ --delete'%(root+folderName))
#         os.system('touch -m %s/jobs'%(root+folderName)) #update mtime even if nothing transferred
#         print('backing up %s on suncat'%folderName)
#         suncout, err = subprocess.Popen(['ssh','{0}@suncatls1.slac.stanford.edu'.format(user), 'rsync  -rtqvu /nfs/slac/g/suncatfs/ksb/share/jobs/ /nfs/slac/g/suncatfs/ksb/share/backup/%s/jobs/ --delete'%folderName], stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
#         if user=='ksb':
#             print('backing up %s on nersc'%folderName)
#             nerscout, err = subprocess.Popen(['ssh','krisb@cori.nersc.gov', 'rsync  -rtqvu /global/cscratch1/sd/krisb/share/jobs/ /global/cscratch1/sd/krisb/share/backup/%s/jobs/ --delete'%folderName], stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
#             print(err)
#     lastMonth,lastWeek,lastDay = map(getDaysSinceLastBackup,['monthly','weekly','daily'])
#
#     if   lastMonth > 30: makeBackup('monthly')
#     elif lastWeek  > 7:  makeBackup('weekly')
#     elif lastDay   > 1 or force:
#         makeBackup('daily')
#         lpad.maintain(infinite=False)
#
# def delete(constraint : typ.Any
#           ,check      : bool    = True
#           ,archive    : bool    = True
#           ,deletePath : bool    = True
#           ) -> None:
#     """
#     Delete completed jobs that meet some constraint. Removes storage directory (but not working directory). Never delete from Temp.
#     """
#     # raise NotImplementedError
#     additionalConstraint = [USER_(user),job.deleted == 0]
#
#     output = db.Query([JOB,FWID,STORDIR,WORKDIR]
#                     ,AND(*(constraint + additionalConstraint))).query()
#     for jid,fwid,path,wpath in output:
#         if not check or ask('Do you want to delete %s?'%path):                          # Delete storage directory
#             if archive:
#                 try: lpad.archive_wf(fwid)                                                # Archive firework
#                 except ValueError: print('Could not archive fwid %d'%fwid)
#             db.updateDB('deleted',          'id',jid,1,                table='job')  # Note deletion in deleted column
#             db.updateDB('working_directory','id',jid,'formerly: '+wpath.replace('formerly: ',''),table='job')  # Modify due to UNIQUE constraint in schema
#             if deletePath:
#                 sherlock_trash = '/scratch/users/ksb/share/trash/'
#                 nfs_trash      = '/nfs/slac/g/suncatfs/ksb/share/trash/'
#                 nersc_trash    = '/global/cscratch1/sd/krisb/share/trash/'
#                 if 'scratch' in path:
#                     new_path = sherlock_trash + '%s/%s/'%(user,os.path.basename(path[1:len(path)-1]))
#                     shutil.move(path,new_path)
#                     print('moved from %s to %s'%(path, new_path))
#                 elif 'nfs' in path:
#                     new_path = nfs_trash + '%s/%s/'%(user,os.path.basename(path[1:len(path)-1]))
#                     d   = subprocess.Popen(['ssh','{0}@suncatls1.slac.stanford.edu'.format(user),
#                         'mv {0} {1}'.format(path,new_path)],
#                         stdout=subprocess.PIPE, stderr=subprocess.PIPE)
#                     dout, err = d.communicate()
#                     print('moved from %s to %s'%(path, new_path))
#                 elif 'global' in path:
#                     new_path = nersc_trash + 'krisb/%s/'%(os.path.basename(path[1:len(path)-1]))
#                     d   = subprocess.Popen(['ssh','krisb@cori.nersc.gov', 'mv {0} {1}'.format(path,new_path)],
#                                             stdout=subprocess.PIPE, stderr=subprocess.PIPE)
#                     dout, err = d.communicate()
#                     print('moved from %s to %s'%(path, new_path))
#                 else: raise NotImplementedError(path)
#                 db.updateDB('storage_directory','id',jid,new_path,table='job')  # Note deletion in deleted column <--- WHAT DOES THIS DO?
#             print('deleted!')
#
#
# #####################
# # Updating DB Columns
# # -------------------
#
# def sync_suncat()->None:
#     print('Syncing /nfs/slac/g/suncatfs/ksb/share/jobs to /scratch/users/ksb/share/suncat_jobs_copy/ ...')
#     os.system('rsync -rtqvu --perms --chmod=777 --omit-dir-times %s@suncatls1.slac.stanford.edu:/nfs/slac/g/suncatfs/ksb/share/jobs /scratch/users/ksb/share/suncat_jobs_copy/ --delete'%user)
# def sync_nersc()->None:
#     print('Syncing /global/cscratch1/sd/krisb/share/jobs to /scratch/users/ksb/share/nersc_jobs_copy/ ...')
#     os.system('rsync -rtqvu --perms --chmod=777 --omit-dir-times krisb@cori.nersc.gov:/global/cscratch1/sd/krisb/share/jobs /scratch/users/ksb/share/nersc_jobs_copy/ --delete')
#
#
#
#
# def update_db(cols       : typ.Optional[str]    = None
#              ,from_col   : typ.Optional[str]    = None
#              ,to_col     : typ.Optional[str]    = None
#              ,impt       : bool                 = True
#              ,retry      : bool                 = False
#              ,verbose    : bool                 = True
#              ,load       : bool                 = True
#              ,db_path    : str                  = realdb
#              ) -> None:
#     """
#     cols :: String
#         - Space separated list of column names
#         - Exclusive list of details to compute
#     from_col,to_col :: String
#         - Strings which denote the start and end columns for a range to details
#     impt :: Bool
#         - If true, don't compute useless/expensive things, like voronoi
#     retry :: Bool
#         - Overwrite existing values of columns
#     load :: Bool
#         - trigger load_db to be run
#     """
#
#     if cols is None: deets = dt.get_details(from_col,to_col,impt)
#     else:            deets = [dt.detail_dict[x] for x in cols.split()]
#
#     if load: load_jobs(db_path=db_path)
#
#     print('updating: <<%s>>'%','.join(map(str,deets)))
#
#     for d in deets:
#         d.apply(db_path,retry,verbose)
#         if str(d)=='refjob': fill_refeng(db_path=db_path)
#
# def fill_refeng(db_path : str = realdb) -> None:
#     """
#     Makes sure every relevant calculator has a row for each element
#     in refeng and every atoms has the right elements in composition
#
#     THIS SHOULD BE CALLED AFTER REFJOB IS APPLIED
#     """
#     cmd = 'INSERT OR IGNORE INTO refeng (calc_id,element_id,kptden_x,kptden_y) VALUES (?,?,?,?)'
#
#     binds = db.Query(cols     = [job.calc_id,REFJOB,KPTDEN_X,KPTDEN_Y]
#                     ,table    = job
#                     ,db_path  = db_path).query()
#
#     db.sqlexecutemany(cmd,binds,db_path=db_path) # type: ignore
#
# def fill_comp(db_path : str = realdb)->None:
#     """
#     Adds rows for each chemical composition
#
#     THIS SHOULD BE CALLED AFTER NEW JOBS ARE LOADED
#     """
#     cmd = 'INSERT OR REPLACE INTO composition (atoms_id,element_id,has) VALUES (?,?,?)'
#     atoms_elems = db.Query(cols  = [ATOMSID,NUMBER]
#                         ,table = atom
#                         ,distinct= True
#                         ,db_path=db_path).query()
#
#     binds = [(x,y,1) for (x,y) in atoms_elems]
#
#     db.sqlexecutemany(cmd,binds,db_path=db_path) # type: ignore
#
# #############################
# # Database startup/generation
# # ---------------------------
#
# def load_new(db_path : str = realdb) -> None:
#     if user=='ksb': backup()
#     load_jobs(db_path=db_path)
#     update_db(load=False,db_path=db_path)
#
# def reset_derived(db_path : str = realdb) -> None:
#     for d in dt.details: d.reset(db_path)
#
# def reset_from(from_col : str
#               ,db_path  : str = realdb
#               ) -> None:
#     for d in dt.get_details(from_col=from_col): d.reset(db_path)
#     update_db(from_col=from_col,load=True,retry=True,db_path=db_path)
#
# def reset_refeng(db_path : str = realdb) -> None:
#     db.drop_table('refeng',db_path=realdb)
#     db.add_refeng(db_path)
#     reset_from('refjob')
#
# def reset_all(limit     : typ.Optional[int] = None
#              ,update    : bool              = False
#              ,db_path   : str               = tempdb
#              ) -> None:
#     """
#     Repopulate completed table using the data stored in .../ksb/shared/jobs/...
#     """
#     db.removeSuncatDataDB(db_path) # removes temp
#     db.createSuncatDataDB(db_path) # creates temp
#     load_jobs(limit,db_path)       # loads temp
#     fill_comp(db_path)             # populates composition table (derived from atom table)
#     if update: update_db(load=False,db_path=db_path) # takes 2-3x longer
#
#
# def load_jobs(limit   : typ.Optional[int] = None
#              ,db_path : str =realdb
#              ) -> None:
#     """
#     Loads all completed jobs into the database
#     Scrapes any folder not in 'storage_directory' column for info in atoms/calc/job tables
#     """
#     sync_suncat() # Make sure .../share/suncatdataTEMP/ matches /nfs/slac/g/suncatfs/ksb/share/jobs
#     if user=='ksb': sync_nersc()
#     print("Loading recently completed jobs ...")
#
#     sharedjobsSherlock = '/scratch/users/ksb/share/jobs'
#     sharedjobsSuncat   = '/nfs/slac/g/suncatfs/ksb/share/jobs'
#     sharedjobsNersc    = '/global/cscratch1/sd/krisb/share/jobs'
#
#     suncout, serr = subprocess.Popen(['ssh','{0}@suncatls1.slac.stanford.edu'.format(user), 'cd %s;ls -d $PWD/*/*'%sharedjobsSuncat]
#                                     , stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate() # List of jobs in suncat stored jobs
#     if user == 'ksb':
#         nerscout, nerr = subprocess.Popen(['ssh','krisb@cori.nersc.gov', 'cd %s;ls -d $PWD/*/*'%sharedjobsNersc]
#                                     , stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate() # List of jobs in suncat stored jobs
#     else: nerscout = b''
#     sherout = os.popen('cd %s; ls -d $PWD/*/*'%sharedjobsSherlock).read() # List of jobs in sherlock stored jobs
#     nerscout = nerscout.decode(); suncout = suncout.decode() #convert from bytes to str
#     all_jobs_raw = itertools.chain.from_iterable([x.split('\n') for x in [sherout,suncout,nerscout]])
#
#     allJobs = [x+'/' for x in all_jobs_raw if len(x)>0]              # Merge lists, filter any '' items
#     newJobs = set(allJobs)-set(db.Query(table=job,db_path=db_path).query_col(job.storage_directory)) # Identify jobs not present already in database
#
#     if limit is not None: newJobs = list(newJobs)[:limit] # type: ignore
#     if newJobs:
#         print('adding %d new jobs'%len(newJobs))
#
#         for i,path in enumerate(newJobs):
#             if i%20: print(20-i%20)
#             else: print_sleep(1)
#             load_folder(path,db_path=db_path)
#
#         fill_comp(db_path=db_path)
#
#     else: print('No new jobs to add')
#
#
# ###################
# # Guessing Job Type
# # -----------------
# def guessJobType(vibpckls:list,qnlog:str) -> str:
#     """
#     Decide whether job is a vib job, a collection of singlepoints (e.g. bulkmod/latticeopt), or a relax
#     """
#     if len(vibpckls) > 0:                                  return 'vib'          # for vib, read INITIAL atoms from any .traj file (final doesn't matter)
#     else:
#         bfgs = qnlog.count('BFGS:')                                              # for bulkmod or lattice opt, read INITIAL atoms from any .traj file (accuracy here matters for bulkmod, not latticeopt)
#         if bfgs > 1 and bfgs==qnlog.count('BFGS:    0'):   return 'singlepoints' # possibly relax converges with single point, exclude these jobs (bulkmods and latticeopts take more than one singlepoint)
#         else:                                              return 'relax'        # includes vc-relax
#
# class Directory(object):
#     def __init__(self
#                 ,log    : str
#                 ,qnlog  : str
#                 ,pwinp  : str
#                 ,incar  : str
#                 ,kptcar  : str
#                 ,poscar  : str
#                 ,potcar  : str
#                 ,outcar  : str
#                 ,jsons  : list
#                 ,trajs  : list
#                 ,vibpckls  : list
#                 ) -> None:
#         self.log      = log
#         self.qnlog    = qnlog
#         self.pwinp    = pwinp
#         self.incar    = incar
#         self.kptcar   = kptcar
#         self.poscar   = poscar
#         self.potcar   = potcar
#         self.outcar   = outcar
#         self.jsons    = jsons
#         self.trajs    = trajs
#         self.vibpckls = vibpckls
#         self.jobtype  = guessJobType(vibpckls,qnlog)
#
# def get_files(storpth : str) -> Directory:
#     """
#     This function condenses most of the I/O into one step.
#         Grabs content of log file + pw.inp (if it exists)
#         Grabs the name of anything with a traj or json extension
#         Identifies whether or not there are vib.pckl files
#     """
#
#     storpth = replacer(storpth,{'/nfs/slac/g/suncatfs/ksb/share':'/scratch/users/ksb/share/suncat_jobs_copy'
#                                ,'/global/cscratch1/sd/krisb/share':'/scratch/users/ksb/share/nersc_jobs_copy'})
#
#     def get(x:str)->str:
#         try: return read_on_sher(storpth+x)
#         except Exception as e: return ''
#     def getGlob(x:str)->list: return glob.glob(storpth+x)
#     knownFiles = [get(x) for x in ['log','qn.log','pw.inp','INCAR','KPOINTS','POSCAR','POTCAR','OUTCAR']]
#     manyFiles  = map(getGlob,['*.json','*.traj','vib*.pckl'])
#     filtered   = [x for x in manyFiles if 'FW.json' not in x]
#
#     return Directory(*list(knownFiles + filtered)) # type: ignore
#
# def load_folder(storpath : str ,db_path : str = realdb)->None:
#     """
#     INPUT: a json of runtime data (generated by log()). OUTPUT: populates a new row of completed table
#     """
#     print('loading ',storpath)
#
#     direc   = get_files(storpath)
#
#     iID    = scrape.get_atoms_id(direc,True,db_path=db_path) # Assign IDs to init/final atoms. Add to DB if doesn't exist
#     fID    = scrape.get_atoms_id(direc,False,db_path=db_path) #
#     calcid = scrape.get_calc_id(direc,db_path=db_path)           # Assign IDs to calc params. Add to DB if doesn't exist
#
#     job_name = scrape.get_job_name(direc)
#     rawruntime = json.loads(read_on_sher(storpath+'runtime.json'))    # Runtime information
#     kwargs     = json.loads(rawruntime.pop('kwargs'))                    # Take kwargs and move to seperate object
#
#
#     if job_name is None:
#         job_name   = kwargs.get('job_name','')
#
#     runtime    = merge_dicts([rawruntime,{'calc_id': calcid
#                                         ,'initatoms':iID
#                                         ,'finalatoms':fID
#                                         ,'guess_jobtype':direc.jobtype
#                                         ,'job_name':job_name}])                                               # Look at *calc* table and get ID (if no matching calc exists, add a row to table)
#
#     colNames,binds = ','.join(runtime.keys()), list(runtime.values())                            # Runtime column names and corresponding values
#     command = 'INSERT into job (%s) VALUES (%s) '%( colNames, ','.join(['?']*len(binds)) ) # Make SQL command and
#     db.sqlexecute(command,binds,db_path=db_path) # type: ignore
