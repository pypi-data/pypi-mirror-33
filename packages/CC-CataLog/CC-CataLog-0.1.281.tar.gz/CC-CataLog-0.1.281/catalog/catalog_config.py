#External imports
import os

#Internal Imports
"""
This file contains the enviromental variables and job submission settings
"""

###################
#AUTO-GENERATED KEYS
###################


###################
#USER SPECIFIED KEYS
###################
"""
Current required enviromental variables:
    - USER
        The name the user wants to use as default login to new clusters
    - HOSTNAME
        The name of the machine used to identify the cluster please use 'local'
        for non-job running machines
    - SHERLOCK2_USERNAME
        Login name for sherlock2
    - SUNCAT_USERNAME
        Login name for suncat,suncat2, and suncat3
    - LAUNCHPAD_YAML
        path to the launchpad yaml to load the fireworks launchpad
"""
CATALOG_LOC = os.getenv('CATALOG_LOC')
assert not CATALOG_LOC == None, 'MISSING ENVIROMENTAL VARIABLE: CATALOG_LOC'

USER = os.getenv('USER')
assert not USER == None, 'MISSING ENVIROMENTAL VARIABLE: USER'

HOSTNAME     = os.getenv('HOSTNAME')
assert not HOSTNAME == None, 'MISSING ENVIROMENTAL VARIABLE: HOSTNAME'

#Sherlock2 Keys
###############
SHERLOCK2_USERNAME = os.getenv('SHERLOCK2_USERNAME')
assert not SHERLOCK2_USERNAME == None, 'MISSING ENVIROMENTAL VARIABLE: SHERLOCK2_USERNAME'

#Suncat Keys
###############
SUNCAT_USERNAME = os.getenv('SUNCAT_USERNAME')
assert not SUNCAT_USERNAME == None, 'MISSING ENVIROMENTAL VARIABLE: SUNCAT_USERNAME'

#Fireworks keys
###############
LAUNCHPAD_YAML   = os.path.join(CATALOG_LOC,'fireworks','FW_CONFIG_DIR','my_launchpad.yaml')
assert not LAUNCHPAD_YAML == None, 'MISSING ENVIROMENTAL VARIABLE: LAUNCHPAD_YAML'


# ######################
# # Job Submission Settings
# # --------------------

def allocate(job,n):
    """
    Take in a Job object and an integer, n. Return a list of n Cluster objects.
    """
    return ['suncat']

def guessTime(job) -> int:
    return 50

def guessNodes(job) -> int:
    return 1
