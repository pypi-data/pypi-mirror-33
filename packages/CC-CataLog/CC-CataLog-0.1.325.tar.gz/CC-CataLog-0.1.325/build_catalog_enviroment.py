#External imports
import sys
from glob import glob
import venv # type: ignore
import os, shutil

#Check to confirm that python3.6 or newer is being used
major_version, minor_version = sys.version_info[:2]
if major_version < 3 or minor_version < 6:
    raise Exception("Python 3.6 or a more recent version is required.")

class UserDefinedVariable:
    def __init__(self
                ,name
                ,desc       = ''
                ,domain     = None
                ,test       = lambda x: True
                ,process    = lambda x: x):
        """
        Class for storing information on user defined variables

        Parameters
        ----------
        name   : str
            The name the variable will be stored as.
        desc   : str
            A description of the user defined variable to be displayed
        domain : list
            A list of values that are allowed for the user defined variables.
            Defaults to None which allows all values
        test   : function
            A function that will be applied to the value given. Defaults to
            store_true
        process: function
            A function to process the user input (i.e. turn a path into an absolute path
            with os.path.abspath)
        """
        self.name    = name
        self.desc    = desc
        self.domain  = domain
        self.test    = test
        self.process = process

    def get_user_val(self):
        print('#####################')
        print(self.name+': '+self.desc)
        user_value = None
        while user_value == None:
            user_value = input("Please Enter your value for {}: ".format(self.name))
            if not self.test(user_value):
                user_value = None
            else:
                if (not self.domain is None and not user_value in self.domain):
                    user_value = None
                    print("Please enter a valid {} from the following domain:\n{}".format(self.name,self.domain))
        self.user_value = self.process(user_value)
        os.environ[self.name] = user_value
        print("value for {} set to {}".format(self.name,self.user_value))
        print('#-------------------')
        return self.user_value

