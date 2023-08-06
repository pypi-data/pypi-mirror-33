#!/bin/bash
################################################################################
# cd to <source dir> and install all requirements to <target>
# expects <source dir>/requirements.txt to exist

function die_usage
  {
  test -n "$1" && echo $1
  echo "usage make_virtualenv.sh <source dir> <target> [requirements_file]"
  exit 1
  }

VENV_OPTS="--clear --prompt='' "
PIP_OPTS='--allow-external wadofstuff-django-serializers --allow-unverified wadofstuff-django-serializers '
PIP_OPTS=''

################################################################################

source_dir=$1
target=$2
requirements=$3


if test -z "$source_dir"; then
  die_usage
fi

if test -z "$target"; then
  die_usage
fi

if test -z "$requirements"; then
  requirements="$source_dir/requirements.txt"
fi

if ! test -d "$source_dir"; then
  die_usage "source dir '$source_dir' not found"
fi

if ! test -f "$requirements"; then
  die_usage "requirements $source_dir/requirements.txt not found"
fi

virtualenv $VENV_OPTS $target

if [ "$?" -ne "0" ]; then
  echo "Could not create env, $target: $?"
    exit 1
fi

BASEDIR=`pwd`/$(dirname $0)

source $target/bin/activate

if [ "$?" -ne "0" ]; then
  echo "Could not activate env, $target: $?"
    exit 1
fi

if [ "$3" = "USE_CCACHE" ]
then
  echo ">>>>>>>>>>>>>> Attempting to use ccache for speedups in compile. <<<<<<<<<<<<<<"
  
  hash ccache 2>/dev/null
  if [ $? -gt 0 ]
  then
    echo "Cannot use ccache, it's not installed. Skipping ccache step."
  else
    CCA=`which ccache`
    if [ ! -h $BASEDIR/g++ ]
    then
      ln -s $CCA $BASEDIR/g++
    fi
    if [ ! -h $BASEDIR/gcc ]
    then
      ln -s $CCA $BASEDIR/gcc
    fi
    if [ ! -h $BASEDIR/cc ]
    then
      ln -s $CCA $BASEDIR/cc
    fi
    if [ ! -h $BASEDIR/c++ ]
    then
      ln -s $CCA $BASEDIR/c++
    fi
    export PATH=$BASEDIR:${PATH}
    echo ">>> compilation search path is now $PATH"
  fi
fi

cd $source_dir
pip install $PIP_OPTS -r $requirements
rv=$?
if [ "$rv" -ne "0" ]; then
  echo "pip install failed: $rv"
  exit 1
fi

# clean up
find $target/ -type f -name \*.pyc -exec rm {} \;
find $target/ -type f -name \*.pyo -exec rm {} \;

