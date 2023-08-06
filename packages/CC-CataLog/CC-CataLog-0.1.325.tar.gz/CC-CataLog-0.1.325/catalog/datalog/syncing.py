#Typing imports
import typing as typ

#External imports
import os

#Internal Imports
from dbgen.main import load_jobs as l_j
from catalog.catalog_config import SHERLOCK2_USERNAME,SUNCAT_USERNAME, USER

"""
Features:
- Syncing suncat -> sherlock
- Loading database (from local machine)
To do:
- underlying file system periodic backup
"""

################################################################################
# Sync Clusters
# -------------------

def sync_suncat()->None:
    print('Syncing /nfs/slac/g/suncatfs/ksb/share/jobs to /scratch/users/ksb/share/suncat_jobs_copy/ ...')
    slac  = '%s@suncatls1.slac.stanford.edu:/nfs/slac/g/suncatfs/ksb/share/jobs/%s/'%(SUNCAT_USERNAME,USER)
    sher  = '/scratch/users/ksb/share/suncat_jobs_copy/jobs/%s/'%(USER)
    rsync = 'rsync -rtqvu --perms --chmod=777 --omit-dir-times %s %s  --delete'%(slac,sher)
    ssh   = 'ssh %s@login.sherlock.stanford.edu '%SHERLOCK2_USERNAME
    os.system(ssh + rsync)

def sync_nersc()->None:
    print('Syncing /global/cscratch1/sd/krisb/share/jobs to /scratch/users/ksb/share/nersc_jobs_copy/ ...')
    os.system('rsync -rtqvu --perms --chmod=777 --omit-dir-times krisb@cori.nersc.gov:/global/cscratch1/sd/krisb/share/jobs /scratch/users/ksb/share/nersc_jobs_copy/ --delete')

#####################
# Load Database
# -------------------
def load_jobs(parallel : bool = True)-> None:
    sync_suncat()
    l_j(parallel = parallel
        ,catalog = True
        ,only    = """
                     catalog

                     metadata
                     anytraj
                     relax_job
                     subjobs

                     calc
                     calc_other
                     kptden

                     traj
                     systype
                     substructs

                     pop_struct_catalog
                     pop_ads_catalog
                     pop_bulk_struct_catalog
                     pop_surf_struct_catalog
                     """)
def ads_triple()->None:
    l_j(only = "ads_triple")
