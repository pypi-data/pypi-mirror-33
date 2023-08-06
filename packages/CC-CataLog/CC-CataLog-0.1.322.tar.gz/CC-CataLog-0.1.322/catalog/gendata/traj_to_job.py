#Typing imports
import typing as typ
if typ.TYPE_CHECKING:
    from catalog.jobs.jobs import Job

#external modules
import json,pickle,copy
import ase # type: ignore
from ase.io import read # type: ignore
from ase.visualize import view

#internal modules
from catalog.jobs.jobs              import Job
from catalog.misc.utilities         import merge_dicts
from catalog.misc.print_parse       import abbreviate_dict
from catalog.jobs.versions          import current_version
import catalog.misc.atoms           as     ma
from catalog.jobs.repeat            import RepeatChecker

checker = RepeatChecker()

class TrajToJob(object):
    """
    Class to easily submit jobs from an existing traj File

    Traj is a initital traj file that will initilize numerous types of job_submiter

    !!!!DEFAULT CALCULATOR VALUES ARE IN easy_makeQEcalc METHOD!!!!

    Currently supported jobkinds:
    relax
    latticeopt
    vcrelax

    Currently supported codes:
    quantumespresso

    Keys required in user_params:
    kpts, xc, fmax, pw

    latticeopt jobs: xtol

    vcrelax jobs: cell_dofree (optional)

    Surface jobs: facet (for 2D materials simply use json.dumps([0,0,0]))
    """
    def __init__(self
                ,traj              : ase.Atoms
                ,jobkind           : str
                ,structure         : str
                ,user_params       : dict           = {}
                ,repeat_checker    : RepeatChecker  = checker
                ) -> None:

                #Check assertions on user inputs
                assert isinstance(traj,ase.Atoms)
                assert jobkind     in ['relax','vcrelax','latticeopt']

                #Set object member data
                self.traj               = traj
                self.structure          = structure
                self.jobkind            = jobkind
                self.repeat_checker     = repeat_checker

                #Initialize the job parameters with the easy_makeQEcalc
                #User must specify the following keys in user_params:
                #kpts, xc, fmax, pw (See easy_makeQEcalc for more detailed explanation of types)
                self.params              = self.easy_makeQEcalc(user_params)
                self.params['inittraj']  = ma.traj_to_json(traj)
                self.params['jobkind']   = jobkind
                self.params['structure'] = structure
                self.job                 = current_version.process_dict(self.params)

    def easy_makeQEcalc(self
                       ,params : dict
                       ) -> dict:
        """returns a dictionary containing all of the ASE calculator parameters
        required to specify a QE calculator object and its associated force minimizer

        USAGE:
        params: A dictionary containing at least the critical calculator parameters
        that must be specified for each calculator (no defaults are specified). If
        non-critical parameters are supplied, the default values will be updated.
        If non-calculator parameters are supplied they will be unchanged

        Required params:
        key                type:                       ex:
        (kpts or kptden)   (int or json.dumps(list)    (4 or json.dumps([12,12,12]))
        xc                 str                          'RPBE'
        fmax               float                        0.05
        pw                 int                          500


        Output:
        merged_params: A dictionary that contains the merged dictionary of the
        originally supplied parameters and the default parameters with their
        updated values
        """

        ###################
        #Default Parameters
        ###################
        #convergence_params
        convergence_params_defaults = {
        'econv':				1e-5
        ,'mixing':				0.1
        ,'nmix':				10
        ,'maxstep':				200
        ,'nbands':				-20
        ,'sigma':				0.1
        }
        #!!!!IMPORTANT CALCULATOR PARAMETERS!!!!
        calculator_params_defaults = {
        'psp':                  'gbrv15pbe'
        ,'dwrat':               10
        ,'dftcode':             'quantumespresso'
        }

        critical_calc_keys = ['kpts','kptden','xc','pw','fmax']
        default_keys = list(convergence_params_defaults.keys())+list(calculator_params_defaults.keys())

        #Check that critical calculator keys were supplied
        assert set(['xc','pw','fmax']) <= set(params.keys()),"Please supply xc, pw, or fmax"
        assert 'kpts' in params.keys() or 'kptden' in params.keys(), "Please supply kpts or kptden"

        #Merge default dictionaries with the supplied critical parameters
        critical_params = {k: params.get(k) for k in critical_calc_keys}
        merged_params = merge_dicts([critical_params,convergence_params_defaults,calculator_params_defaults])
        merged_params.update({k: params.get(k) for k in params.keys() if k not in  critical_calc_keys})
        return merged_params

    def submit(self
              ,check         : bool = True
              ) -> None:
        view(self.traj)
        msg =  abbreviate_dict(self.params)+'\nNew job, sure you want to submit the following? (y/n)'
        if not check or 'y' in input(msg).lower():
            self.job.submit(self.repeat_checker)
        else:
            print('The job was not submitted')
