#!/bin/bash
source /scratch/users/$USER/CataLog/.env/bin/activate
cd $FIREWORKS_FOLDER

$CATALOGPATH/.env/bin/qlaunch -w $FIREWORKS_FOLDER/my_fworker2.yaml -r rapidfire
