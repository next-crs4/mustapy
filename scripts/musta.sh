#!/bin/bash
PARAMS=""

WORKDIR=""
SAMPLESFILE=""

help_flag=0

while [ "$1" != "" ]; do

case $1 in
  -h | --help)
    PARAMS="${PARAMS} $1"
    help_flag=1
    shift
  ;;
  -w | --work-dir)
    shift
    WORKDIR=$1
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
[  ! -d "$WORKDIR" ] && [ $help_flag -eq 0 ]&& echo "WARNING: ${WORKDIR} does not exist or is not a directory. Trying to create it." && mkdir -p $WORKDIR

CMD="docker run "

[ $help_flag -eq 0 ] && CMD="${CMD} -v ${WORKDIR}:/volumes/workdir"

[ $help_flag -eq 0 ] && [ -f "$SAMPLESFILE" ] && CMD="${CMD} -v ${SAMPLESFILE}:/volumes/samples.yml"

CMD="${CMD} musta:Dockerfile musta ${PARAMS}"
echo $CMD
eval $CMD