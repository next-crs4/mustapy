#!/bin/bash
PARAMS=""

WORKDIR=""
INDIR=""
SAMPLESFILE=""

help_flag=0

while [ "$1" != "" ]; do

case $1 in
  -h | --help)
    PARAMS="${PARAMS} $1"
    help_flag=1
    shift
  ;;
  -w | --workdir)
    shift
    WORKDIR=$1
    shift
  ;;
  -i | --inputs)
    shift
    INDIR=$1
    shift
  ;;
  -s | --samples)
    shift
    SAMPLESFILE=$1
    shift
  ;;
  *)
    PARAMS="${PARAMS} $1"
    shift

esac
done


[  -z "$WORKDIR" ] && [ $help_flag -eq 0 ] && echo "ERROR: -w | --workdir is a mandatory argument" && exit 1
[  ! -d "$WORKDIR" ] && [ $help_flag -eq 0 ] && echo "WARNING: ${WORKDIR} does not exist or is not a directory. Trying to create it." && mkdir -p $WORKDIR
[  ! -z "$INDIR" ] && [  ! -d "$INDIR" ] && [ $help_flag -eq 0 ] && echo "ERROR: ${INDIR} does not exist or is not a directory.  Exiting..." && exit 1
[  ! -z "$SAMPLESFILE" ] && [  ! -f "$SAMPLESFILE" ] && [ $help_flag -eq 0 ] && echo "ERROR: ${SAMPLESFILE} does not exist or is not a file.  Exiting..." && exit 1
#[  -d "$WORKDIR" ] && [ $help_flag -eq 0 ] && [ ! -z "$(ls -A ${WORKDIR})" ] && echo "ERROR: ${WORKDIR}  is not empty. Exiting..." && exit 1

CMD="docker run "

[ $help_flag -eq 0 ] && CMD="${CMD} -v ${WORKDIR}:/volumes/workdir"

[ $help_flag -eq 0 ] && [ -f "$SAMPLESFILE" ] && CMD="${CMD} -v ${SAMPLESFILE}:/volumes/workdir/samples.yml"
[ $help_flag -eq 0 ] && [ -d "$INDIR" ] && CMD="${CMD} -v ${INDIR}:/volumes/workdir/inputs/samples.yml"

CMD="${CMD} musta:Dockerfile musta ${PARAMS}"
eval $CMD