#!/bin/bash
PARAMS=""

TMPDIR=""
WORKDIR=""
RESOURCESDIR=""
DATASOURCEDIR=""
SAMPLESFILE=""
REFERENCE=""
BEDFILE=""
GERMLINEFILE=""
VARIANTFILE=""
DBSNPFILE=""
help_flag=0

CMD="docker run "

# PARSE ARGS
while [ "$1" != "" ]; do

case $1 in
  -h | --help)
    PARAMS="${PARAMS} $1"
    help_flag=1
    shift
  ;;
  -t | --tmpdir)
    shift
    TMPDIR=$1
    shift
  ;;
  -w | --workdir)
    shift
    WORKDIR=$1
    shift
  ;;
  -ds | --data-source)
    shift
    DATASOURCEDIR=$1
    shift
  ;;
  -rd | --resources-dir)
    shift
    RESOURCESDIR=$1
    shift
  ;;
  -r | --reference-file)
    shift
    REFERENCE=$1
    REFDIR=$(dirname "$REFERENCE")
    REFNAME=$(basename "$REFERENCE" | sed 's/\(.*\)\..*/\1/')
    shift
  ;;
  -b | --bed-file)
    shift
    BEDFILE=$1
    shift
  ;;
  -db | --dbsnp-file)
    shift
    DBSNPFILE=$1
    shift
  ;;
  -v | --variant-file)
    shift
    VARIANTFILE=$1
    shift
  ;;
  -g | --germline-resource)
    shift
    GERMLINEFILE=$1
    shift
  ;;
  -s | --samples-file)
    shift
    SAMPLESFILE=$1
    shift
  ;;
  *)
    PARAMS="${PARAMS} $1"
    shift

esac
done

# CHECK ARGS
[  -z "$WORKDIR" ] && [ $help_flag -eq 0 ] && [ -z "$RESOURCESDIR" ] \
&& echo "ERROR: -w | --workdir is a mandatory argument" && exit 1

[  ! -d "$WORKDIR" ] && [ $help_flag -eq 0 ] && [ -z "$RESOURCESDIR" ] \
&& echo "WARNING: ${WORKDIR} does not exist or is not a directory. Trying to create it." && mkdir -p $WORKDIR

[  ! -z "$RESOURCESDIR" ] && [  ! -d "$RESOURCESDIR" ] \
&& echo "WARNING: ${RESOURCESDIR} does not exist or is not a directory. Trying to create it." && mkdir -p $RESOURCESDIR

[  ! -z "$TMPDIR" ] && [  ! -d "$TMPDIR" ] \
&& [ $help_flag -eq 0 ] && echo "WARNING: ${TMPDIR} does not exist or is not a directory. Trying to create it." && mkdir -p $TMPDIR

[  ! -z "$TMPDIR" ] && [  ! -d "$TMPDIR" ] \
&& [ $help_flag -eq 0 ] && echo "WARNING: ${DATASOURCEDIR} does not exist or is not a directory.  Exiting..." && exit 1


[  ! -z "$SAMPLESFILE" ] && [  ! -f "$SAMPLESFILE" ] \
&& [ $help_flag -eq 0 ] && echo "ERROR: ${SAMPLESFILE} does not exist or is not a file.  Exiting..." && exit 1

[  ! -z "$REFERENCE" ] && [  ! -f "$REFERENCE" ] \
&& [ $help_flag -eq 0 ] && echo "ERROR: ${REFERENCE} does not exist or is not a file.  Exiting..." && exit 1

[  ! -z "$REFERENCE" ] && [  -f "$REFERENCE" ] && [ ! -f "${REFERENCE}.fai" ] \
&& [ $help_flag -eq 0 ] && echo "ERROR:  Fasta index file (.fai) for reference ${REFERENCE} does not exist." \
&& echo "Please see https://github.com/broadinstitute/gatk-docs/blob/master/gatk3-faqs/How_can_I_prepare_a_FASTA_file_to_use_as_reference%3F.md for help creating it." \
&& echo "Exiting..." \
&& exit 1

[  ! -z "$REFERENCE" ] && [  -f "$REFERENCE" ] && [ ! -f "${REFDIR}/${REFNAME}.dict" ] \
&& [ $help_flag -eq 0 ] && echo "ERROR:  Fasta dict file (.dict) for reference ${REFERENCE} does not exist." \
&& echo "Please see https://github.com/broadinstitute/gatk-docs/blob/master/gatk3-faqs/How_can_I_prepare_a_FASTA_file_to_use_as_reference%3F.md for help creating it." \
&& echo "Exiting..." \
&& exit 1

[  ! -z "$BEDFILE" ] && [  ! -f "$BEDFILE" ] \
&& [ $help_flag -eq 0 ] && echo "ERROR: ${BEDFILE} does not exist or is not a file.  Exiting..." && exit 1

