import pickle as pickle#External Modules
import os,json,glob
import fireworks # type: ignore
################################################################################

#################################
# Auxillary functions for scripts
#################################
def merge_dicts(listDicts):
    import itertools
    return dict(itertools.chain.from_iterable([x.items() for x in listDicts])) #presumes no overlap in keys

def get_cluster():
    import os
    hostname = os.environ['HOSTNAME'].lower()
    if  'sh'in hostname or  'gpu-' in hostname:
        sher = os.environ['SHERLOCK']
        if   sher == '1':  return 'sherlock'
        elif sher == '2': return 'sherlock2'
        else: raise ValueError('What cluster is this? '+sher)

    elif    'su'      in hostname: return 'suncat'
    elif    'nid'     in hostname: return 'nersc'
    else: raise ValueError("clusterRoot could not parse HOSTNAME: %s"%hostname)

def get_number_of_nodes():
    """
    Identify which parallel processor is executing this code
    """
    import os
    pwd = os.getcwd()

    if os.getenv('SHERLOCK')=='2':
        #On Sherlock 2
        with open('world.size','w') as f:
            number_of_nodes = int(os.getenv('SLURM_JOB_NUM_NODES'))
            f.write(str(number_of_nodes))
    elif '/nfs/slac/g/suncatfs' in pwd:
        with open('world.size','w') as f:
            procs = os.getenv('LSB_HOSTS').split()
            number_of_nodes = int(len(procs)/8)
            f.write(str(number_of_nodes))
    else:
        number_of_nodes = 1
    return number_of_nodes

def rank():
    """
    Identify which parallel processor is executing this code
    """
    import sys
    # Check for special MPI-enabled Python interpreters:
    if '_gpaw' in sys.builtin_module_names:
        import _gpaw  # type: ignore      # http://wiki.fysik.dtu.dk/gpaw
        world = _gpaw.Communicator()
    elif '_asap' in sys.builtin_module_names:
        import _asap # type: ignore    # http://wiki.fysik.dtu.dk/asap, can't import asap3.mpi here (import deadlock)
        world = _asap.Communicator()
    elif 'asapparallel3' in sys.modules: # type: ignore    # Older version of Asap
        import asapparallel3 # type: ignore
        world = asapparallel3.Communicator()
    elif 'Scientific_mpi' in sys.modules:
        from Scientific.MPI import world # type: ignore
    else:
        from ase.parallel import DummyMPI # type: ignore
        world = DummyMPI()# This is a standard Python interpreter:
    rank = world.rank #size = world.size

    return rank

#############################################
# Universally-applicable functions for scripts
#############################################

def write_script(listOfFuncs,mainFunc):
    """
    Takes a list of functions and writes them to script.py
    One function is specified as the function called by __main__
    """
    import inspect

    with open('script.py','w') as f:
        for fnc in listOfFuncs:
            f.write('\n\n'+inspect.getsource(fnc))
        f.write("\n\nif __name__ == '__main__': %s()\n\n"%mainFunc.__name__)

    os.system('chmod 755 script.py')


def writeMetaScript(dftcode):
    if dftcode == 'gpaw':
        script = """#!/bin/bash
# Slurm parameters
NTASKS=`echo $SLURM_TASKS_PER_NODE|tr '(' ' '|awk '{print $1}'`
NNODES=`scontrol show hostnames $SLURM_JOB_NODELIST|wc -l`
NCPU=`echo " $NTASKS * $NNODES " | bc`
# load gpaw-specific paths
source /scratch/users/ksb/gpaw/paths.bash
# run parallel gpaw
mpirun -n $NCPU gpaw-python script.py"""

    elif dftcode == 'quantumespresso':
        script = """#!/bin/bash\npython2 script.py"""

    with open('metascript.sh','w') as f: f.write(script)

    os.system('chmod 755 metascript.sh')


def initialize():
    """
    Does three things to initialize (any) job:
        1. Delete old error and output files for restarted jobs
        2. Load job input parameters
        3. Write initial Atoms object to init.traj
    """
    import json,os,glob
    import ase.io as aseio # type: ignore
    import ase.parallel as asepar # type: ignore

    def keepNewest(string):                 # Step 1
        listPth = glob.glob(string)
        ordered = sorted([(os.path.getmtime(pth),pth) for pth in listPth])
        for t,pth in ordered[:-1]:
            os.remove(pth)

    if rank()==0:
        keepNewest('*.error')
        keepNewest('*.out')

    try:   os.remove('result.json')
    except OSError: pass
    try:   os.remove('runtime.json')
    except OSError: pass

    with asepar.paropen('params.json','r') as f: prms  = json.loads(f.read())    # Step 2
    atoms   = make_atoms(prms)
    atoms.set_pbc([1,1,1])

    aseio.write('init.traj',atoms)         # Step 3

    return prms,atoms

###########################
# Atoms object manipulation
###########################

def traj_to_json(atoms):
    """
    Serialize an Atoms object in a human readable way
    """
    import ase, json
    def roundfloat(x):
        output =  round(float(x),3)
        return abs(output) if  output == 0 else output
    atomdata = []
    const    = atoms.constraints
    if const: const_list = const[0].get_indices().tolist()
    else:     const_list = []

    atoms.wrap()
    for a in atoms: atomdata.append({'number'		: int(a.number)
                                    ,'x'			: roundfloat(a.x)
                                    ,'y'			: roundfloat(a.y)
                                    ,'z'			: roundfloat(a.z)
                                    ,'magmom'		: roundfloat(a.magmom)
                                    ,'tag'			: int(a.tag)
                                    ,'constrained'	: int(a.index in const_list)
                                    ,'index'		: int(a.index)})

    out = {'cell': [[roundfloat(x) for x in xx] for xx in atoms.get_cell().tolist()]
          ,'atomdata':atomdata}

    return json.dumps(out)


def json_to_traj(raw_json):
    """
    Inverse of traj_to_json
    """
    from ase.constraints import FixAtoms
    import numpy as np
    import ase, json

    raw_atoms = json.loads(raw_json)
    try:
        atom_data = raw_atoms['atom_data']
    except KeyError:
        atom_data = raw_atoms['atomdata']

    pos = np.array([[a[q] for a in atom_data] for q in ['x','y','z']]).T

    fix = FixAtoms([a['index'] for a in atom_data if a['constrained']])

    atoms = ase.Atoms(numbers     = [a['number'] for a in atom_data]
                     ,cell        = raw_atoms['cell']
                     ,positions   = pos
                     ,magmoms     = [a['magmom'] for a in atom_data]
                     ,tags        = [a['tag'] for a in atom_data]
                     ,constraint  = fix)
    return atoms

def make_atoms(params):
    import pickle as pickle # type: ignore
    try:
        return json_to_traj(params['inittraj'])
    except KeyError:
        return pickle.loads(str(params['inittraj_pckl']))


