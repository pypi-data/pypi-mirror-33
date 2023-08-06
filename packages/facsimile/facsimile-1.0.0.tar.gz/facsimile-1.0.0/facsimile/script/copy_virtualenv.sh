#!/bin/bash
################################################################################

function die_usage
  {
  test -n "$1" && echo $1
  echo "usage copy_virtualenv.sh <source> <destination dir> <new fq path>"
  exit 1
  }

src=$1
dst=$2
path=$3

################################################################################

if test -z "$src"; then
  die_usage
fi

if test -z "$dst"; then
  die_usage
fi

if test -z "$path"; then
  die_usage
fi

if ! test -d "$src"; then
  die_usage "source dir '$src' not found"
fi

# clean up
find $src -type f -name \*.pyc -exec rm {} \;
find $src -type f -name \*.pyo -exec rm {} \;

envdir=`basename $src`

# get virtual env path from activate
eval `grep VIRTUAL_ENV= $src/bin/activate`

# copy
rsync -a --delete $src $dst


# rewrite path in files
find $dst -type f -exec sed --in-place -e "s,$VIRTUAL_ENV,$path,g" {} \;

# fix lib64 symlink
rm $dst/$envdir/lib64
ln -s lib $dst/$envdir/lib64

