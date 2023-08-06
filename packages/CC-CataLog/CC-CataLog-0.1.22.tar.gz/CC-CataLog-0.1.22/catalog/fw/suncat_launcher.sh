#!/bin/bash
source /u/if/$USER/CataLog/.env/bin/activate
cd $FIREWORKS_FOLDER

$CATALOGPATH/.env/bin/qlaunch -r rapidfire
