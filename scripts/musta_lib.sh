#!/bin/bash

init() {
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
}

log() {
    local timestamp
    timestamp=$(date +"%Y-%m-%d %T")
    local message="[$timestamp] $1"
    __log_msg__="${__log_msg__}${message}"$'\n'
    echo "$message"
}

parse_args() {
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
                ;;
        esac
    done
}

check_mandatory_argument() {
    local arg_value=$1
    local arg_name=$2

    if [ -z "$arg_value" ]; then
        [ $help_flag -eq 0 ] && log "ERROR: $arg_name is a mandatory argument" && exit 1
    fi
}

check_and_create_directory() {
    local dir_path=$1

    if [ -n "$dir_path" ]; then
      [ ! -d "$dir_path" ] && log "WARNING: $dir_path does not exist or is not a directory. Trying to create it." && mkdir -p "$dir_path"
    fi
}

check_directory() {
    local dir_name=$1

    [ -n "$dir_name" ] && [ ! -d "$dir_name" ] && log "ERROR: $dir_name does not exist or is not a directory. Exiting..." && exit 1
}

check_file() {
    local file_path=$1

    [ -n "$file_path" ] && [ ! -f "$file_path" ] && log "ERROR: $file_path does not exist or is not a file. Exiting..." &&  exit 1

}

mount_docker_file() {
  local source_file=$1
  local target_file=$2

  if [[ "${CMD}" != *" --mount type=bind,source=${source_file},target=${target_file} "* ]]; then
    CMD="${CMD} --mount type=bind,source=${source_file},target=${target_file}"
  fi
}

generate_common_params() {
    local option=$1
    local source_file=$2
    local volume_path=$3

    PARAMS="${PARAMS} ${option} ${volume_path}/$(basename ${source_file})"
}

check_reference_files() {
    local reference_file=$1
    local refdir=$(dirname "$reference_file")
    local refname=$(basename "$reference_file" | sed 's/\(.*\)\..*/\1/')
    local reference_basename=$(basename "$reference_file")

    if [ -n "$reference_file" ] && [ -f "$reference_file" ]; then
        # Check for .fai file
        if [ ! -f "${reference_file}.fai" ]; then
            log "ERROR: Fasta index file (.fai) for reference ${reference_file} does not exist."
            log "Please see https://github.com/broadinstitute/gatk-docs/blob/master/gatk3-faqs/How_can_I_prepare_a_FASTA_file_to_use_as_reference%3F.md for help creating it."
            log "Exiting..."
            exit 1
        fi

        # Check for .dict file
        if [ ! -f "${refdir}/${refname}.dict" ]; then
            log "ERROR: Fasta dict file (.dict) for reference ${reference_file} does not exist."
            log "Please see https://github.com/broadinstitute/gatk-docs/blob/master/gatk3-faqs/How_can_I_prepare_a_FASTA_file_to_use_as_reference%3F.md for help creating it."
            log "Exiting..."
            exit 1
        fi

        mount_docker_file "$reference_file" "/volumes/resources/${reference_basename}"
        mount_docker_file "${reference_file}.fai" "/volumes/resources/${reference_basename}.fai"
        mount_docker_file "${refdir}/${refname}.dict" "/volumes/resources/${refname}.dict"
        generate_common_params "-r" "$reference_file" "/volumes/resources"

    fi
}

check_bed_file() {
    local bed_file=$1
    local bed_filename=$(basename "$bed_file")
    local extension="${filename##*.}"

    if [ -n "$bed_file" ] && [ -f "$bed_file" ]; then
        # Check if the file is compressed
        if [ "$extension" == "vcf" ]; then
            log "ERROR: BED file is not compressed."
            log "Please compress and index your bed file: bgzip -c  ${bed_file} > ${bed_file}.gz && tabix -p bed ${bed_file}.gz"
            log "See: https://www.biostars.org/p/59492/"
            log "Exiting..."
            exit 1
        fi

        # Check for .tbi file
        if [ ! -f "${bed_file}.tbi" ]; then
            log "ERROR: An index file (.tbi) is required but was not found for file ${bed_file}."
            log "Please compress and index your bed file: tabix -p bed ${bed_file}"
            log "See: https://www.biostars.org/p/59492/"
            log "Exiting..."
            exit 1
        fi

        mount_docker_file "$bed_file" "/volumes/resources/${bed_filename}"
        mount_docker_file "${bed_file}.tbi" "/volumes/resources/${bed_filename}.tbi"
        generate_common_params "-b" "$bed_file" "/volumes/resources"

    fi
}