def cellpar_to_cell(cellpar, ab_normal=(0, 0, 1), a_direction=None):
    """Return a 3x3 cell matrix from cellpar=[a,b,c,alpha,beta,gamma]. Angles must be in degrees.
    The returned cell is orientated such that a and b are normal to `ab_normal` and a is parallel to the projection of `a_direction` in the a-b plane.
    Default `a_direction` is (1,0,0), unless this is parallel to `ab_normal`, in which case default `a_direction` is (0,0,1).
    The returned cell has the vectors va, vb and vc along the rows. The cell will be oriented such that va and vb are normal to `ab_normal` and va will be along the projection of `a_direction` onto the a-b plane.
    """
    import numpy as np # type: ignore
    from numpy import pi, sin, cos, arccos, sqrt, dot
    def unit_vector(x): #Return a unit vector in the same direction as x.
        y = np.array(x, dtype='float')
        return y / np.linalg.norm(y)
    if a_direction is None:
        if np.linalg.norm(np.cross(ab_normal, (1, 0, 0))) < 1e-5: a_direction = (0, 0, 1)
        else: a_direction = (1, 0, 0)
    ad = np.array(a_direction) # Define rotated X,Y,Z-system, with Z along ab_normal and X along
    Z = unit_vector(ab_normal) # the projection of a_direction onto the normal plane of Z.
    X = unit_vector(ad - dot(ad, Z) * Z)
    Y = np.cross(Z, X)
    # Express va, vb and vc in the X,Y,Z-system
    alpha, beta, gamma = 90., 90., 90.
    if isinstance(cellpar, (int, float)): a = b = c = cellpar
    elif len(cellpar) == 1:     a = b = c = cellpar[0]
    elif len(cellpar) == 3: a, b, c = cellpar
    else:  a, b, c, alpha, beta, gamma = cellpar
    # Handle orthorhombic cells separately to avoid rounding errors
    eps = 2 * np.spacing(90.0, dtype=np.float64)  # around 1.4e-14
    if abs(abs(alpha) - 90) < eps: cos_alpha = 0.0 # alpha
    else:  cos_alpha = cos(alpha * pi / 180.0)
    if abs(abs(beta) - 90) < eps: cos_beta = 0.0 # beta
    else: cos_beta = cos(beta * pi / 180.0)
    if abs(gamma - 90) < eps: # gamma
        cos_gamma,sin_gamma = 0.0,1.0
    elif abs(gamma + 90) < eps:
        cos_gamma,sin_gamma = 0.0,-1.0
    else:
        cos_gamma = cos(gamma * pi / 180.0)
        sin_gamma = sin(gamma * pi / 180.0)
    va = a * np.array([1, 0, 0]) # Build the cell vectors
    vb = b * np.array([cos_gamma, sin_gamma, 0])
    cx = cos_beta
    cy = (cos_alpha - cos_beta * cos_gamma) / sin_gamma
    cz = sqrt(1. - cx * cx - cy * cy)
    vc = c * np.array([cx, cy, cz])
    abc = np.vstack((va, vb, vc)) # Convert to the Cartesian x,y,z-system
    T = np.vstack((X, Y, Z))
    return dot(abc, T) #cell

def makeCalc(p):
    """Make a relaxation calculator for GPAW/QE given input parameters"""
    import json

    def makeGPAWcalc():
        from gpaw import (GPAW,PW,Davidson,Mixer,MixerSum,FermiDirac,setup_paths,PoissonSolver) # type: ignore

        if p['psp'] == 'oldpaw':
            setup_paths.insert(0, '/scratch/users/ksb/gpaw/oldpaw/gpaw-setups-0.6.6300/')
            psp = 'paw'
        else: psp = p['psp']

        if p['spinpol'] or p['hund']:
            mixer = MixerSum(beta=p['mixing'],nmaxold=p['nmix'],weight=100)
        else:
            mixer = Mixer(beta=p['mixing'],nmaxold=p['nmix'],weight=100)

        if p['hund']:
            occupations   = FermiDirac(0.01,fixmagmom=True)
            poissonsolver = None # broken??? PoissonSolver(eps=1e-12)
        else:
            occupations   = FermiDirac(p['sigma'])
            poissonsolver = None

        return GPAW(mode         = PW(p['pw'],force_complex_dtype=p['hund'])
                    ,xc          = p['xc']
                    ,kpts        = p['kpts']
                    ,spinpol     = p['spinpol']
                    ,convergence = {'energy':p['econv']} #eV/electron
                    ,mixer       = mixer
                    ,maxiter       = p['maxstep']
                    ,nbands        = p['nbands']
                    ,occupations   = occupations
                    ,setups        = psp
                    ,eigensolver   = 'rmm-diis' if p['hund'] else Davidson(5)
                    ,poissonsolver = poissonsolver
                    ,hund          = p['hund']
                    ,txt           = 'log'
                    ,symmetry      = 'off')

    def makeQEcalc():
        import json
        from espresso import espresso # type: ignore

        pspDict =   {'sherlock' : {'gbrv15pbe':'/home/vossj/suncat/psp/gbrv1.5pbe'}
                    ,'sherlock2': {'gbrv15pbe':'/home/users/vossj/suncat/psp/gbrv1.5pbe'}
                    ,'suncat'   : {'gbrv15pbe':'/nfs/slac/g/suncatfs/sw/external/esp-psp/gbrv1.5pbe'}}
        pspPath =  pspDict[get_cluster()][p['psp']]
        number_of_nodes = get_number_of_nodes()
        return espresso( pw         = p['pw']
                        ,dw         = p['dw']
                        ,xc         = p['xc']
                        ,kpts       = p['kpts']
                        ,spinpol    = p['spinpol']
                        ,convergence=   {'energy':      p['econv']
                                        ,'mixing':      p['mixing']
                                        ,'mixing_mode': p['mixingtype']
                                        ,'nmix':        p['nmix']
                                        ,'maxsteps':    p['maxstep']
                                        ,'diag':        'david'}
                        ,nbands            = p['nbands']
                        ,sigma             = p['sigma']
                        ,dipole            = {'status': p['dipole']}
                        ,outdir            = 'calcdir'
                        ,startingwfc       = 'atomic+random'
                        ,tot_magnetization = 'hund' if p['hund'] else -1
                        ,nspin             = -2 if p['hund'] else None
                        ,psppath           = pspPath
                        ,parflags          = '-npool {}'.format(number_of_nodes)
                        ,mode              = 'scf'
                        ,output     = {'removesave':True})

    if   p['dftcode']=='gpaw': return makeGPAWcalc()
    else:                      return makeQEcalc()

