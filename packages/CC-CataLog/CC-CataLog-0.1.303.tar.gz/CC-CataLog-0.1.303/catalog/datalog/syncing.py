#Typing imports
import typing as typ

#External imports
import os

#Internal Imports
from dbgen.main import load_jobs

user = os.environ['USER']

#####################
# Sync Clusters
# -------------------

def sync_suncat()->None:
    print('Syncing /nfs/slac/g/suncatfs/ksb/share/jobs to /scratch/users/ksb/share/suncat_jobs_copy/ ...')
    slac  = '%s@suncatls1.slac.stanford.edu:/nfs/slac/g/suncatfs/ksb/share/jobs'%user
    sher  = '/scratch/users/ksb/share/suncat_jobs_copy/'
    rsync = 'rsync -rtqvu --perms --chmod=F777 --omit-dir-times %s %s  --delete'%(slac,sher)
    ssh   = 'ssh %s@login.sherlock.stanford.edu '%user
    os.system(ssh + rsync)

def sync_nersc()->None:
    print('Syncing /global/cscratch1/sd/krisb/share/jobs to /scratch/users/ksb/share/nersc_jobs_copy/ ...')
    os.system('rsync -rtqvu --perms --chmod=777 --omit-dir-times krisb@cori.nersc.gov:/global/cscratch1/sd/krisb/share/jobs /scratch/users/ksb/share/nersc_jobs_copy/ --delete')

#####################
# Load Database
# -------------------
def load_jobs_catalog(parallel : bool = True)-> None:
    sync_suncat()
    load_jobs(catalog  = True
             ,parallel = parallel
             ,only     = """
                         populate_catalog_job

                         update_job_metadata
                         populate_relax_job
                         populate_subjobs

                         populate_relax_calc
                         populate_calc_other
                         kptden

                         populate_struct_traj_atom_cell
                         update_system_type
                         populate_substructs

                         pop_struct_catalog
                         pop_ads_catalog
                         pop_bulk_struct_catalog
                         pop_surf_struct_catalog
                         """)
