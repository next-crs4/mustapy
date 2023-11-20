#!/bin/bash

source musta_lib.sh

init

parse_args "$@"

[ $help_flag -eq 1 ] && show_help

check_mandatory_argument "$WORKDIR" "-w | --workdir"
check_mandatory_argument "$SAMPLESFILE" "-s | --samples-file"

check_and_create_directory "$WORKDIR"
check_and_create_directory "$RESOURCESDIR"
check_and_create_directory "$TMPDIR"

[ -n "$DATASOURCEDIR" ] && check_directory "$DATASOURCEDIR"

[ -n "$SAMPLESFILE" ] && check_file "$SAMPLESFILE"
[ -n "$REFERENCE" ] && check_file "$REFERENCE"
[ -n "$BEDFILE" ] && check_file "$BEDFILE"
[ -n "$GERMLINEFILE" ] && check_file "$GERMLINEFILE"
[ -n "$VARIANTFILE" ] && check_file "$VARIANTFILE"
[ -n "$DBSNPFILE" ] && check_file "$DBSNPFILE"

[ -n "$REFERENCE" ] && check_reference_files "$REFERENCE"
[ -n "$BEDFILE" ] && check_bed_file "$BEDFILE"
[ -n "$GERMLINEFILE" ] && check_germline_file "$GERMLINEFILE"
[ -n "$VARIANTFILE" ] && check_variant_file "$VARIANTFILE"
[ -n "$DBSNPFILE" ] && check_dbsnp_file "$DBSNPFILE"

[ -n "$WORKDIR" ] && mount_directory "$WORKDIR" "/volumes/workdir" "-w"
[ -n "$DATASOURCEDIR" ] && mount_directory "$DATASOURCEDIR" "/volumes/datasource" "-ds"
[ -n "$RESOURCESDIR" ] && mount_directory "$RESOURCESDIR" "/volumes/resources" "-rd"
[ -n "$TMPDIR" ] && mount_directory "$TMPDIR" "/volumes/tmp" "-t"

[ -n "$SAMPLESFILE" ] && mount_docker_file "$SAMPLESFILE" "/volumes/inputs/$(basename $SAMPLESFILE)"
[ -n "$SAMPLESFILE" ] && generate_common_params "-s" "$SAMPLESFILE" "/volumes/inputs"

[ -n "$SAMPLESFILE" ] && process_samples_file "$SAMPLESFILE"

CMD="${CMD} musta:Dockerfile musta ${PARAMS}"

#echo $CMD

eval $CMD