check_germline_file() {
    local germline_file=$1
    local germline_filename=$(basename $germline_file)

    if [ -n "$germline_file" ] && [ -f "$germline_file" ]; then
        # Check for .idx file
        if [ ! -f "${germline_file}.idx" ]; then
            log "ERROR: An index file (.idx) is required but was not found for file ${germline_file}"
            log "Try running gatk IndexFeatureFile on the input. See: https://gatk.broadinstitute.org/hc/en-us/articles/5358901172891-IndexFeatureFile"
            log "Exiting..."
            exit 1
        fi

        mount_docker_file "$germline_file" "/volumes/resources/${germline_filename}"
        mount_docker_file "${germline_file}.idx" "/volumes/resources/${germline_filename}.idx"
        generate_common_params "-g" "$germline_file" "/volumes/resources"
    fi
}

check_variant_file() {
    local variant_file=$1
    local variant_filename=$(basename $variant_file)

    if [ -n "$variant_file" ] && [ -f "$variant_file" ]; then
        # Check for .idx file
        if [ ! -f "${variant_file}.idx" ]; then
            log "ERROR: An index file (.idx) is required but was not found for file ${variant_file}"
            log "Try running gatk IndexFeatureFile on the input. See: https://gatk.broadinstitute.org/hc/en-us/articles/5358901172891-IndexFeatureFile"
            log "Exiting..."
            exit 1
        fi

        mount_docker_file "$variant_file" "/volumes/resources/${variant_filename}"
        mount_docker_file "${variant_file}.idx" "/volumes/resources/${variant_filename}.idx"
        generate_common_params "-v" "$variant_file" "/volumes/resources"
    fi
}

check_dbsnp_file() {
    local dbsnp_file=$1
    local dbsnp_filename=$(basename $dbsnp_file)

    if [ -n "$dbsnp_file" ] && [ -f "$dbsnp_file" ]; then
        # Check for .tbi file
        if [ ! -f "${dbsnp_file}.tbi" ]; then
            log "ERROR: An index file (.tbi) is required but was not found for file ${dbsnp_file}"
            log "Please compress and index all input vcf files: bgzip -c ${dbsnp_file} > ${dbsnp_file}.gz && tabix -p vcf ${dbsnp_file}.gz"
            log "See: https://www.biostars.org/p/59492/"
            log "Exiting..."
            exit 1
        fi

        mount_docker_file "$dbsnp_file" "/volumes/resources/${dbsnp_filename}"
        mount_docker_file "${dbsnp_file}.tbi" "/volumes/resources/${dbsnp_filename}.tbi"
        generate_common_params "-db" "$dbsnp_file" "/volumes/resources"
    fi
}

mount_directory() {
    local host_dir=$1
    local docker_dir=$2
    local volume_flag=$3

    if [ -n "$host_dir" ] && [ -d "$host_dir" ];  then
        CMD="${CMD} -v ${host_dir}:${docker_dir}"
        PARAMS="${PARAMS} ${volume_flag} ${docker_dir}"
    else
        log "ERROR: ${host_dir} does not exist or is not a directory. Exiting..."
        exit 1
    fi
}