if [ ! -z "$BEDFILE" ] && [  -f "$BEDFILE" ] && [ $help_flag -eq 0 ]; then
  filename=$(basename $BEDFILE)
  extension="${filename##*.}"
  if [ $extension == 'vcf' ]; then
    echo "ERROR: BED file is not compressed" && \
    echo "Please compress and index your bed file: bgzip -c  ${line} > ${line}.gz && tabix -p bed ${line}.gz" && \
    echo "See: https://www.biostars.org/p/59492/" && \
    echo "Exiting..." && exit 1
  fi
fi

[  ! -z "$BEDFILE" ] && [  -f "$BEDFILE" ] && [ ! -f "${BEDFILE}.tbi" ]  \
&& [ $help_flag -eq 0 ] && echo "ERROR:  An index file (.tbi) is required but was not found for file ${BEDFILE}" \
&& echo "Please compress and index your bed file: tabix -p bed ${BEDFILE}" \
&& echo "See: https://www.biostars.org/p/59492/" \
&& echo "Exiting..." && exit 1

[  ! -z "$GERMLINEFILE" ] && [  ! -f "$GERMLINEFILE" ] \
&& [ $help_flag -eq 0 ] && echo "ERROR: ${GERMLINEFILE} does not exist or is not a file.  Exiting..." && exit 1

[  ! -z "$GERMLINEFILE" ] && [  -f "$GERMLINEFILE" ] && [ ! -f "${GERMLINEFILE}.idx" ] \
&& [ $help_flag -eq 0 ] && echo "ERROR:  An index file (.idx) is required but was not found for file ${GERMLINEFILE}" \
&& echo " Try running gatk IndexFeatureFile on the input. See: https://gatk.broadinstitute.org/hc/en-us/articles/5358901172891-IndexFeatureFile" \
&& echo "Exiting..." && exit 1

[  ! -z "$VARIANTFILE" ] && [  ! -f "$VARIANTFILE" ] \
&& [ $help_flag -eq 0 ] && echo "ERROR: ${VARIANTFILE} does not exist or is not a file.  Exiting..." && exit 1

[  ! -z "$VARIANTFILE" ] && [  -f "$VARIANTFILE" ] && [ ! -f "${VARIANTFILE}.idx" ] \
&& [ $help_flag -eq 0 ] && echo "ERROR:  An index file (.idx) is required but was not found for file ${VARIANTFILE}" \
&& echo " Try running gatk IndexFeatureFile on the input. See: https://gatk.broadinstitute.org/hc/en-us/articles/5358901172891-IndexFeatureFile" \
&& echo "Exiting..." && exit 1


[  ! -z "$DBSNPFILE" ] && [  ! -f "$DBSNPFILE" ] \
&& [ $help_flag -eq 0 ] && echo "ERROR: ${DBSNPFILE} does not exist or is not a file.  Exiting..." && exit 1

[  ! -z "$DBSNPFILE" ] && [  -f "$DBSNPFILE" ] && [ ! -f "${DBSNPFILE}.tbi" ] \
&& [ $help_flag -eq 0 ] && echo "ERROR:  An index file (.tbi) is required but was not found for file ${DBSNPFILE}" \
&& echo "Please compress and index all input vcf files: bgzip -c  ${DBSNPFILE} > ${DBSNPFILE}.gz && tabix -p vcf ${DBSNPFILE}.gz" \
&& echo "See: https://www.biostars.org/p/59492/" \
&& echo "Exiting..." && exit 1

# check workdir
[ $help_flag -eq 0 ] && [ -z "$RESOURCESDIR" ] && CMD="${CMD} -v ${WORKDIR}:/volumes/workdir" && PARAMS="${PARAMS} -w /volumes/workdir"

# check resources dir
[ $help_flag -eq 0 ] && [ -d "$RESOURCESDIR" ] \
&& CMD="${CMD} -v ${RESOURCESDIR}:/volumes/resources" && PARAMS="${PARAMS} -rd /volumes/resources"

# check data-source dir
[ $help_flag -eq 0 ] && [ -d "$DATASOURCEDIR" ] \
&& CMD="${CMD} -v ${DATASOURCEDIR}:/volumes/datasource" && PARAMS="${PARAMS} -ds /volumes/datasource"


# check tmp dir
[ $help_flag -eq 0 ] && [ -d "$TMPDIR" ] \
&& CMD="${CMD} -v ${TMPDIR}:/volumes/tmp" && PARAMS="${PARAMS} -t /volumes/tmp"

# check samples file
[ $help_flag -eq 0 ] && [ -f "$SAMPLESFILE" ] \
&& CMD="${CMD} --mount type=bind,source=${SAMPLESFILE},target=/volumes/inputs/$(basename $SAMPLESFILE)" \
&& PARAMS="${PARAMS} -s /volumes/inputs/$(basename $SAMPLESFILE)"

