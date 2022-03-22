#!/bin/bash
PARAMS=()

INDIR=""
OUTDIR=""
WORKDIR=""
REFDIR=""
SAMPLESFILE=""

in_flag=0
out_flag=0
ref_flag=0
work_flag=0
samples_flag=0


showError() {
# `cat << EOF` This means that cat should stop reading when EOF is detected
cat << EOF
Please, be careful. Input & Output files must be:

EOF
# EOF is found above and hence cat command stops reading. This is equivalent to echo but much neater when printing out.
}

for i in "$@"
do
case $i in
  -h | --help)
  docker run musta:Dockerfile musta --help
  exit 0
  ;;
  -o |--output-dir)
  out_flag=1
  shift
  ;;
  -i |--input-dir)
  in_flag=1
  shift
  ;;
  -w |--work-dir)
  work_flag=1
  shift
  ;;
  -r |--reference-dir)
  ref_flag=1
  shift
  ;;
  -s |--samples)
  samples_flag=1
  shift
  ;;
  *)
  if [ $out_flag -eq 1 ];
  then
    OUTDIR=$(readlink -m "$1")
    out_flag=0
  elif [ $in_flag -eq 1 ];
  then
    INDIR=$(readlink -m "$1")
    in_flag=0
  elif [ $ref_flag -eq 1 ];
  then
    REFDIR=$(readlink -m "$1")
    ref_flag=0
  elif [ $work_flag -eq 1 ];
  then
    WORKDIR=$(readlink -m "$1")
    work_dir=0
  elif [ $samples_flag -eq 1 ];
  then
    SAMPLESFILE=$(readlink -m "$1")
    samples_flag=0
  else
    PARAMS+=" "$i
  fi
  shift
  ;;
esac
done

[[  -z "$INDIR" ]] && echo "ERROR: -i | --input-dir is a mandatory argument"; exit 1;
[[  -z "$OUTDIR" ]] && echo "ERROR: -o | --output-dir is a mandatory argument"; exit 1;
[[  -z "$WORKDIR" ]] && echo "ERROR: -w | --work-dir is a mandatory argument"; exit 1;
[[  -z "$REFDIR" ]] && echo "ERROR: -r | --reference-dir is a mandatory argument"; exit 1;
[[  -z "$SAMPLESFILE" ]] && echo "ERROR: -s | --samples-file is a mandatory argument"; exit 1;

[[  ! -d "$INDIR" ]] && echo "ERROR: ${INDIR} does not exist or is not a directory"; exit 1;
[[  ! -d "$OUTDIR" ]] && echo "ERROR: ${OUDIR} does not exist or is not a directory"; exit 1;
[[  ! -d "$REFDIR" ]] && echo "ERROR: ${REFDIR} does not exist or is not a directory"; exit 1;
[[  ! -d "$WORKDIR" ]] && echo "ERROR: ${WORKDIR} does not exist or is not a directory"; exit 1;

docker run -v \
$(echo "$INDIR"):/volumes/inputs \
$(echo "$OUTDIR"):/volumes/ouputs \
$(echo "$REFDIR"):/volumes/references \
$(echo "$SAMPLESFILE"):/volumes/samples.yml \
musta:Dockerfile musta \

$(echo $PARAMS)