def makeQEVCcalc(p):
    import json
    from espresso import espresso # type: ignore
    pspDict =   {'sherlock': {'gbrv15pbe':'/home/vossj/suncat/psp/gbrv1.5pbe'}
                ,'sherlock2': {'gbrv15pbe':'/home/users/vossj/suncat/psp/gbrv1.5pbe'}
                ,'suncat':   {'gbrv15pbe':'/nfs/slac/g/suncatfs/sw/external/esp-psp/gbrv1.5pbe'}}
    pspPath =  pspDict[get_cluster()][p['psp']]
    number_of_nodes = get_number_of_nodes()
    return  espresso( pw            = p['pw']
                    ,dw             = p['dw']
                    ,xc             = p['xc']
                    ,kpts           = p['kpts']
                    ,nbands         = p['nbands']
                    ,dipole         = {'status': p['dipole']}
                    ,sigma          = p['sigma']
                    ,mode           = 'vc-relax'
                    ,cell_dynamics  = 'bfgs'
                    ,opt_algorithm  = 'bfgs'
                    ,cell_factor    = p['cell_factor']
                    ,cell_dofree    = p['cell_dofree']
                    ,spinpol        = p['spinpol']
                    ,outdir         = 'calcdir'
                    ,output         = {'removesave':True}
                    ,psppath        = pspPath
                    ,parflags       = '-npool {}'.format(number_of_nodes)
                    ,convergence    =   {'energy':  p['econv']
                                        ,'mixing':  p['mixing']
                                        ,'nmix':    p['nmix']
                                        ,'maxsteps':p['maxstep']
                                        ,'diag':    'david'})


def makeQEvibcalc(p):
    import json
    from espresso.vibespresso import vibespresso # type: ignore

    pspDict =   {'sherlock': {'gbrv15pbe':'/home/vossj/suncat/psp/gbrv1.5pbe'}
                ,'sherlock2': {'gbrv15pbe':'/home/users/vossj/suncat/psp/gbrv1.5pbe'}
                ,'suncat':   {'gbrv15pbe':'/nfs/slac/g/suncatfs/sw/external/esp-psp/gbrv1.5pbe'}}
    pspPath =  pspDict[get_cluster()][p['psp']] #this must be done here because we don't know what cluster job will be run on
    number_of_nodes = get_number_of_nodes()
    return vibespresso( pw           = p['pw']
                        ,dw          = p['dw']
                        ,xc          = p['xc']
                        ,kpts        = p['kpts']
                        ,spinpol     = p['spinpol']
                        ,dipole      = {'status': p['dipole']}
                        ,convergence =   {'energy':  p['econv']
                                         ,'mixing':  p['mixing']
                                         ,'nmix':    p['nmix']
                                         ,'maxsteps':p['maxstep']
                                         ,'diag':    'david'}
                        ,nbands      = p['nbands']
                        ,sigma       = p['sigma']
                        ,outdir      = 'calcdir'
                        ,startingwfc = 'atomic+random'
                        ,psppath     = pspPath
                        ,parflags    = '-npool {}'.format(number_of_nodes)
                        ,output      = {'removesave':True,'wf_collect':False})

def makeQEnebCalc(p):
    import json
    from espresso.multiespresso import multiespresso # type: ignore
    pspDict =   {'sherlock': {'gbrv15pbe':'/home/vossj/suncat/psp/gbrv1.5pbe'}
                ,'sherlock2': {'gbrv15pbe':'/home/users/vossj/suncat/psp/gbrv1.5pbe'}
                ,'suncat':   {'gbrv15pbe':'/nfs/slac/g/suncatfs/sw/external/esp-psp/gbrv1.5pbe'}}
    pspPath =  pspDict[get_cluster()][p['psp']] #this must be done here because we don't know what cluster job will be run on

    return multiespresso(ncalc        = p['images']
                        ,outdirprefix ='neb'
                        ,pw           = p['pw']
                        ,dw           = p['dw']
                        ,xc           = p['xc']
                        ,kpts         = p['kpts']
                        ,spinpol      = p['spinpol']
                        ,dipole       = {'status': p['dipole']}
                        ,sigma        = p['sigma']
                        ,nbands       = p['nbands']
                        ,psppath      = pspPath
                		,output       = {'avoidio':False,
                                         'removewf':True,
                                         'wf_collect':False}
                        ,convergence  =  {'energy':  p['econv']
                                         ,'mixing':  p['mixing']
                                         ,'nmix':    p['nmix']
                                         ,'mixing_mode': p['mixingtype']
                                         ,'maxsteps':p['maxstep']
                                         ,'diag':    'david'} )

def cFunc(prms):
    """
    Selects the appropriate calculator-making function given
    properties of the parameter dictionary
    """
    dftcode,jobkind =prms['dftcode'],prms['jobkind']
    relax = prms['jobkind'] in ['latticeopt','relax','bulkmod','fbl','xc']
    if relax :                return makeCalc
    elif jobkind =='vcrelax': return makeQEVCcalc
    elif jobkind == 'vib':    return makeQEvibcalc
    elif jobkind == 'neb':    return makeQEnebCalc
    else: NotImplementedError('jobkind {} has no calculator function'.format(jobkind))


def optimize_pos(atoms,calc,fmax, restart = 'qn.pckl'):
    import ase.optimize as aseopt # type: ignore

    atoms.set_calculator(calc)
    dyn = aseopt.BFGS(atoms=atoms, logfile='qn.log', trajectory='qn.traj',restart = restart)
    dyn.run(fmax=fmax)

def traj_details(atoms):
    """ Returns dictionary summary of an (optimized) Atoms object """
    import pickle as pickle # type: ignore
    import numpy as np # type: ignore

    try: mag = atoms.get_magnetic_moments()
    except: mag = np.array([0]*len(atoms))
    return {'finaltraj':traj_to_json(atoms)
            ,'finalpos_pckl':pickle.dumps(atoms.get_positions())
            ,'finalcell_pckl':pickle.dumps(atoms.get_cell())
            ,'finalmagmom_pckl':pickle.dumps(mag)}

def log(params):
    """
    Execute at the end of all scripts. Copies info to external storage, where it should be added to a database
    """
    import os,shutil,getpass,time,sys,json
    kwargs = json.loads(params.get('kwargs','{}'))

    #####################
    # Auxillary functions
    #--------------------
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
############################
############################
# JobKind-specific functions
############################
############################

###########################
# OptimizeLattice functions
###########################

def OptimizeLatticeScript():
    import pickle as pickle
    import json,os,ase,shutil
    import scipy.optimize as opt    # type: ignore
    import ase.parallel   as asepar # type: ignore

    global energies,lparams

    #######################
    print("Initializing...")
    #----------------------
    params,initatoms = initialize()      # Remove old .out/.err files, load from fw_spec, and write 'init.traj'
    shutil.copy('init.traj','out.traj')  # Initial guess for atomic coordinates inside get_bulk_energy reads from 'out.traj'
    energies,lparams = [],[]             # type: ignore

    if rank()==0:
        for d in ['qn.traj','qn.log','lattice_opt.log','energy_forces.pckl']:          # Remove partially completed calculations that may still be held over from failed job
            if os.path.exists(d): os.remove(d)
            print('Removed existing file ',d)

    ################################
    print("Loading initial guess...")
    #-------------------------------

    try:
        with asepar.paropen('lastguess.json','r') as f: iGuess = json.loads(f.read())
        print('\tread lastguess from lastguess.json: ',iGuess)
    except:
        iGuess = get_init_guess(params['structure'],initatoms.get_cell())
        print('\tgenerating initial guess from get_init_guess(): ',iGuess)

    ########################################
    print("Optimizing cell and positions...")
    #---------------------------------------
    optimizedLatticeParams  = opt.fmin(get_bulk_energy,iGuess,args=(params,),ftol=1,xtol=params['xtol'])
    print('Optimized lattice params: ',optimizedLatticeParams)

    ################################
    print("Storing Results...")
    #-------------------------------

    if rank() == 0:
        optAtoms    = ase.io.read('out.traj') #read optimized cell and positions
        with open('energy_forces.pckl') as f: eng,forces=pickle.loads(str(f.read()))
        resultDict  = merge_dicts([params,traj_details(optAtoms)
                                ,{'raw_energy':     eng
                                ,'forces_pckl':     pickle.dumps(forces)
                                ,'latticeopt_pckl': pickle.dumps(zip(energies,lparams))}])

        with open('result.json', 'w') as f: f.write(json.dumps(resultDict))
        log(params)
    return 0

