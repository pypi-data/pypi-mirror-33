#!/bin/bash
source $CATALOG_LOC/.env/bin/activate
$CATALOG_LOC/.env/bin/qlaunch -c $CATALOG_LOC/fireworks/FW_CONFIG_DIR --logdir $CATALOG_LOC/fireworks/logs -r rapidfire
