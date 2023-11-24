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
        [ $help_flag -eq 0 ] && echo "ERROR: $arg_name is a mandatory argument" && exit 1
    fi
}

check_and_create_directory() {
    local dir_path=$1

    if [ -n "$dir_path" ]; then
      [ ! -d "$dir_path" ] && echo "WARNING: $dir_path does not exist or is not a directory. Trying to create it." && mkdir -p "$dir_path"
    fi
}

check_directory() {
    local dir_name=$1
    echo "#${dir_name}#"

    [ -n "$dir_name" ] && [ ! -d "$dir_name" ] && echo "ERROR: $dir_name does not exist or is not a directory. Exiting..." && exit 1
}

check_file() {
    local file_path=$1

    [ -n "$file_path" ] && [ ! -f "$file_path" ] && echo "ERROR: $file_path does not exist or is not a file. Exiting..." &&  exit 1

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
            echo "ERROR: Fasta index file (.fai) for reference ${reference_file} does not exist."
            echo "Please see https://github.com/broadinstitute/gatk-docs/blob/master/gatk3-faqs/How_can_I_prepare_a_FASTA_file_to_use_as_reference%3F.md for help creating it."
            echo "Exiting..."
            exit 1
        fi

        # Check for .dict file
        if [ ! -f "${refdir}/${refname}.dict" ]; then
            echo "ERROR: Fasta dict file (.dict) for reference ${reference_file} does not exist."
            echo "Please see https://github.com/broadinstitute/gatk-docs/blob/master/gatk3-faqs/How_can_I_prepare_a_FASTA_file_to_use_as_reference%3F.md for help creating it."
            echo "Exiting..."
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
            echo "ERROR: BED file is not compressed."
            echo "Please compress and index your bed file: bgzip -c  ${bed_file} > ${bed_file}.gz && tabix -p bed ${bed_file}.gz"
            echo "See: https://www.biostars.org/p/59492/"
            echo "Exiting..."
            exit 1
        fi

        # Check for .tbi file
        if [ ! -f "${bed_file}.tbi" ]; then
            echo "ERROR: An index file (.tbi) is required but was not found for file ${bed_file}."
            echo "Please compress and index your bed file: tabix -p bed ${bed_file}"
            echo "See: https://www.biostars.org/p/59492/"
            echo "Exiting..."
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
            echo "ERROR: An index file (.idx) is required but was not found for file ${germline_file}"
            echo "Try running gatk IndexFeatureFile on the input. See: https://gatk.broadinstitute.org/hc/en-us/articles/5358901172891-IndexFeatureFile"
            echo "Exiting..."
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
            echo "ERROR: An index file (.idx) is required but was not found for file ${variant_file}"
            echo "Try running gatk IndexFeatureFile on the input. See: https://gatk.broadinstitute.org/hc/en-us/articles/5358901172891-IndexFeatureFile"
            echo "Exiting..."
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
            echo "ERROR: An index file (.tbi) is required but was not found for file ${dbsnp_file}"
            echo "Please compress and index all input vcf files: bgzip -c ${dbsnp_file} > ${dbsnp_file}.gz && tabix -p vcf ${dbsnp_file}.gz"
            echo "See: https://www.biostars.org/p/59492/"
            echo "Exiting..."
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
        echo "ERROR: ${host_dir} does not exist or is not a directory. Exiting..."
        exit 1
    fi
}

process_samples_file() {
  local samples_file="$1"

  if [ -f "$samples_file" ]; then
    keys=$(grep -E '^[a-zA-Z0-9_]+:' "$samples_file" | sed 's/:$//')

    get_value() {
      local key="$1"
      local type="$2"
      grep -A 1000 "^${key}:" "$samples_file" | awk -v type="$type" '/^[[:space:]]+[-]?[[:space:]]+'"$type"':/ {getline; print}' | sed -E 's/^[[:space:]]+-[[:space:]]+//'
    }

    get_filename_and_extension() {
      local file_path="$1"

      if [ -f "$file_path" ]; then
        local filename=$(basename "$file_path")
        local extension="${filename##*.}"
        echo "$filename $extension"
      else
        echo "ERROR: $file_path does not exist or is not a file. Exiting..." && exit 1
      fi
    }

   mount_bam_file() {
    local file_path="$1"
    local target_dir="$2"

    ret=$(get_filename_and_extension "$file_path")
    filename=$(echo "$ret" | cut -d' ' -f1)
    extension=$(echo "$ret" | cut -d' ' -f2)

    if [ "$extension" == 'bam' ]; then
      [ ! -f "${file_path}.bai" ] && echo "ERROR: Some input bam files are not indexed." && \
      echo "Please index all input bam files: samtools index ${file_path}" && \
      echo "See: http://www.htslib.org/doc/samtools-index.html" && \
      echo "Exiting..." && exit 1

     mount_docker_file "$file_path" "${target_dir}/${filename}"
     mount_docker_file "${file_path}.bai" "${target_dir}/${filename}.bai"

    else
      echo "ERROR: ${file_path} does not appear to be a valid bam file. Please check it out" && exit 1
    fi
  }

  mount_vcf_file() {
    local file_path="$1"
    local target_dir="$2"

    ret=$(get_filename_and_extension "$file_path")
    filename=$(echo "$ret" | cut -d' ' -f1)
    extension=$(echo "$ret" | cut -d' ' -f2)

    if [ $extension == 'vcf' ]; then
      echo "ERROR: ${file_path} is not compressed" && \
      echo "Please compress and index all input vcf files: bgzip -c  ${file_path} > ${file_path}.gz && tabix -p vcf ${file_path}.gz" && \
      echo "See: https://www.biostars.org/p/59492/" && \
      echo "Exiting..." && exit 1
    fi

    if [[ $filename == *vcf.gz ]]; then
      [ ! -f "${file_path}.tbi" ] && echo "ERROR: Some input vcf files are not indexed." && \
      echo "Please index all input vcf files: tabix -p vcf ${file_path}.gz" && \
      echo "See: https://www.biostars.org/p/59492/" && \
      echo "Exiting..." && exit 1

      mount_docker_file "$file_path" "${target_dir}/${filename}"
      mount_docker_file "${file_path}.tbi" "${target_dir}/${filename}.tbi"
    else
      echo "ERROR: ${file_path} does not appear to be a valid vcg.gz file. Please check it out" && exit 1
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
      echo "ERROR: ${file_path} does not appear to be a valid maf file. Please check it out" && exit 1
    fi
  }


    for key in $keys; do
      if grep -q "^${key}:" "$samples_file"; then
        normal_bam=$(get_value "$key" "normal_bam" | head -n 1)
        tumor_bam=$(get_value "$key" "tumor_bam" | head -n 1)
        vcf=$(get_value "$key" "vcf" | head -n 1)
        maf=$(get_value "$key" "maf" | head -n 1)

        [ -n "$normal_bam" ] && mount_bam_file "$normal_bam" "/volumes/inputs"
        [ -n "$tumor_bam" ] && mount_bam_file "$tumor_bam" "/volumes/inputs"

        [ -n "$vcf" ] && mount_vcf_file "$vcf" "/volumes/inputs"

        [ -n "$maf" ] && mount_maf_file "$maf" "/volumes/inputs"
      fi
    done
  fi
}

show_help() {
  local cmd="docker run musta:Dockerfile musta --help"

  eval $cmd
  exit 0
}