def get_init_guess(structure,cell):
    """
    Convert cell into parameters a,b,c,alpha,beta,gamma
    Depending on structure, return sufficient information required to reconstruct cell (e.g. only 'a' is needed if the structure is known cubic)
    """
    import numpy as np # type: ignore

    def angle(v1,v2): return np.arccos(np.dot(v1,np.transpose(v2))/(np.linalg.norm(v1)*np.linalg.norm(v2)))
    a,b,c            = np.linalg.norm(cell[0]),np.linalg.norm(cell[1]),np.linalg.norm(cell[2])
    alpha,beta,gamma = angle(cell[1],cell[2]), angle(cell[0],cell[2]), angle(cell[0],cell[1])

    if   structure in ['fcc','bcc','fcc-unit','bcc-unit','rocksalt','cubic','diamond','cscl','zincblende','rocksalt-unit','zincblende-unit','M3N-unit','antibixbyite']: return [a]
    elif structure in ['hexagonal','hcp','Li3N']: return [a,c]
    elif structure in ['triclinic']: return [a,b,c,alpha,beta,gamma]
    else: raise ValueError('Bad entry in "structure" field for Atoms object info dictionary: '+structure)

def get_bulk_energy(latticeParams,params):
    #For a given set of bravais lattice parameters, optimize atomic coordinates and return minimum energy
    import pickle as pickle
    import ase,json # type: ignore
    import ase.parallel as asepar # type: ignore
    import ase.io as aseio # type: ignore
    global energies,lparams

    with asepar.paropen('lastguess.json','w') as f: f.write(json.dumps(list(latticeParams)))
    atomsInitUnscaled = make_atoms(params)
    atoms = from_params(atomsInitUnscaled,latticeParams,params['structure'])
    optimize_pos(atoms,makeCalc(params),params['fmax'])
    energy,forces = atoms.get_potential_energy(),atoms.get_forces()
    energies.append(energy);lparams.append(latticeParams)
    with asepar.paropen('lattice_opt.log','a') as logfile: logfile.write('%s\t%s\n' %(energy,latticeParams))
    aseio.write('out.traj',atoms)
    with open('energy_forces.pckl','w') as f: f.write(pickle.dumps((energy,forces)))
    return energy

def from_params(atomsInput,cellParams,structure):
    """
    Params is a list of 1 to 6 numbers (a,b,c,alpha,beta,gamma).
    ANGLES OF INPUT ARE IN RADIANS, ASE CELLS WANT ANGLES IN DEGREES
    Depending on structure, we can construct the cell from a subset of these parameters
    """
    import math     as m

    a = cellParams[0]
    if   structure in ['cubic','cscl','fcc-unit','bcc-unit','zincblende-unit','rocksalt-unit','M3N-unit','antibixbyite']:  cell = [a,a,a,90,90,90]
    elif structure in ['fcc','diamond','zincblende','rocksalt']: cell = [a,a,a,60,60,60]
    elif structure in ['bcc']:                                   cell = [a,a,a,109.47122,109.47122,109.47122]
    elif structure in ['hcp','hexagonal','Li3N']:                       cell = [a,a,cellParams[1],90,90,120]                                                                                          # Input is assumed to be two parameters, a and c
    elif structure in ['triclinic']:                             cell = [cellParams[0],cellParams[1],cellParams[2],m.degrees(cellParams[3]),m.degrees(cellParams[4]),m.degrees(cellParams[5])] # You should really be using VC relax for this....
    else: raise NotImplementedError('from_params(atomsInput,cellParams,structure) cannot handle unknown structure = '+structure)
    atoms = atomsInput.copy()
    atoms.set_cell(cellpar_to_cell(cell),scale_atoms=True)

    return atoms

###########################
# BulkModulus functions
###########################
def BulkModulusScript():
    import json,base64,copy,os
    import ase,matplotlib # type: ignore
    import numpy        as np # type: ignore
    import ase.eos      as aseeos # type: ignore
    import ase.parallel as asepar # type: ignore
    matplotlib.use('Agg')
    #######################
    print("Initializing...")
    #----------------------

    params,optAtoms = initialize()  # Remove old .out/.err files, load from fw_spec, and write 'init.traj'

    optCell,vol,eng = optAtoms.get_cell() , [],[]
    strains         = np.linspace(1 - params['strain'],1 + params['strain'],9)

    if rank()==0:
        for d in ['qn.traj','qn.log']:          # Remove partially completed calculations that may still be held over from failed job
            if os.path.exists(d): os.remove(d)
            print('Removed existing file ',d)

    ##################################################
    print("Calculating energies at various strains...")
    #-------------------------------------------------

    for i, strain in enumerate(strains):
        atoms = optAtoms.copy()
        atoms.set_cell(optCell*strain,scale_atoms=True)
        optimize_pos(atoms,makeCalc(params),params['fmax'])

        volume,energy = atoms.get_volume(),atoms.get_potential_energy()
        vol.append(copy.deepcopy(volume));eng.append(copy.deepcopy(energy))

    ################################
    print("Analyzing dE/dV curve...")
    #-------------------------------

    aHat,quadR2 = quad_fit(np.array(copy.deepcopy(vol)),np.array(copy.deepcopy(eng)))

    try:
        eos = aseeos.EquationOfState(vol,eng)
        v0, e0, b = eos.fit()
        eos.plot(filename='bulk-eos.png',show=False)
        b0= b/ase.units.kJ*1e24                                     #GPa: use this value if EOS doesn't fail
        with open('bulk-eos.png', 'rb') as f: img = base64.b64encode(f.read())

    except ValueError:                                  # too bad of a fit for ASE to handle
        b0 = aHat*2*vol[4]*160.2                        # units: eV/A^6 * A^3 * 1, where 1 === 160.2 GPa*A^3/eV
        img = None

    ################################
    print("Storing Results...")
    #-------------------------------

    resultDict  = merge_dicts([params,traj_details(optAtoms)
                                ,{'bulkmod':b0,'bfit':quadR2,'bulkmodimg_base64':img,'voleng_json':json.dumps(zip(vol,eng))}])

    with open('result.json', 'w') as outfile:   outfile.write(json.dumps(resultDict))

    if rank()==0: log(params)
    return 0

