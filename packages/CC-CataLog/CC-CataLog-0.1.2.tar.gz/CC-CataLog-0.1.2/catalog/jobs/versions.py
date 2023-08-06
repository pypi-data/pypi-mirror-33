import json
# Internal Modules
from catalog.jobs.version_utils import Version,Key,const,onlyif,pickletraj_to_jsontraj,dftcode,err,has_parent,get_kwargs,classify,single_atom,check_init_magmoms
from decimal import Decimal
################################################
# Constants
#----------
NoneType = type(None)
#######################################################
# data
#-----
keys_v1 = [Key('jobkind'
            ,'What kind of calculation the job is performing'
            ,domain = ['latticeopt,relax,vcrelax,neb,bulkmod,dos,xc,chargemol,fbl']
            )

          ,Key('pw'
            ,'Planewave cutoff, eV'
            ,int)

          ,Key('dftcode'
            ,'Which code is used to generate results'
            ,domain = ['vasp','gpaw','quantumespresso'])

          ,Key('xc'
            ,'Exchange correlation functional'
            ,domain = ['PBE','RPBE','BEEF','mBEEF'])

          ,Key('psp'
            ,'Name of pseudopotential used'
            ,domain = ['sg15','gbrv15pbe','paw','oldpaw'])

          ,Key('kpts'
            ,'List/Tuple of K points (x,y,z)'
            ,[list,tuple]
            ,process = {0:lambda d: json.loads(d['kpts']) if isinstance(d['kpts'],str) else d['kpts']}
            )

          ,Key('spinpol'
            ,'Whether or not calculation is spin polarized'
            ,int
            ,default = check_init_magmoms)


          ,Key('inittraj'
            ,'JSON version of an ASE trajectory file'
            ,str
            ,default = {0 : pickletraj_to_jsontraj})

          ,Key('econv'
            ,'Differential energy for electronic convergence'
            ,[float,Decimal]
            ,default = const(1e-5))

          ,Key('fmax'
            ,'Max force for ionic convergence'
            ,[float,Decimal]
            ,default = const(0.05))

          ,Key('mixing'
            ,'Linear mixing parameter for electronic density'
            ,[float,Decimal]
            ,default = const(0.1))

          ,Key('maxstep'
            ,'Max number of electronic steps'
            ,int
            ,default = const(250))

          ,Key('sigma'
            ,'Fermi temperature'
            ,[float,Decimal]
            ,process = lambda d: float(d['sigma'])
            ,default = const(0.1))

          ,Key('nbands'
            ,'Number of bands (negative means additional empty bands)'
            ,[int,NoneType]
            ,default = onlyif(dftcode('gpaw','quantumespresso')
                             ,const(-12)))

          ,Key('nmix'
            ,'Number of previous steps mixed in the electronic density'
            ,[int,NoneType]
            ,default = onlyif(dftcode('gpaw','quantumespresso')
                             ,const(10)))

          ,Key('hund'
            ,'Flag for managing spin for single-atom calculations in GPAW'
            ,domain  = [0,1,None]
            ,default = onlyif(dftcode('gpaw'),single_atom))

          ,Key('dw'
            ,'Electronic density granularity cutoff'
            ,[int,NoneType]
            ,default = onlyif(dftcode('quantumespresso')
                             ,lambda d: d['pw']*10))

          ,Key('mixingtype'
            ,'Mixing scheme'
            ,domain  = ['plain','local-TF',None]
            ,default = onlyif(dftcode('quantumespresso')
                             ,const('plain')))

          ,Key('gga'
            ,'XC functional (is this redundant given the xc key?) '
            ,domain  = ['PE','BF',None]
            ,default = onlyif(dftcode('vasp')
                             ,const('PE')))

          ,Key('luse_vdw'
            ,'Turn on vdW correction'
            ,domain=[0,1,None]
            ,default = onlyif(dftcode('vasp')
                             ,const(0)))

          ,Key('zab_vdw'
            ,'???'
            ,domain  = [0,1,None]
            ,default = onlyif(lambda p: p.get('gga')=='BF'
                             ,const(-1.8867)))

          ,Key('gamma'
              ,'Include gamma point?'
              ,domain  = [0,1,None]
              ,default = onlyif(dftcode('vasp')
                            ,const(1)))

          ,Key('ismear'
              ,'ISMEAR determines how the partial occupancies are set for each wavefunction (-1 = Fermi, 0 = Gaussian) IS THIS THE SAME THING AS MIXINGTYPE?'
              ,domain  = [-1,0,None]
              ,default = onlyif(dftcode('vasp')
                            ,const(0)))

          ,Key('kind'
            ,'override automatic detection of bulk/surface/molecule'
            ,domain  = ['bulk','surface','molecule']
            ,default = lambda d: classify(d['inittraj']))

          ,Key('dipol'
            ,"JSON'd list of dipole moment center coordinates (initial guesss)"
            ,[str,NoneType]
            ,default = const(None))

          ,Key('algo'
              ,'specify the electronic minimisation algorithm'
              ,domain  = ['Normal','All','Fast','Damped','Diag',None]
              ,default = onlyif(dftcode('vasp')
                               ,const('normal')))

          ,Key('ibrion'
            ,"SEE VASP DOCS"
            ,[int,NoneType]
            ,default = onlyif(dftcode('vasp')
                             ,const(2)))

          ,Key('nelmdl'
            ,"# of non self consistent electronic steps"
            ,[int,NoneType]
            ,default = onlyif(dftcode('vasp')
                             ,const(-5)))

          ,Key('prec'
            ,'influences the default for four sets of parameters (ENCUT; NGX, NGY, NGZ; NGXF, NGYF, NGZF and ROPT)'
            ,domain  = ['Low','Medium','High','Normal','Accurate','Single',None]
            ,default = onlyif(dftcode('vasp')
                             ,const('normal')))


          ,Key('ionic_steps'
            ,'Max # of ionic steps'
            ,int
            ,default = const(250))

          ,Key('lreal'
            ,'Determines whether the projection operators are evaluated in real-space or in reciprocal space'
            ,domain  = ['.TRUE.','.FALSE.','Auto',None]
            ,default = onlyif(dftcode('vasp')
                            ,const('auto')))

          ,Key('lvhar'
            ,'Determines whether the total local potential (file LOCPOT) contains the entire local potential (ionic plus Hartree plus exchange correlation) or the electrostatic contributions only (ionic plus Hartree)'
            ,[int,NoneType]
            ,default = onlyif(dftcode('vasp')
                            ,const(0)))

          ,Key('structure'
            ,"""The meaning of this isn't terribly clear
                - (should an fcc lattice with an interstitial H be classified as fcc?)
                - Functionally, it is only important when doing latticeopt
                -  (cell information is condensed to minimum-length vector
                -  (e.g. trigonal cells are parameterized by a singleton)
                - which is operated upon by scipy.fmin)"""

            ,domain = ['fcc','hcp','bcc','diamond','cscl'
                      ,'rocksalt-unit','zincblende-unit','M3N-unit'
                      ,'rocksalt'     ,'zincblende'     ,'M3N'
                      ,'Li3N', 'antibixbyite'
                      ,'triclinic','2DMaterial',None]

            ,default = onlyif(lambda d: d['kind'] in ['bulk'] and d['jobkind'] == 'latticeopt'
                             ,err('structure')))

          ,Key('facet'
            ,'json-dumped list of three integers (sorry, HCP)'
            ,[str,NoneType]
            ,default = onlyif(lambda d: d['kind']=='surface'
                             ,err('facet')))

          ,Key('adsorbates'
            ,"JSON'd list of lists (each sublist is a list of indices for a particular adsorbate)"
            ,[str,NoneType]
            ,default = const(None))

          ,Key('xtol'
            ,'Convergence threshold for lattice parameters (or angles, in radians) when minimizing energy'
            ,[float,Decimal,NoneType]
            ,default = onlyif(lambda d: d['jobkind']=='latticeopt'
                             ,const(0.005)))

          ,Key('strain'
            ,'The percent (in both +/- directions) by which all lattice vectors will be stained to generate a dE/dV curve'
            ,[float,Decimal,NoneType]
            ,default = onlyif(lambda d: d['jobkind']=='bulkmod'
                             ,const(0.03)))

          ,Key('vibids'
            ,"JSON'd list of indices to vibrate"
            ,[str,NoneType]
            ,default = const(None))

          ,Key('delta'
            ,'Distance by which atoms will be varied to estimate local PES curvature'
            ,[float,Decimal,NoneType]
            ,default = onlyif(lambda d: d['jobkind']=='vib'
                             ,const(0.04)))

          ,Key('bonded_inds'
            ,'json-dumped list of two indices which will be brought together in FBL'
            ,[str,NoneType]
            ,default = onlyif(lambda d: d['jobkind']=='fbl'
                             ,err('bonded_inds')))

          ,Key('energy_cut_off'
            ,'used as a stopping criterion for FBL'
            ,[float,Decimal,int,NoneType]
            ,default = onlyif(lambda d: d['jobkind']=='fbl'
                             ,err('energy_cut_off')))

          ,Key('step_size'
            ,'Angstrom'
            ,[float,Decimal,NoneType]
            ,default = onlyif(lambda d: d['jobkind']=='fbl'
                             ,err('step_size')))

          ,Key('finaltraj'
            ,'???'
            ,[str,NoneType]
            ,default = onlyif(lambda d: d['jobkind']=='neb'
                             ,err('finaltraj')))

          ,Key('k'
            ,'spring constant'
            ,[float,Decimal,NoneType]
            ,default = onlyif(lambda d: d['jobkind']=='neb'
                             ,const(0.3)))

          ,Key('images'
            ,'number of images in NEB'
            ,[int,NoneType]
            ,default = onlyif(lambda d: d['jobkind']=='neb'
                             ,const(5)))

          ,Key('dipole'
            ,"Dipole correction used"
            ,domain=[0,1]
            ,default = lambda d: int(d['kind']=='surface'))

          ,Key('job_name'
            ,'(This used to be in keyword args, which has now been deprecated) '
            ,[str,NoneType]
            ,default = {0 : get_kwargs})

         ,Key('parent'
            ,'Job which the current job is based on (not defined for latticeopt/molecule-relax,vc-relax)'
            ,[str,NoneType]
            ,default = onlyif(has_parent,err('parent')))
         ,Key('cell_dofree'
             ,'Determines which cell parameters vcrelax will try to optimize. (2Dxy will only optimize x and y dimensions)'
             ,domain = ['all','x','y','z','xy','xz','yz','xyz','shape','volume','2Dxy','2Dshape',None]
             ,default = onlyif(lambda d: d['jobkind']=='vcrelax',const(None)))
         ,Key('cell_factor'
             ,'Parameter for VC relax jobs'
             ,[float,Decimal,NoneType]
             ,default = onlyif(lambda d: d['jobkind']=='vcrelax',const(2.)))
            ]

version1 = Version(1,keys_v1)

# keys_v2 can be defined relative to version 1
versions = [version1] # ,version2,...]
current_version = version1
