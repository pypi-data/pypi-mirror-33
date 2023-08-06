# External Modules
import os,shutil,getpass,time,sys,json

################################################################################
def safeMkdir(newDir): # type: ignore
    try:            os.makedirs(newDir)
    except OSError: pass # may fail due to multiple threads or already existing

def safeCopy(path,name): # type: ignore
    try:            shutil.copyfile(path,name)
    except IOError: pass

def clusterRoot(): # type: ignore
    hostname = os.environ['HOSTNAME'].lower()
    if      'sh'    in hostname or  'gpu-' in hostname:    return '/scratch/users/ksb/share/jobs'
    elif    'su'    in hostname:                           return '/nfs/slac/g/suncatfs/ksb/share/jobs'
    elif    'nid'   in hostname:                           return '/global/cscratch1/sd/krisb/share/jobs'
    else: raise ValueError

################################################################################

def log(**kwargs): # type: ignore
    """
    Execute at the end of all scripts. Copies info to external storage, where it should be added to a database
    """

    ######################################################
    print("Collecting environment data...")
    #-----------------------------------------------------
    public_storage    = clusterRoot()+'/'  # type: ignore

    user              = getpass.getuser()
    timestamp         = time.time()
    working_directory = os.getcwd()
    script            = sys.argv[0].split('/')[-1] # e.g. opt.py

    ######################################################
    print("Agglomerating data to be logged in database...")
    #-----------------------------------------------------
    newDir      = public_storage+'%s/%s/'%(user,str(timestamp).replace('.','')) #name of new directory

    allCols     = ['deleted','user',    'timestamp', 'working_directory','storage_directory','kwargs']
    binds       = [0,         user,  int(timestamp),  working_directory,  newDir,          json.dumps(kwargs)]
    runtime     = dict(zip(allCols,binds))

    #################################################
    print("Creating and Populating copy directory...")
    #------------------------------------------------
    safeMkdir(newDir) # type: ignore

    with open(newDir+'runtime.json','w') as f: f.write(json.dumps(runtime))       # Write runtime info to file

    for root, dirs, files in os.walk(working_directory, topdown=False):
        for name in files:
            originalPath = os.path.join(root, name)
            if  name == script:                           # uniform naming system for 'opt.py' script
                safeCopy(originalPath,newDir+'script.py') # type: ignore
            elif '.err' in name:                          # uniform naming system for error file
                safeCopy(originalPath,newDir+'myjob.err') # type: ignore
            elif '.out' in name:                          # uniform naming system from out file
                safeCopy(originalPath,newDir+'myjob.out') # type: ignore
            elif os.stat(originalPath).st_size < 1e9: safeCopy(originalPath,newDir+name)  # type: ignore

    os.system('chmod -R 755 %s'%newDir)

    return 0
