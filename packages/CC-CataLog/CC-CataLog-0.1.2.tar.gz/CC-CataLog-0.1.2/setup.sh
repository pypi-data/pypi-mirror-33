#!/bin/sh
#Setup script for CataLog on Scratch

#1. Creates Virtual Enviroment
#2. Installs necessary packages
#3. Creates necessary enviromental variables

export CATALOGPATH="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

build_venv(){
  python3 -m venv $CATALOGPATH/.env
  export VIRTUALENV_RC=$CATALOGPATH/.env/bin/activate
  set_enviromental_variable(){
    printf -n "Set Enviromental Variable ${1}: "
    read path
    echo "${1} set to ${path}"
    echo export $1=$path>>$VIRTUALENV_RC
  }


  echo "###############################">>$VIRTUALENV_RC
  echo "#CataLog Enviromental Variables">>$VIRTUALENV_RC
  echo "###############################">>$VIRTUALENV_RC
  set_enviromental_variable USER
  set_enviromental_variable HOSTNAME
  set_enviromental_variable LAUNCHPAD_YAML
  set_enviromental_variable FIREWORKS_FOLDER
  set_enviromental_variable SHERLOCK2_USERNAME
  set_enviromental_variable SUNCAT_USERNAME
  echo "###############################"
  echo "All Enviromental Variables set in ${VIRTUALENV_RC}"
  echo "Please modify that file to change enviromental variabes in the future"

  echo export CATALOGPATH=$CATALOGPATH>>$VIRTUALENV_RC
  echo export PYTHONPATH="$( dirname $CATALOGPATH )":\$PYTHONPATH>>$VIRTUALENV_RC
  source $CATALOGPATH/.env/bin/activate

  #Install required python packages
  pip install CC-CataLog
}

if [ ! -d $CATALOG/.env ];
then
  build_venv
else
  echo "Virtual Enviroment already built!"
fi
