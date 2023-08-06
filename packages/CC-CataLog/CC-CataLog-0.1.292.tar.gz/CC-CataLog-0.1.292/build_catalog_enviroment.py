#External imports
import sys
from glob import glob


#Check to confirm that python3.6 or newer is being used
major_version, minor_version = sys.version_info[:2]
if major_version < 3 or minor_version < 6:
    raise Exception("Python 3.6 or a more recent version is required.")

import venv # type: ignore
import os, shutil

def build_venv(env_dir):
    if not os.path.exists(env_dir):
        os.mkdir(env_dir)

    #Build the Virtual enviroment and set the required user variables
    venv.create(os.path.join(env_dir,'.env'),with_pip = True,symlinks = True)
    shell = os.getenv('SHELL','')
    rcpath = os.path.join(env_dir,'.env/bin/activate')
    user_vars_dict = get_user_enviroment_vars()
    set_user_enviromental_vars(rcpath,        user_vars_dict)
    set_user_enviromental_vars(rcpath+'.csh', user_vars_dict)

    #Pip install the required packages
    python_exec = os.path.join(env_dir,'.env/bin/python')
    os.system("{} -m pip install pip --upgrade --no-cache-dir".format(python_exec))
    os.system("{} -m pip install numpy --upgrade --no-cache-dir".format(python_exec))
    os.system("{} -m pip install CC-CataLog --upgrade --no-cache-dir".format(python_exec))

    # #Add the fireworks folder and the required sub-directories
    add_fireworks_folders()

    #Get the user to set the $CATALOG_LOC variable in their bashrc
    if 'bash' in shell:
        print("""
        !!!!!!IMPORTANT!!!!!
        NEED TO DO ONE MORE THING
        PLEASE RUN THIS COMMAND
        echo export CATALOG_LOC={}>>~/.bashrc

        To Source this enviroment in the future use the command:
        source $CATALOG_LOC/.env/activate
        or you can alias it:
        echo alias cata_src=\"source $CATALOG_LOC/.env/bin/activate\">>~/.bashrc
        """.format(os.environ['CATALOG_LOC']))
    elif 'tcsh' in shell:
        print("""
        !!!!!!IMPORTANT!!!!!
        NEED TO DO ONE MORE THING
        PLEASE RUN THIS COMMAND
        echo setenv CATALOG_LOC {}>>~/.cshrc

        To Source this enviroment in the future use the command:
        source $CATALOG_LOC/.env/activate.csh
        or you can alias it:
        echo alias cata_src "source $CATALOG_LOC/.env/bin/activate.csh">>~/.cshrc
        """.format(os.environ['CATALOG_LOC']))

def get_user_enviroment_vars():
    #Set of required user-defined variables
    user_keys = {'USER'               : "Generic username used as default for new clusters"
                ,'SHERLOCK2_USERNAME' : "Username for Sherlock2 cluster"
                ,'SUNCAT_USERNAME'    : "Username for Suncat Cluster"
                ,'HOSTNAME'           : "Name of current cluster (sherlock, suncat, local)"
                ,'LAUNCHPAD_YAML'     : "Path to your launchpad_yaml for fireworks on this cluster"
                }
    user_vars_dict = {} # type: dict
    #Print a description of each variable and ask the user for input
    for var, desc in user_keys.items():
        print('#####################')
        print(var+': '+desc)
        user_value = input("Please Enter your value for env-var, {}: ".format(var))
        if var in ['LAUNCHPAD_YAML']:
            user_value = os.path.abspath(user_value)
        os.environ[var] = user_value
        user_vars_dict[var] = user_value
        print("value for {} set to {}".format(var,user_value))
        print('#-------------------')
    return user_vars_dict

def set_user_enviromental_vars(rcpath,user_vars_dict):
    with open(rcpath,'a') as f:
        f.write("#####################\n")
        f.write("#Catalog enviromental variables\n")
        f.write("#####################\n")
        if rcpath.endswith('csh'):
            f.write("setenv PYTHONPATH {}:$PYTHONPATH\n".format(env_dir))
            for key,val in user_vars_dict.items():
                f.write("setenv {} {}\n".format(key,val))
        else:
            f.write("export PYTHONPATH={}:$PYTHONPATH\n".format(env_dir))
            for key,val in user_vars_dict.items():
                f.write("export {}={}\n".format(key,val))