def quad_fit(xIn,yIn):
    """ Input x vector: units A^3, Input y vector: units eV """
    import numpy            as np # type: ignore
    import scipy.optimize   as opt # type: ignore

    # Center data around 4th data point
    x = xIn-xIn[4]; y = yIn-yIn[4]
    def model(a):  return a*np.square(x)
    def errVec(a): return a*np.square(x) - y   #create fitting function of form mx+b
    aHat, success = opt.leastsq(errVec, [0.1])
    yhat    = model(aHat)
    ybar    = np.sum(y)/len(y)          # or sum(y)/len(y)
    ssresid = np.sum((yhat-y)**2)
    sstotal = np.sum((y - ybar)**2)    # or sum([ (yi - ybar)**2 for yi in y])
    r2      = 1 - (ssresid / float(sstotal)) #
    return float(aHat[0]),float(r2)

###########################
# XC Contribs functions
##########################
def XCcontribsScript():
    import json,ase,copy # type: ignore
    from gpaw        import restart # type: ignore
    from gpaw.xc.bee import BEEFEnsemble # type: ignore
    params,atoms = initialize()  # Remove old .out/.err files, load from fw_spec, and write 'init.traj'
    pbeParams = copy.deepcopy(params)
    pbeParams['xc']='PBE'
    atoms.set_calculator(makeCalc(pbeParams))
    atoms.get_potential_energy()
    atoms.calc.write('inp.gpw', mode='all')

    atoms,calc = restart('inp.gpw', setups='sg15', xc='mBEEF'
                            , convergence={'energy': 5e-4}, txt='mbeef.txt')
    atoms.get_potential_energy()
    beef        = BEEFEnsemble(calc)
    xcContribs  = beef.mbeef_exchange_energy_contribs()
    ################################
    print("Storing Results...")
    #-------------------------------
    ase.io.write('final.traj',atoms)
    resultDict  = merge_dicts([params,traj_details(ase.io.read('final.traj'))
                                ,{'xc_contribs': xcContribs.tolist()}])
    with open('result.json', 'w') as outfile:   outfile.write(json.dumps(resultDict))
    if rank()==0: log(params)
    return 0

#################
# Relax functions
#################

def RelaxScript():
    import pickle as pickle
    import ase,json,os # type: ignore
    import ase.parallel   as asepar # type: ignore

    #######################
    print("Initializing...")
    #----------------------

    params,initatoms = initialize()  # Remove old .out/.err files, load from fw_spec, and write 'init.traj'

    if rank()==0:
        if os.path.exists('qn.traj'):
            if os.stat('qn.traj').st_size > 100:
                initatoms = ase.io.read('qn.traj')
                print('\treading from qn.traj...')
            else:
                os.remove('qn.traj')
                print('removed empty qn.traj')
        if os.path.exists('qn.log') and os.stat('qn.log').st_size < 100:
            os.remove('qn.log')
            print('\tremoved empty qn.log...')

    #######################
    print("Optimizing positions...")
    #----------------------
    optimize_pos(initatoms,makeCalc(params),params['fmax'])

    ############################
    print("Storing Results...")
    #--------------------------
    ase.io.write('final.traj',initatoms)
    e0 = initatoms.get_potential_energy()
    f0 = initatoms.get_forces()
    optAtoms = ase.io.read('final.traj')
    resultDict  = merge_dicts([params,traj_details(optAtoms)
                                ,{'raw_energy': e0
                                ,'forces_pckl':pickle.dumps(f0)} ])

    with open('result.json', 'w') as f: f.write(json.dumps(resultDict))
    if rank()==0: log(params)
    return 0


#####################
# Vibration Functions
#####################
def VibScript():
    from ase.vibrations       import Vibrations # type: ignore
    import pickle as pickle
    import glob,json,ase,os # type: ignore

    #######################
    print("Initializing...")
    #----------------------

    params,atoms = initialize()  # Remove old .out/.err files, load from fw_spec, and write 'init.traj'

    prev = glob.glob('*.pckl') #delete incomplete pckls - facilitating restarted jobs

    if rank()==0:
        for p in prev:
            if os.stat(p).st_size < 100: os.remove(p)

    atoms.set_calculator(makeQEvibcalc(params))
    vib = Vibrations(atoms,delta=params['delta'],indices=json.loads(params['vibids']))

    vib.run(); vib.write_jmol()

    ##########################
    print("Storing Results...")
    #-------------------------

    vib.summary(log='vibrations.txt')

    with open('vibrations.txt','r') as f: vibsummary = f.read()

    ase.io.write('final.traj',atoms)
    optAtoms = ase.io.read('final.traj')

    vib_energies,vib_frequencies = vib.get_energies(),vib.get_frequencies()

    resultDict  = merge_dicts([params,  traj_details(optAtoms),{'vibfreqs_pckl': pickle.dumps(vib_frequencies)
                                        ,'vibsummary':vibsummary
                                        ,'vibengs_pckl':pickle.dumps(vib_energies)}])

    with open('result.json', 'w') as outfile:   outfile.write(json.dumps(resultDict))
    with open('result.json', 'r') as outfile: json.loads(outfile.read()) #test that dictionary isn't 'corrupted'
    if rank()==0: log(params)
    return 0


#####################
# VCRelax Functions
#####################

def VCRelaxScript():
    import ase,json,pickle,os # type: ignore
    #######################
    print("Initializing...")
    #----------------------
    params,atoms = initialize()  # Remove old .out/.err files, load from fw_spec, and write 'init.traj'

    if not os.path.exists('intermediate.traj'):
        ##########################################
        print("Running VC Relax for first time...")
        #-----------------------------------------
        atoms.set_calculator(makeQEVCcalc(params))
        energy = atoms.get_potential_energy()   # Trigger espresso to be launched
        ase.io.write('intermediate.traj',atoms.calc.get_final_structure())

    ###########################################
    print("Running VC Relax for second time...")
    #------------------------------------------
    atoms = ase.io.read('intermediate.traj')
    atoms.set_calculator(makeQEVCcalc(params))
    energy = atoms.get_potential_energy() #trigger espresso to be launched
    ase.io.write('final.traj',atoms.calc.get_final_structure())

    ################################
    print("Storing Results...")
    #-------------------------------
    e0,f0   = atoms.get_potential_energy(),atoms.get_forces()
    atoms   = ase.io.read('final.traj')

    resultDict  = merge_dicts([params,traj_details(atoms),
                                {'raw_energy':  e0
                                ,'forces_pckl': pickle.dumps(f0)}])

    with open('result.json', 'w') as outfile:   outfile.write(json.dumps(resultDict))
    with open('result.json', 'r') as outfile: json.loads(outfile.read()) #test that dictionary isn't 'corrupted'
    if rank()==0: log(params)
    return 0

#####################
# FBL Script
#####################

