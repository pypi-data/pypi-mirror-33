# Typing Modules
import typing as typ

# External Modules
import pickle,json
from decimal import Decimal

# Internal Modules
from catalog.misc.atoms import traj_to_json,json_to_traj,classify_system
from catalog.jobs.jobs import Job
"""
Class for version control of "jobs".

Also store versions in this file


Old preprocessing that might need to be addressed:

        params['spinpol']  = typ.Any([x>0 for x in self.atoms.get_initial_magnetic_moments()])

        ###############################################################
        if params.get('kpts') is None and params.get('kptden') is not None:
            recipcell,kpts = self.atoms.get_reciprocal_cell(),[]
            for i in range(3):
                k = 2 * 3.14 * ((recipcell[i]**2).sum())**(0.5) * params['kptden']
                kpts.append(2 * int(round(k / 2)))

            if   self.kind=='surface':  params['kpts'] = json.dumps(kpts[:2]+[1])
            elif self.kind=='molecule': params['kpts'] = json.dumps([1,1,1])
            else:                       params['kpts'] = json.dumps(kpts)
        ##################################################################

        if 'facet_json' in params.keys(): params['facet']=params.pop('facet_json')
        if 'vibids_json' in params.keys(): params['vibids']=params.pop('vibids_json')
        if 'adsorbates_json' in params.keys(): params['adsorbates']=params.pop('adsorbates_json')
        if params.get('structure')=='hexagonal': params['structure'] = 'hcp'

"""
###################################################
# Constants
#----------


# We want a mapping from VERSION NUMBER to FUNCTION
#   where the function fills in the value (typ.Any type)
#   *given* the rest of the parameters (typ.Dict)
# Alternatively, a single function means valid for all verions
DefaultFunc    = typ.Callable[[typ.Dict],typ.Any]
DefaultHandler = typ.Union[DefaultFunc,typ.Dict[int,DefaultFunc]]

#######################################################
# Helper functions
#-----------------

def err(keyname : str) ->  DefaultFunc:
    """
    Throws an error when called - use as 'default' function for required keys
    """
    def f(d : dict) -> typ.Any:
        raise ValueError("Required key <%s> not found in %s"%(keyname,str(d.keys())))
    return f

def const(x : typ.Any) -> DefaultFunc:
    """
    Turns a value into a function that ignores its input and returns that value
    """
    def f(_ : dict) -> typ.Any: return x
    return f

def onlyif(pred  : typ.Callable[[typ.Dict], bool]
          ,dfunc : DefaultFunc
          ) -> typ.Any:
    """
    Applies default function only if condition is met (otherwise None)
    """
    def f(Dictionary : dict)->typ.Any:
        if pred(Dictionary): return dfunc(Dictionary)
        else:                return None
    return f

def dftcode(*codes : str) -> typ.Callable[[typ.Dict], bool]:
    """
    Helpful docstring
    """
    def f(d : dict) -> bool: return d['dftcode'] in codes
    return f

def single_atom(params : typ.Dict ) -> bool:
    """
    Helpful docstring
    """
    atoms      = json_to_traj(params['inittraj'])
    singleatom = len(atoms) == 1
    mol        = params.get('kind')=='molecule'
    return singleatom and mol

def classify(traj_json : str) -> str:
    """
    Identify whether initial traj of a params typ.Dict is bulk/surf/molecule
    """
    return classify_system(json_to_traj(traj_json))

def get_kwargs(d: typ.Dict)->str:
    """
    Try to extract job name from a Version 0 job
    """
    k = d.get('kwargs')
    if k is None: return ''
    else:
        try:
            kw = json.loads(k)
            n  = kw.get('jobname')
            return n if n else ''
        except:
            return ''

def has_parent(d : typ.Dict) -> bool:
    """
    Check for a job needing to have a parent
    """
    conditions = [d['jobkind'] in ['vcrelax','latticeopt']
                 ,d['jobkind']=='relax' and d['kind']=='molecule']
    return not any(conditions)


