#External imports
import os

#Internal Imports
"""
This file contains the enviromental variables and job submission settings
"""

###################
#AUTO-GENERATED KEYS
###################
CATALOGPATH  = os.path.dirname(os.path.abspath(__file__))

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
    - FIREWORKS_FOLDER
        Folder to launch jobs from
    - LAUNCHPAD_YAML
        path to the launchpad yaml to load the fireworks launchpad
"""

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
FIREWORKS_FOLDER = os.getenv('FIREWORKS_FOLDER')
assert not FIREWORKS_FOLDER == None, 'MISSING ENVIROMENTAL VARIABLE: FIREWORKS_FOLDER'
LAUNCHPAD_YAML   = os.getenv('LAUNCHPAD_YAML')
assert not FIREWORKS_FOLDER == None, 'MISSING ENVIROMENTAL VARIABLE: LAUNCHPAD_YAML'


# ######################
# # Job Submission Settings
# # --------------------

def allocate(job,n):
    """
    Take in a Job object and an integer, n. Return a list of n Cluster objects.
    """
    return ['sherlock2']

def guessTime(job) -> int:
    return 36

def guessNodes(job) -> int:
    return 2