process_samples_file() {
  local samples_file="$1"

  if [ -f "$samples_file" ]; then
    keys=$(grep -E '^[a-zA-Z0-9_]+:' "$samples_file" | sed 's/:$//')
  else
    check_file "$samples_file"
  fi

  if echo "${PARAMS}" | grep -wq "detect"; then
    check_detect=true
  else
    check_detect=false
  fi

  
  if echo "${PARAMS}" | grep -wq "classify"; then
    check_classify=true
  else
    check_classify=false
  fi

  if echo "${PARAMS}" | grep -wq "interpret"; then
    check_interpret=true
  else
    check_interpret=false
  fi

  get_value() {
    local key="$1"
    local type="$2"
    grep -A 1000 "^${key}:" "$samples_file" | awk -v type="$type" '/^[[:space:]]+[-]?[[:space:]]+'"$type"':/ {getline; print}' | sed -E 's/^[[:space:]]+-[[:space:]]+//'
  }

  get_filename_and_extension() {
    local file_path="$1"
    file_path=$(echo $file_path | awk '{$1=$1};1')

    if [ -f "$file_path" ]; then
      local filename=$(basename "$file_path")
      local extension="${filename##*.}"
      filename=$(echo "$filename" | sed -e 's/^[[:space:]]*//' -e 's/[[:space:]]*$//')
      extension=$(echo "$extension" | sed -e 's/^[[:space:]]*//' -e 's/[[:space:]]*$//')
      echo "$filename $extension"
    else
      log "ERROR: $file_path does not exist or is not a file. Exiting..." && exit 1
    fi
  }

  mount_bam_file() {
    local file_path="$1"
    local target_dir="$2"

    ret=$(get_filename_and_extension "$file_path")
    filename=$(echo "$ret" | cut -d' ' -f1)
    extension=$(echo "$ret" | cut -d' ' -f2)

    if [ "$extension" == 'bam' ]; then
      [ ! -f "${file_path}.bai" ] && log "ERROR: Some input bam files are not indexed." && \
      log "Please index all input bam files: samtools index ${file_path}" && \
      log "See: http://www.htslib.org/doc/samtools-index.html" && \
      log "Exiting..." && exit 1

     mount_docker_file "$file_path" "${target_dir}/${filename}"
     mount_docker_file "${file_path}.bai" "${target_dir}/${filename}.bai"

    else
      log "ERROR: ${file_path} does not appear to be a valid bam file. Please check it out" && exit 1
    fi
  }

  mount_vcf_file() {
    local file_path="$1"
    local target_dir="$2"

    ret=$(get_filename_and_extension "$file_path")
    filename=$(echo "$ret" | cut -d' ' -f1)
    extension=$(echo "$ret" | cut -d' ' -f2)

    if [ $extension == 'vcf' ]; then
      log "ERROR: ${file_path} is not compressed" && \
      log "Please compress and index all input vcf files: bgzip -c  ${file_path} > ${file_path}.gz && tabix -p vcf ${file_path}.gz" && \
      log "See: https://www.biostars.org/p/59492/" && \
      log "Exiting..." && exit 1
    fi

    if [[ $filename == *".vcf.gz" ]]; then
      [ ! -f "${file_path}.tbi" ] && log "ERROR: Some input vcf files are not indexed." && \
      log "Please index all input vcf files: tabix -p vcf ${file_path}.gz" && \
      log "See: https://www.biostars.org/p/59492/" && \
      log "Exiting..." && exit 1

      mount_docker_file "$file_path" "${target_dir}/${filename}"
      mount_docker_file "${file_path}.tbi" "${target_dir}/${filename}.tbi"
    else
      log "ERROR: ${file_path} does not appear to be a valid vcf.gz file. Please check it out" && exit 1
    fi
  }

  mount_maf_file(){
    local file_path="$1"
    local target_dir="$2"

    ret=$(get_filename_and_extension "$file_path")
    filename=$(echo "$ret" | cut -d' ' -f1)
    extension=$(echo "$ret" | cut -d' ' -f2)

    if [ $extension == 'maf' ]; then
      mount_docker_file "$file_path" "${target_dir}/${filename}"
    else
      log "ERROR: ${file_path} does not appear to be a valid maf file. Please check it out" && exit 1
    fi
  }


  for key in $keys; do
    if grep -q "^${key}:" "$samples_file"; then
      [ "$check_detect" = true ] && normal_bam=$(get_value "$key" "normal_bam" | head -n 1)
      [ "$check_detect" = true ] && tumor_bam=$(get_value "$key" "tumor_bam" | head -n 1)
      [ "$check_classify" = true ] && vcf=$(get_value "$key" "vcf" | head -n 1)
      [ "$check_interpret" = true ] && maf=$(get_value "$key" "maf" | head -n 1)

      [ "$check_detect" = true ] && [ -n "$normal_bam" ] && mount_bam_file "$normal_bam" "/volumes/inputs"
      [ "$check_detect" = true ] && [ -n "$tumor_bam" ] && mount_bam_file "$tumor_bam" "/volumes/inputs"

      [ "$check_classify" = true ] && [ -n "$vcf" ] && mount_vcf_file "$vcf" "/volumes/inputs"

      [ "$check_interpret" = true ] && [ -n "$maf" ] && mount_maf_file "$maf" "/volumes/inputs"
    fi
  done
}

show_help() {
  local options=('detect' 'classify' 'interpret')
  local cmd="docker run musta:Dockerfile musta"
  for opt in "${options[@]}"; do
    if [[ $PARAMS == *"$opt"* ]]; then
       cmd="${cmd} ${opt}"
    fi
  done
  cmd="${cmd} --help"
  eval $cmd
  exit 0
}