def check_init_magmoms(d : typ.Dict) -> int:
    """
    Returns true (1) if typ.Any magmoms in inittraj
    """
    try:
        atom_data = json.loads(d['inittraj'])['atom_data']
    except KeyError:
        atom_data = json.loads(d['inittraj'])['atomdata']
    mags     = [a['magmom'] for a in atom_data]
    return any([x>0 for x in mags])


##############################################################################################################
##############################################################################################################
##############################################################################################################
# Classes
#--------
class Key(object):
    """
    dtype       - a type / list of types that we enforce with `isinstance`
                - if we specify a domain of possible values, then this field is
                    redundant (throw error if both/neither specified)

    description - what the key is used for, typ.Any special considerations

    domain      - an (optional) set of values that we enforce the value falls in

    default     - a function which can initialize the value (given the rest of
                    the typ.Dictionary)

    """
    def __init__(self
                ,name    : str
                ,desc    : str                          = '<no description available yet>'
                ,dtype   : typ.Any                      = None # don't know how to typecheck this one
                ,domain  : typ.Optional[list]           = None
                ,process : typ.Optional[DefaultHandler] = None
                ,default : typ.Optional[DefaultHandler] = None
                ) -> None:

        # Validate input upon construction
        init_err  = 'need to specify either a domain of values or a set of'
        init_err += 'possible types for '+name

        assert (domain is None) ^ (dtype is None), init_err

        # Default handling of inputs
        if isinstance(dtype,type):
            dtype = [dtype]         # box a singleton

        if process is None:
            process = lambda d: d.get(self.name)

        if default is None:
            default = err(name)    # default = throw error

        # Store data in fields
        self.name    = name
        self.dtype   = dtype
        self.desc    = desc
        self.domain  = domain
        self.process = process
        self.default = default

    def _check(self
              ,val : typ.Any
              ) -> typ.Any:
        """
        Enforces domain and type specification for a given value
        """
        err_msg  = "Expected one of %s for input %s" % (self.dtype,self.name)
        err_msg += ", but got %s" % val.__class__
        if self.dtype is not None:
            success  = any([isinstance(val,x) for x in self.dtype])

            if not success:
                raise TypeError(err_msg)

            elif self.domain is not None:
                err_msg2  = "Expected %s to be in %s" % (self.dtype,self.domain)
                err_msg2 += ", but got %s" % val
                success   = val in self.domain
                if not success:
                    raise ValueError(err_msg2)

        return val

    def get_val(self
               ,params  : dict
               ,curr_version : int
               ) -> typ.Any:
        """
        Protocol for inferring a value from an arbitrary params typ.Dictionary
        Handles defaults and applies the validation check
        """

        val = params.get(self.name)

        if val is None: process_func = self.default
        else:           process_func = self.process

        version = params.get('version',0) # before the days of version control

        # print('\tgetting val for',self.name)

        if version > curr_version:
            raise ValueError('current version < dict version')

        elif version < curr_version:

            if isinstance(process_func,typ.Dict):
                try:
                    val = process_func[version](params)
                except KeyError:
                    err_msg = "%s has no default for version %d"%(self.name,version)
                    raise ValueError(err_msg)
            else:
                # no version-dependency of default function
                val = process_func(params)

        return self._check(val)

class Version(object):
    """
    Gives a set of keys a unique ID
    """
    def __init__(self
                ,id       : int
                ,keys     : typ.List[Key]
                ) -> None:

        # Validate input upon construction
        assert len(set([x.name for x in keys]))==len(keys),'DUPLICATE KEYS'

        self.id   = id
        self.keys = keys

    def process_dict(self,dict_input : dict)->"Job":
        dict_output = dict_input
        for key in self.keys:
            val = key.get_val(dict_output, self.id)
            if isinstance(val,Decimal):
                val = float(val)
            dict_output.update({key.name:val})
        return Job(dict_output)


#######################################################
# default functions
#--------------------
def pickletraj_to_jsontraj(d : typ.Dict) -> str:
    """
    Converts old traj format (pickled ASE atoms object) into new format
    """
    try:
        a = pickle.loads(d['inittraj_pckl'].encode())
    except UnicodeDecodeError:
        a = pickle.loads(d['inittraj_pckl'].encode('latin1'), encoding='latin1')
    return traj_to_json(a)