def add_fireworks_folders():
    #Make all the necessary folders
    safe_mkdir(os.path.join(env_dir,'fireworks'))
    safe_mkdir(os.path.join(env_dir,'fireworks','jobs'))
    safe_mkdir(os.path.join(env_dir,'fireworks','FW_CONFIG_DIR'))
    safe_mkdir(os.path.join(env_dir,'fireworks','logs'))

    #Make a FW_config.yaml
    with open(os.path.join(env_dir,'fireworks','FW_config.yaml'),'w') as f:
        f.write('ALWAYS_CREATE_NEW_BLOCK: True')

    #Fill the FW_CONFIG_DIR with my_launchpad, my_fworker, and my_qadapter
    #Copy the launchpad_yaml
    shutil.copy(os.environ['LAUNCHPAD_YAML'],os.path.join(env_dir,'fireworks','FW_CONFIG_DIR','my_launchpad.yaml'))

    #Write the my_fworker.yaml
    with open(os.path.join(env_dir,'fireworks','FW_CONFIG_DIR','my_fworker.yaml'),'w') as f:
        f.write("name: {}\n".format(get_cluster()))
        f.write("category: ''\n")
        f.write("query: '{}'\n")

    if not os.environ['HOSTNAME'] == 'local':
        #Write the my_qadapter.yaml
        #Get the queueing system from the user
        queue_system = None
        print('#####################')
        while not queue_system in ['SLURM','LSF','PBS','None']:
            queue_system = input("Which queueing system does this cluster use (SLURM/LSF/PBS/None)?")
        if queue_system == 'None':
            print("Since the queueing system was set to None, this machine can not be used to run jobs\n It can still launch them though!")
        print('#-------------------')

        template_dict = {'LSF'   : 'LoadSharingFacility_template.txt'
                        ,'PBS'   : 'PBS_template.txt'
                        ,'SLURM' : 'SLURM_template.txt'
                        ,'None'  : 'None'}
        template_file = glob('{}/.env/lib/*/site-packages/catalog/fw/qadapter_templates/{}'.format(env_dir,template_dict[queue_system]))[0]

        qtype_dict    = {'LSF'   : 'LoadSharingFacility'
                        ,'PBS'   : 'PBS'
                        ,'SLURM' : 'SLURM'
                        ,'None'  : 'null'}

        with open(os.path.join(env_dir,'fireworks','FW_CONFIG_DIR','my_qadapter.yaml'),'w') as f:
            f.write("_fw_name: CommonAdapter\n")
            f.write("_fw_q_type: {}\n".format(qtype_dict[queue_system]))
            f.write("_fw_template_file: {}\n".format(template_file))
            f.write("queue: {}\n".format(os.environ['HOSTNAME']))
            f.write("rocket_launch: rlaunch -c $CATALOG_LOC/FW_CONFIG_DIR singleshot\n")

        #Copy the launcher function to the fireworks folder
        with open(os.path.join(env_dir,'fireworks','launcher.sh'),'w') as f:
            f.write("#!/bin/bash\n")
            f.write("source $CATALOG_LOC/.env/bin/activate\n")
            f.write("$CATALOG_LOC/.env/bin/qlaunch -c $CATALOG_LOC/fireworks/FW_CONFIG_DIR --logdir $CATALOG_LOC/fireworks/logs -r rapidfire\n")
        os.chmod(os.path.join(env_dir,'fireworks','launcher.sh'),0o755)

def safe_mkdir(dir_path):
    if not os.path.exists(dir_path):
        os.mkdir(dir_path)

def get_cluster():# type: ignore
    """Get the name of the cluster this command is being executed on"""
    hostname = os.environ['HOSTNAME'] # type: ignore
    if      'sh'     in hostname: return 'sherlock2'
    elif    'gpu-15' in hostname: return 'sherlock2'
    elif    'su'     in hostname: return 'suncat' #important to distinguish suncat2 and 3?
    elif    'kris'   in hostname: return 'kris'
    elif    'local'  in hostname: return 'local'
    else: raise ValueError("was not able to identify the cluster from hostname = %s"%hostname)


if __name__ == '__main__':
    env_dir = input('Please enter the path you would like to put the CataLog enviroment\n(Please choose an empty or non-existent folder): ')
    env_dir = os.path.abspath(env_dir)
    os.environ['CATALOG_LOC'] = env_dir
    build_venv(env_dir)
