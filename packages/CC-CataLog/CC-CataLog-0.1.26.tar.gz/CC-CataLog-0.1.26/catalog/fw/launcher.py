#Typing imports
import typing as typ

#External imports
from fireworks.queue.queue_launcher import rapidfire # type: ignore
import os

#Internal Imports
from catalog.fw.incomplete import lpad
from catalog.jobs.cluster import Cluster, cluster_dict
from catalog.catalog_config import HOSTNAME

def launch(clust_str : str = get_cluster()):
    cluster = cluster_dict[clust_str]
    rapidfire(lpad, cluster.fworker, cluster.qadapter, launch_dir=os.path.join(CATALOG_LOC,'fireworks','FW_CONFIG_DIR'))

if __name__ == '__main__':
    launch(HOSTNAME)
