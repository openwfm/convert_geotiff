#!/bin/bash

exe=${exe:-'../../../convert_geotiff'}

# Options:
# -h         : Show this help message and exit
# -c NUM     : Indicates categorical data (NUM = number of categories)
# -b NUM     : Tile border width (default 3)
# -w [1,2,4] : Word size in output in bytes (default 2)
# -z         : Indicates unsigned data (default FALSE)
# -t NUM     : Output tile size (default 100)
# -s SCALE   : Scale factor in output (default 1.)
# -m MISSING : Missing value in output (default 0., ignored for categorical data)
# -u UNITS   : Units of the data (default "NO UNITS")
# -d DESC    : Description of data set (default "NO DESCRIPTION")

success=${success:-0}

function runandcheck {
  dir=$(basename $1 .tif)
  mkdir ${dir}
  pushd ${dir} > /dev/null
  r="${exe} ${cat} ${word} ${signed} ${tilesize} ${scale} ${missing} ${units} ${desc} ../${1}"
  eval $r
  if [ $? -ne 0 ] ; then
      echo "FAILED: $r"
      ((success++))
  fi
  popd > /dev/null
  rm -fr ${dir}
}

function runandcheckall {
  for f in *.tif ; do 
    runandcheck $f
  done
}

runandcheckall

units='-u myunits'
desc='-d "This is a description"'
for w in 1 2 4 ; do
word="-w $w"
for signed in ' ' '-z' ; do
for ts in 10 ; do
tilesize="-t $ts"
for sc in 0.5 2.0 ; do
scale="-s $sc"
for m in 100 ; do
missing="-m $m"
runandcheckall
done
done
done
done
done
exit $success