def FBLScript():
    import ase,json,base64,copy,os,matplotlib, fnmatch # type: ignore
    import numpy        as np # type: ignore
    from ase.constraints import FixBondLength # type: ignore
    import pickle
    matplotlib.use('Qt5Agg')
    #######################
    print("Initializing...")
    #----------------------

    params,optAtoms = initialize()  # Remove old .out/.err files, load from fw_spec, and write 'init.traj'

    #Check for work that has already been done will use the last completed step as starting point
    step = 0
    if rank() == 0:
        step_files = fnmatch.filter(os.walk('.').next()[2], 'step_*_.traj')
        if not step_files == []:
            step_list = sorted(map(lambda x: int(x.split('_')[1]),step_files), reverse = True)
            for step in step_list:
                try:
                    optAtoms = ase.io.read('step_{0}_.traj'.format(step))
                    step += 1
                    print("Restarting at step {0}".format(step))
                    break
                except:
                    pass

    #Initialize the energy_cut_off of steps and step size
    energy_cut_off  = params['energy_cut_off']
    step_size       = params['step_size']
    fix             = params['fix'] if fix in params.keys() else 0.5

    #Initialize bond distance and fix the bond length
    bonded_inds = json.loads(params['bonded_inds'])
    optAtoms.set_constraint(optAtoms.constraints+[FixBondLength(*bonded_inds)])


    d_init, energy_array, atoms_array = optAtoms.get_distance(*bonded_inds), [], []
    if step == 0:
        print("Starting with inittraj_pckl, bond distance = {0}".format(d_init))
        d_array = [d_init]
    else:
        d_init += -step_size
        print("Beginning with bond distance = {0}".format(d_init))
        complete_steps = np.arange(0,step)
        atoms_array += map(lambda x: ase.io.read('step_{0}_.traj'.format(x)),complete_steps)
        energy_array += map(lambda x: x.get_potential_energy(),atoms_array)
        d_array = map(lambda x: x.get_distance(*bonded_inds),atoms_array)

    #Create the rest of the bond distance array that will be iterated through
    d_array += sorted(np.arange(0.3,(np.floor((d_init)/step_size)*step_size+0.01),step_size),reverse=True)

    if rank()==0:
        for d in ['qn.traj','qn.log']:          # Remove partially completed calculations that may still be held over from failed job
            if os.path.exists(d): os.remove(d)
            print('Removed existing file ',d)

    ##################################################
    print("Reducing the bond distance and relaxing atoms")
    #-------------------------------------------------
    if round(d_init,1) == 0.2:
        print('Bond distance already at or below 0.3 Angstrom, no additional steps will be taken')
    else:
        atoms = optAtoms.copy()
        for d_curr in d_array[step:]:
            step_curr = d_array.index(d_curr)
            if step_curr>0 and energy_array[-1]-energy_array[0]>energy_cut_off:
                d_array = d_array[:step_curr]
                print('Energy cutoff hit at step {0}'.format(step_curr))
                break
            atoms.set_distance(*bonded_inds,distance = d_curr, fix = 0.5)
            optimize_pos(atoms,makeCalc(params),params['fmax'], restart = None)
            ase.io.write('step_{0}_.traj'.format(step_curr),atoms)
            atoms_array.append(atoms.copy())
            energy_array.append(atoms.get_potential_energy())
            print('Step {0} completed: Energy = {1}; Bond Distance = {2}'.format(step_curr, energy_array[-1], atoms.get_distance(*bonded_inds)))

    ################################
    print("Analyzing energy vs bond length curve...")
    #-------------------------------
    d_array.reverse(); energy_array.reverse(); atoms_array.reverse()
    TS_step, TS_dis, TS_energy, TS_atoms, TS_barrier, rxn_energy = get_FBL_TS_energy(d_array, energy_array, atoms_array)
    img = FBL_plotter(d_array, energy_array, TS_step = TS_step)

    ################################
    print("Storing Results...")
    #-------------------------------
    ase.io.write('TS.traj',TS_atoms)
    fbl_dict = {'fbl_barrier':TS_barrier,'rxn_energy':rxn_energy
                ,'TS_bond_length':TS_dis,'TS_atoms': pickle.dumps(TS_atoms)
                ,'TS_energy':TS_energy,'fblimg_base64':img}
    resultDict  = merge_dicts([params,traj_details(TS_atoms), fbl_dict,])

    with open('result.json', 'w') as outfile:   outfile.write(json.dumps(resultDict))

    if rank()==0: log(params)
    return 0

def get_FBL_TS_energy(d_list, e_list, atoms_list, min_d = 0.7):
    from scipy.interpolate import CubicSpline # type: ignore
    import numpy as np # type: ignore
    from copy import deepcopy

    d_list =deepcopy(d_list); e_list = deepcopy(e_list); atoms_list = deepcopy(atoms_list)

    #Fit data to a cubic spline for more precise identification of peak
    cs = CubicSpline(d_list,e_list)
    xs = np.arange(min(d_list),max(d_list),0.01)
    diff_e = np.diff(cs(xs))

    #Find peaks from instanteous slopes in the cubic spline fit
    peaks = []
    for i, slope in enumerate(diff_e>0):
        if i< len(diff_e)-1:
            if slope and not diff_e[i+1]>0:
                peaks.append(i+1)

    #Identify the TS as the step with the closest energy to the peak energy
    if peaks == []:
        max_peak_ind = np.argmax(cs(xs))
    else:
        max_peak_ind = peaks[np.argmax([cs(xs)[i] for i in peaks])]

    TS_step = np.argmin(abs(xs[max_peak_ind]-d_list))

    #Store the data for the transition state
    TS_atoms = atoms_list[TS_step]
    TS_dis = d_list[TS_step]
    TS_energy = e_list[TS_step]
    TS_barrier = TS_energy - e_list[np.argmax(d_list)]

    #Find bonded state through similar algorithm
    troughs = []
    for i, slope in enumerate(diff_e<0):
        if i< len(diff_e)-1:
            if slope and not diff_e[i+1]<0:
                troughs.append(i+1)
    if troughs ==[]:
        troughs = [0]
        print('No bonded state found!!!')
    bonded_dis = np.min([xs[i] for i in troughs])
    bonded_step = np.argmin(abs(np.array(d_list)-bonded_dis))
    bonded_energy = e_list[bonded_step]
    rxn_energy = bonded_energy - e_list[np.argmin(d_list)]

    if TS_dis < min_d:
        print('Warning: very small ts bond length')
    return TS_step, TS_dis, TS_energy, TS_atoms, TS_barrier, rxn_energy

def FBL_plotter(d_list, e_list, TS_step = None):
    import matplotlib
    matplotlib.use('TKAgg')
    import matplotlib.pyplot as plt # type: ignore
    import numpy as np # type: ignore
    import base64
    fig  = plt.figure()
    e_list = np.array(e_list) - e_list[-1]
    plt.plot(d_list,e_list)
    if TS_step == None:
        plt.plot(d_list[TS_step],e_list[TS_step],marker ='o',color='r')
    plt.xlabel('Bond length (Angstroms)')
    plt.ylabel('Energy (eV)')
    plt.title('Barrier = %1.4f eV'%(e_list[TS_step]))
    plt.savefig('./fbl_plot.png')
    with open('./fbl_plot.png', 'rb') as f: img = base64.b64encode(f.read())
    return img

#####################
# IN PROGRESS
#####################


