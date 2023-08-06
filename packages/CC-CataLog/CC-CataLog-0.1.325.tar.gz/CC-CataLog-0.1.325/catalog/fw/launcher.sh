#!/bin/bash
source $CATALOG_LOC/.env/bin/activate
cd $CATALOG_LOC/fireworks/FW_CONFIG_DIR
$CATALOG_LOC/.env/bin/qlaunch -c $CATALOG_LOC/fireworks/FW_CONFIG_DIR --logdir $CATALOG_LOC/fireworks/logs -r rapidfire