# check reference file
[ $help_flag -eq 0 ] && [ -f "$REFERENCE" ] \
&& CMD="${CMD} --mount type=bind,source=${REFERENCE},target=/volumes/resources/$(basename $REFERENCE)" \
&& CMD="${CMD} --mount type=bind,source=${REFERENCE}.fai,target=/volumes/resources/$(basename ${REFERENCE}.fai)" \
&& CMD="${CMD} --mount type=bind,source=${REFDIR}/${REFNAME}.dict,target=/volumes/resources/${REFNAME}.dict" \
&& PARAMS="${PARAMS} -r /volumes/resources/$(basename $REFERENCE)"

# check bed file
[ $help_flag -eq 0 ] && [ -f "$BEDFILE" ] \
&& CMD="${CMD} --mount type=bind,source=${BEDFILE},target=/volumes/resources/$(basename $BEDFILE)" \
&& PARAMS="${PARAMS} -b /volumes/resources/$(basename $BEDFILE)"

# check bed file
[ $help_flag -eq 0 ] && [ -f "$BEDFILE" ] && [ -f "${BEDFILE}.tbi" ] \
&& CMD="${CMD} --mount type=bind,source=${BEDFILE}.tbi,target=/volumes/resources/$(basename $BEDFILE.tbi)" \


# check germline resource
[ $help_flag -eq 0 ] && [ -f "$GERMLINEFILE" ] \
&& CMD="${CMD} --mount type=bind,source=${GERMLINEFILE},target=/volumes/resources/$(basename $GERMLINEFILE)" \
&& CMD="${CMD} --mount type=bind,source=${GERMLINEFILE}.idx,target=/volumes/resources/$(basename $GERMLINEFILE).idx" \
&& PARAMS="${PARAMS} -g /volumes/resources/$(basename $GERMLINEFILE)"

# check variant file
[ $help_flag -eq 0 ] && [ -f "$VARIANTFILE" ] \
&& CMD="${CMD} --mount type=bind,source=${VARIANTFILE},target=/volumes/resources/$(basename $VARIANTFILE)" \
&& CMD="${CMD} --mount type=bind,source=${VARIANTFILE}.idx,target=/volumes/resources/$(basename $VARIANTFILE).idx" \
&& PARAMS="${PARAMS} -v /volumes/resources/$(basename $VARIANTFILE)"

# check dbsnp file
[ $help_flag -eq 0 ] && [ -f "$DBSNPFILE" ] \
&& CMD="${CMD} --mount type=bind,source=${DBSNPFILE},target=/volumes/resources/$(basename $DBSNPFILE)" \
&& CMD="${CMD} --mount type=bind,source=${DBSNPFILE}.tbi,target=/volumes/resources/$(basename $DBSNPFILE).tbi" \
&& PARAMS="${PARAMS} -db /volumes/resources/$(basename $DBSNPFILE)"

if [ -f "$SAMPLESFILE" ]; then

  for line in `cat ${SAMPLESFILE}`
  do
    if [ -f $line ]; then
        filename=$(basename $line)
        extension="${filename##*.}"
        if [ $extension == 'bam' ]; then
          [ ! -f "${line}.bai" ] && echo "ERROR: Some input bam files are not indexed." && \
          echo "Please index all input bam files: samtools index ${line}" && \
          echo "See: http://www.htslib.org/doc/samtools-index.html" && \
          echo "Exiting..." && exit 1
          SOURCE="${line}.bai"
          TARGET="/volumes/inputs/${filename}.bai"
          if [[ "${CMD}" != *"${TARGET}"* ]]; then
            CMD="${CMD} --mount type=bind,source="${SOURCE}",target=${TARGET}"
          fi

        elif [ $extension == 'vcf' ]; then
          [ ! -f "${line}.gz" ] && echo "ERROR: Some input vcf files are not compressed" && \
          echo "Please compress and index all input vcf files: bgzip -c  ${line} > ${line}.gz && tabix -p vcf ${line}.gz" && \
          echo "See: https://www.biostars.org/p/59492/" && \
          echo "Exiting..." && exit 1
        fi

        if [[ $filename == *vcf.gz ]]; then
          [ ! -f "${line}.tbi" ] && echo "ERROR: Some input vcf files are not indexed." && \
          echo "Please index all input vcf files: tabix -p vcf ${line}.gz" && \
          echo "See: https://www.biostars.org/p/59492/" && \
          echo "Exiting..." && exit 1

          CMD="${CMD} --mount type=bind,source="${line}.tbi",target=/volumes/inputs/${filename}.tbi"
        fi

        MOUNT="--mount type=bind,source="${line}",target=/volumes/inputs/${filename}"
        if [[ "${CMD}" != *"${MOUNT}"* ]]; then
          CMD="${CMD} ${MOUNT}"
        fi
    else
      echo "ERROR: ${line} does not exist or is not a file.  Exiting..." && exit 1
    fi
  done
fi

CMD="${CMD} musta:Dockerfile musta ${PARAMS}"

#echo $CMD

eval $CMD