def NebScript():

    import os

    params,initatoms = initialize()  # Remove old .out/.err files, load from fw_spec, and write 'init.traj'
    n = params['images']
    if not os.path.exists('neb1.traj'): neb = initializeNeb(params)
    else: neb = reloadNeb()

    while True:
        if check_unconverged(params):
            address_unconverged(params)
        else:
            statuses = [check_images_near_peaks(i) for i in range(n)]
            if statuses.count('peak')==1: return finalize(statuses.index('peak')) #converged
            elif statuses.count('near_peak')==2: split_neb(*[s for s in statuses if s=='nearpeak'])
            else: run_neb()

def initializeNeb(params):
    """
    read in information from job param dictionary
    """

    import pickle as pickle # type: ignore
    from ase.neb import NEB # type: ignore

    #######################
    print("Initializing...")
    #----------------------

    finalatoms = pickle.loads(str(params['finaltraj_pckl']))
    write('initial.traj',initatoms)
    write('final.traj',finalatoms)
    images = [initatoms]
    for i in range(n):
        images.append(initatoms.copy())
    images.append(finalatoms)
    neb = NEB(images,k=params['k'])
    neb.interpolate()
    return neb

def run_neb(params):
    """
    Run NEB
    """
    from ase.optimize import FIRE # type: ignore
    from ase.io import Trajectory # type: ignore

    #######################
    print("Running...")
    #----------------------

    m = makeQEnebCalc(params)
    m.set_neb(neb)
    qn = FIRE(neb,logfile='qn.log')
    for j in range(1,n+1):
        traj = Trajectory('neb%d.traj' % j, 'w', images[j])
        qn.attach(traj)

    qn.run(fmax=params['fmax'])

def reloadNeb(params):
    """
    Use existing files in working directory to restart NEB
    """

    from ase.io import write,read # type: ignore

    ################################
    print("Reloading NEB images...")
    #-------------------------------

    images = [read('initial.traj')]
    for i in range(1,n+1):
        images.append(read('neb%d.traj'%i))
    images.append(read('final.traj'))
    neb = NEB(images,k=params['k'])
    return neb

def check_unconverged():
    """
    Check if NEB is unconverged
    """

    #######################
    print("Checking convergence")
    #----------------------

    raise NotImplementedError

def address_unconverged():
    """
    Deal with unconverged NEB
    """

    #########################################
    print("Addressing unconverged NEB...")
    #----------------------------------------

    raise NotImplementedError

def check_image_near_peak(img):
    """

    """

    #########################################
    print("Check if image %d is at a peak..."%img)
    #----------------------------------------

    raise NotImplementedError

def finalize(peak_img):
    """
    Final touches after NEB has converged
    """

    ################################
    print("Storing Results...")
    #-------------------------------

    raise NotImplementedError

def split_neb(peak1,peak2):
    """
    Address a NEB that seems to have two transition states
    """

    #########################################
    print("Addressing NEB with two peaks...")
    #----------------------------------------

    raise NotImplementedError

#####################
#####################
#####################

def DosScript():
    raise NotImplementedError

#############
# FIRETASKS
#############

def executeAndCollect():
    os.system('./metascript.sh')
    try:
        with open('result.json','r') as f:
            resultDictjson = f.read()
    except FileNotFoundError:
        pass

    return fireworks.core.firework.FWAction(stored_data={'resultjson':resultDictjson})

@fireworks.utilities.fw_utilities.explicit_serialize
class OptimizeLattice(fireworks.core.firework.FiretaskBase):
    def run_task(self,fw_spec):

        params = fw_spec['params']

        with open('params.json','w') as f: f.write(json.dumps(params))

        write_script([initialize  # Universal
                    ,traj_to_json
                    ,json_to_traj
                    ,make_atoms
                    ,cFunc(params)
                    ,optimize_pos
                    ,traj_details
                    ,log
                    ,OptimizeLatticeScript # Jobkind-specific
                    ,get_init_guess
                    ,get_bulk_energy
                    ,from_params
                    ,cellpar_to_cell
                    ,rank
                    ,merge_dicts # Auxillary
                    ,get_cluster
                    ,get_number_of_nodes
                    ],OptimizeLatticeScript)

        writeMetaScript(params['dftcode'])

        return executeAndCollect()



@fireworks.utilities.fw_utilities.explicit_serialize
class GetBulkModulus(fireworks.core.firework.FiretaskBase):
    def run_task(self,fw_spec):


        params = fw_spec['params']

        with open('params.json','w') as f: f.write(json.dumps(params))

        write_script([initialize  # Universal
                    ,traj_to_json
                    ,json_to_traj
                    ,make_atoms
                    ,cFunc(params)
                    ,optimize_pos
                    ,traj_details
                    ,log
                    ,BulkModulusScript # Jobkind-specific
                    ,quad_fit
                    ,rank
                    ,merge_dicts # Auxillary
                    ,get_cluster
                    ,get_number_of_nodes
                    ],BulkModulusScript)

        writeMetaScript(params['dftcode'])

        os.system('./metascript.sh')

        with open('result.json','r') as f: resultDictjson = f.read()

        return fireworks.core.firework.FWAction(stored_data={'resultjson':resultDictjson})

@fireworks.utilities.fw_utilities.explicit_serialize
class GetXCcontribs(fireworks.core.firework.FiretaskBase):
    def run_task(self,fw_spec):

        params = fw_spec['params']

        with open('params.json','w') as f: f.write(json.dumps(params))

        write_script([initialize         # Universal
                    ,traj_to_json
                    ,json_to_traj
                    ,make_atoms
                    ,cFunc(params)
                    ,traj_details
                    ,log
                    ,XCcontribsScript   # Jobkind-specific
                    ,merge_dicts         # Auxillary
                    ,rank
                    ,get_cluster
                    ,get_number_of_nodes
                    ],XCcontribsScript)

        writeMetaScript(params['dftcode'])

        return executeAndCollect()

#################################################################
@fireworks.utilities.fw_utilities.explicit_serialize
class Relax(fireworks.core.firework.FiretaskBase):
    def run_task(self,fw_spec):

        params = fw_spec['params']

        with open('params.json','w') as f: f.write(json.dumps(params))

        write_script([initialize    # Universal
                    ,traj_to_json
                    ,json_to_traj
                    ,make_atoms
                    ,cFunc(params)
                    ,optimize_pos
                    ,log
                    ,traj_details
                    ,RelaxScript    # Jobkind-specific
                    ,rank           # Auxillary
                    ,merge_dicts
                    ,get_cluster
                    ,get_number_of_nodes
                    ],RelaxScript)

        writeMetaScript(params['dftcode'])

        return executeAndCollect()

@fireworks.utilities.fw_utilities.explicit_serialize
class Vibrations(fireworks.core.firework.FiretaskBase):
    def run_task(self,fw_spec):

        params = fw_spec['params']

        with open('params.json','w') as f: f.write(json.dumps(params))

        write_script([initialize         # Universal
                    ,traj_to_json
                    ,json_to_traj
                    ,make_atoms
                    ,cFunc(params)
                    ,optimize_pos
                    ,traj_details
                    ,log
                    ,VibScript  # Jobkind-specific
                    ,rank
                    ,merge_dicts         # Auxillary
                    ,get_cluster
                    ,get_number_of_nodes
                    ],VibScript)

        writeMetaScript(params['dftcode'])

        return executeAndCollect()