def build_venv(env_dir):
    #Make the Virtual enviroment folder
    safe_mkdir(env_dir)
    if os.path.exists(os.path.join(env_dir,'.env')):
        print("""
        !!!!!!WARNING!!!!!!
        This folder already contains a .env directory
        This will be deleted if you continue
        """)
        answer = ''
        while not answer.lower() in ['n','y']:
            answer = input('Would you like to continue (y/n)? ')
        if answer.lower() =='n':
            return

    #Build the Virtual enviroment and set the required user variables
    venv.create(os.path.join(env_dir,'.env'),with_pip = True,symlinks = True, clear = True)
    shell = os.getenv('SHELL','')
    rcpath = os.path.join(env_dir,'.env/bin/activate')
    user_vars_dict = get_user_enviroment_vars()
    user_vars_dict['CATALOG_LOC'] = env_dir
    set_user_enviromental_vars(rcpath,        user_vars_dict)
    set_user_enviromental_vars(rcpath+'.csh', user_vars_dict)

    #Pip install the required packages
    python_exec = os.path.join(env_dir,'.env/bin/python')
    os.system("{} -m pip install pip --upgrade --no-cache-dir".format(python_exec))
    os.system("{} -m pip install numpy --upgrade --no-cache-dir".format(python_exec))
    os.system("{} -m pip install CC-CataLog --upgrade --no-cache-dir".format(python_exec))

    # #Add the fireworks folder and the required sub-directories
    add_fireworks_folders(user_vars_dict)

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
        echo 'alias cata_src="source $CATALOG_LOC/.env/bin/activate"' >> ~/.bash_profile
        """.format(env_dir))
    elif 'tcsh' in shell:
        print("""
        !!!!!!IMPORTANT!!!!!
        NEED TO DO ONE MORE THING
        PLEASE RUN THIS COMMAND
        echo setenv CATALOG_LOC {}>>~/.cshrc

        To Source this enviroment in the future use the command:
        source $CATALOG_LOC/.env/activate.csh
        or you can alias it:
        echo 'alias cata_src "source $CATALOG_LOC/.env/bin/activate.csh"' >> ~/.cshrc
        """.format(env_dir))

def get_user_enviroment_vars():
    #Set of required user-defined variables
    def file_exist_test(file_curr):
        if os.path.exists(file_curr):
            return True
        else:
            print("{} does not exist".format(file_curr))
            return False
    user_vars = [UserDefinedVariable(name = "USER"
                                    ,desc = "Generic username used as default for new clusters"
                                    )
                ,UserDefinedVariable(name = "SHERLOCK2_USERNAME"
                                    ,desc = "Username for Sherlock2 cluster"
                                    ,)
                ,UserDefinedVariable(name = "SUNCAT_USERNAME"
                                    ,desc = "Username for Suncat Cluster"
                                    )
                ,UserDefinedVariable(name   = "HOSTNAME"
                                    ,desc   = "Name of current cluster (sherlock, suncat, local"
                                    ,domain = ['sherlock','local','suncat']
                                    )
                ,UserDefinedVariable(name   = "LAUNCHPAD_YAML"
                                    ,desc   = "Path to your my_launchpad.yaml file, relative paths are fine\nIf you don't have a fireworks database yet please get one."
                                    ,test   = file_exist_test
                                    ,process = lambda file_curr: os.path.abspath(file_curr)
                                    )
                ,UserDefinedVariable(name   = "DB_JSON"
                                    ,desc   = "Path to your SQL database credentials json."
                                    ,test   = file_exist_test
                                    ,process = lambda file_curr: os.path.abspath(file_curr)
                                    )
                ]
    user_vars_dict = {} # type: dict
    #Print a description of each variable and ask the user for input
    for user_var in user_vars:
        user_vars_dict[user_var.name] = user_var.get_user_val()
    return user_vars_dict

def set_user_enviromental_vars(rcpath,user_vars_dict):
    with open(rcpath,'a') as f:
        f.write("#####################\n")
        f.write("#Catalog enviromental variables\n")
        f.write("#####################\n")
        if rcpath.endswith('csh'):
            f.write("setenv PYTHONPATH {}:$PYTHONPATH\n".format(user_vars_dict['CATALOG_LOC']))
            for key,val in user_vars_dict.items():
                f.write("setenv {} {}\n".format(key,val))
        else:
            f.write("export PYTHONPATH={}:$PYTHONPATH\n".format(user_vars_dict['CATALOG_LOC']))
            for key,val in user_vars_dict.items():
                f.write("export {}={}\n".format(key,val))

def add_fireworks_folders(user_vars_dict):
    #Make all the necessary folders
    safe_mkdir(os.path.join(user_vars_dict['CATALOG_LOC'],'fireworks'))
    safe_mkdir(os.path.join(user_vars_dict['CATALOG_LOC'],'fireworks','jobs'))
    safe_mkdir(os.path.join(user_vars_dict['CATALOG_LOC'],'fireworks','FW_CONFIG_DIR'))
    safe_mkdir(os.path.join(user_vars_dict['CATALOG_LOC'],'fireworks','logs'))

    #Make a FW_config.yaml
    with open(os.path.join(user_vars_dict['CATALOG_LOC'],'fireworks','FW_config.yaml'),'w') as f:
        f.write('ALWAYS_CREATE_NEW_BLOCK: True')

    #Copy the DB_JSON file
    shutil.copy(user_vars_dict['DB_JSON'],os.path.join(user_vars_dict['CATALOG_LOC'],'fireworks','DB.json'))

    #Fill the FW_CONFIG_DIR with my_launchpad, my_fworker, and my_qadapter
    #Copy the launchpad_yaml
    shutil.copy(user_vars_dict['LAUNCHPAD_YAML'],os.path.join(user_vars_dict['CATALOG_LOC'],'fireworks','FW_CONFIG_DIR','my_launchpad.yaml'))


    #Write the my_fworker.yaml
    with open(os.path.join(user_vars_dict['CATALOG_LOC'],'fireworks','FW_CONFIG_DIR','my_fworker.yaml'),'w') as f:
        f.write("name: {}\n".format(user_vars_dict['HOSTNAME'].replace('sherlock','sherlock2')))
        f.write("category: ''\n")
        f.write("query: '{}'\n")

    if not user_vars_dict['HOSTNAME'] == 'local':
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
        template_file = glob('{}/.env/lib/*/site-packages/catalog/fw/qadapter_templates/{}'.format(user_vars_dict['CATALOG_LOC'],template_dict[queue_system]))[0]

        qtype_dict    = {'LSF'   : 'LoadSharingFacility'
                        ,'PBS'   : 'PBS'
                        ,'SLURM' : 'SLURM'
                        ,'None'  : 'null'}

        with open(os.path.join(user_vars_dict['CATALOG_LOC'],'fireworks','FW_CONFIG_DIR','my_qadapter.yaml'),'w') as f:
            f.write("_fw_name: CommonAdapter\n")
            f.write("_fw_q_type: {}\n".format(qtype_dict[queue_system]))
            f.write("_fw_template_file: {}\n".format(template_file))
            f.write("queue: {}\n".format(user_vars_dict['HOSTNAME'].replace('sherlock2','iric')))
            f.write("rocket_launch: rlaunch -c $CATALOG_LOC/FW_CONFIG_DIR singleshot\n")

        #Copy the launcher function to the fireworks folder
        with open(os.path.join(user_vars_dict['CATALOG_LOC'],'fireworks','launcher.sh'),'w') as f:
            f.write("#!/bin/bash\n")
            f.write("cd $CATALOG_LOC/fireworks\n")
            f.write("source $CATALOG_LOC/.env/bin/activate\n")
            f.write("$CATALOG_LOC/.env/bin/qlaunch -c $CATALOG_LOC/fireworks/FW_CONFIG_DIR --logdir $CATALOG_LOC/fireworks/logs -r rapidfire\n")
        os.chmod(os.path.join(user_vars_dict['CATALOG_LOC'],'fireworks','launcher.sh'),0o755)

def safe_mkdir(dir_path):
    if not os.path.exists(dir_path):
        os.mkdir(dir_path)

if __name__ == '__main__':
    env_dir2 = input('Please enter the path you would like to put the CataLog enviroment\n(Please choose an empty or non-existent folder): ')
    env_dir2 = os.path.abspath(env_dir2)
    build_venv(env_dir2)
