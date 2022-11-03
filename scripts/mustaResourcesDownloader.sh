#!/bin/bash

OUTDIR=""

# PARSE ARGS
while [ "$1" != "" ]; do

case $1 in
  -h | --help)
    shift
  ;;
  -o | --outdir)
    shift
    OUTDIR=$1
    shift
  ;;
esac
done

# CHECK ARGS
[  -z "$OUTDIR" ] \
&& echo "ERROR: -w | --workdir is a mandatory argument" && exit 1

[  ! -d "$OUTDIR" ] \
&& echo "WARNING: ${WORKDIR} does not exist or is not a directory. Trying to create it." \
&& mkdir -p $OUTDIR


CMD="docker run "
CMD="${CMD} -v ${OUTDIR}:/volumes/datasource"
CMD="${CMD} musta:Dockerfile"
CMD="${CMD} gatk FuncotatorDataSourceDownloader --somatic --validate-integrity --extract-after-download --output /volumes/datasource"

echo $CMD
eval $CMD