@fireworks.utilities.fw_utilities.explicit_serialize
class FBL(fireworks.core.firework.FiretaskBase):
    def run_task(self,fw_spec):

        params = fw_spec['params']

        with open('params.json','w') as f: f.write(json.dumps(params))

        write_script([initialize         # Universal
                    ,traj_to_json
                    ,json_to_traj
                    ,make_atoms
                    ,cFunc(params)
                    ,optimize_pos
                    ,traj_details
                    ,log
                    ,FBLScript          # Jobkind-specific
                    ,get_FBL_TS_energy
                    ,FBL_plotter
                    ,rank
                    ,merge_dicts         # Auxillary
                    ,get_cluster
                    ,get_number_of_nodes
                    ],FBLScript)

        writeMetaScript(params['dftcode'])

        return executeAndCollect()

@fireworks.utilities.fw_utilities.explicit_serialize
class DOS(fireworks.core.firework.FiretaskBase):
    def run_task(self,fw_spec):

        params = fw_spec['params']

        with open('params.json','w') as f: f.write(json.dumps(params))

        write_script([initialize         # Universal
                    ,traj_to_json
                    ,json_to_traj
                    ,make_atoms
                    ,cFunc(params)
                    ,optimize_pos
                    ,traj_details
                    ,log
                    ,DosScript          # Jobkind-specific
                    ,rank
                    ,merge_dicts         # Auxillary
                    ,get_cluster
                    ,get_number_of_nodes
                    ],DosScript)

        writeMetaScript(params['dftcode'])

        return executeAndCollect()

@fireworks.utilities.fw_utilities.explicit_serialize
class NEB(fireworks.core.firework.FiretaskBase):
    def run_task(self,fw_spec):

        params = fw_spec['params']

        with open('params.json','w') as f: f.write(json.dumps(params))

        write_script([initialize         # Universal
                    ,traj_to_json
                    ,json_to_traj
                    ,make_atoms
                    ,cFunc(params)
                    ,traj_details
                    ,log
                    ,NebScript          # Jobkind-specific
                    ,rank
                    ,merge_dicts         # Auxillary
                    ,get_cluster
                    ,get_number_of_nodes
                    ],NebScript)

        writeMetaScript(params['dftcode'])

        return executeAndCollect()

@fireworks.utilities.fw_utilities.explicit_serialize
class VCRelax(fireworks.core.firework.FiretaskBase):
    def run_task(self,fw_spec):

        params = fw_spec['params']

        with open('params.json','w') as f: f.write(json.dumps(params))

        write_script([initialize         # Universal
                    ,traj_to_json
                    ,json_to_traj
                    ,make_atoms
                    ,cFunc(params)
                    ,optimize_pos
                    ,traj_details
                    ,log
                    ,VCRelaxScript      # Jobkind-specific
                    ,rank
                    ,merge_dicts         # Auxillary
                    ,get_cluster
                    ,get_number_of_nodes
                    ],VCRelaxScript)

        writeMetaScript(params['dftcode'])

        return executeAndCollect()

def vasp_script():
    import ase.calculators.vasp as vasp_calculator # type: ignore
    import json,multiprocessing,time,os,subprocess

    params,atoms = initialize()      # Remove old .out/.err files, load from fw_spec, and write 'init.traj'
    #############################################
    print("Initializing VASP calculator...")
    #-----------------------------------------

    calc  =  vasp_calculator.Vasp(encut   = params['pw']
                                ,setups   = json.loads(params['psp']) # dictionary {'Cu':'_s'}
                                ,xc       = params['xc']
                                ,gga      = params['gga']      # 'BF'
                                ,luse_vdw = params['luse_vdw'] # True
                                ,zab_vdw  = params.get('zab_vdw')
                                ,kpts     = json.loads(params['kpts'])
                                ,npar     = 1                  # use this if you run on one node (most calculations).  see suncat confluence page for optimal setting
                                ,kpar     = 1
                                ,gamma    = params['gamma']    # True,  # Gamma-centered (defaults to Monkhorst-Pack)
                                ,ismear   = 0                  # assume gaussian smearing, we can make this parameter if necessary
                                ,algo     = params['algo']     #'fast',
                                ,nelm     = params['maxstep']
                                ,sigma    = params['sigma']
                                ,ibrion   = params['ibrion']   #2
                                ,nelmdl   = params['nelmdl']
                                ,isif     = 3 if params['jobkind']=='vcrelax' else 2
                                ,ediffg   = -params['fmax']                        # forces
                                ,ediff    = params['econv']                        # energy conv. both of these are for the internal relaxation, ie nsw
                                ,prec     = params['prec']                         #'Accurate'
                                ,nsw      = params['ionic_steps']                  # use ASE ?
                                ,ispin    = 2 if params['spinpol'] else 1
                                ,lreal    = params['lreal']                        # automatically decide to do real vs recip space calc
                                ,ldipol   = params['dipole']                       #True,
                                ,lvhar    = True                                   #True,
                                ,dipol    = params.get('dipol')                    #(0.5,0.5,0.5),
                                ,idipol   = 3 if params['dipole'] else None
                                ,icharg   = 1)                                     # start from CHGCAR if icharg = 1

    atoms.set_calculator(calc)

    ############################################
    print("Generating VASP Input files with ASE")
    #------------------------------------------
    try:
        proc = multiprocessing.Process(target=atoms.get_potential_energy)
        proc.start();time.sleep(10)
        if proc.is_alive(): proc.terminate()
    except IOError: pass #on nersc, we get io error

    #######################
    print("Running VASP natively...")
    #----------------------

    loader = {'sherlock':  "ml vasp/5.4.1.intel.gpu"
             ,'sherlock2': "ml chemistry vasp/5.4.1"
             ,'nersc':      "module load vasp-tpc/5.4.1"}

    vaspout, vasperr = subprocess.Popen(loader[get_cluster()]+';which vasp_std;srun -n 32 vasp_std', stdout=subprocess.PIPE, stderr=subprocess.PIPE,shell=True).communicate()
    print('VASP output:\n',vaspout)
    with open('OUTCAR','r') as f:
        if 'General timing and accounting informations for this job' in f.read():
            if rank()==0: log(params)
            return 0
    raise ValueError(vasperr)

@fireworks.utilities.fw_utilities.explicit_serialize
class VaspJob(fireworks.core.firework.FiretaskBase):
    def run_task(self,fw_spec):
        import os
        params = fw_spec['params']
        with open('params.json','w') as f: f.write(json.dumps(params))
        write_script([initialize,rank,get_cluster,make_atoms,log,vasp_script],vasp_script)
        os.system('python script.py')
        return 0


########################################################################
# WHAT WE EXPORT
########################################################################
script_dict = {'latticeopt': OptimizeLattice()
             ,'bulkmod': GetBulkModulus(),'vasp':VaspJob()
             ,'relax': Relax(),'vcrelax': VCRelax()
             ,'fbl': FBL(),'dos': DOS(),'neb': NEB()
             ,'vib': Vibrations(),'xc': GetXCcontribs()}
