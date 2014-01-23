#!/bin/sh

OSS="`uname -s`"

if [ $OSS == 'Linux']; then
  VENV='venv/bin/activate'
elif [ $OSS == 'Mac']; then
  VENV='venv/bin/activate'
else
  VENV='venv/Scripts/activate'
fi

rm -Rf build/ dist/ mogwai.egg-info
source $VENV && echo -e 'y\n' | pip uninstall mogwai
source $VENV && nosetests -vv --attr=unit
