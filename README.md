# musta
A novel affordable and reliable framework for accurate detection and comprehensive analysis of somatic mutations in cancer

## Contents
- [Overview](#overview)
- [Requirements](#requirements)
- [Quick Start](#quick-start)
- [Tutorial](#tutorial)

## Overview
Accurate detection and comprehensive analysis of somatic variants are a major task in cancer sample data analysis,
which is routinely carried out combining different software packages with specific software dependencies
and with the need of laborious and  time-consuming data format conversions.

To overcome these limitations, we developed **Musta**, an *end-to-end pipeline to detect, classify
and interpret mutations in cancer*.

**Musta** is a Python command-line tool that easily handles matched tumour-normal or tumour-only samples, from variant
calling to the deconvolution of mutational signatures, through variant annotation,
driver genes detection, pathway analysis, tumor heterogeneity.

**Musta**'s core is *Snakemake-based* and  was conceived for an easy installation through the Docker platform.
A simple Makefile bootstraps **Musta**,
taking care of the installation,
configuration and running steps and allowing the execution of the entire pipeline
or any individual step depending on the starting data.

**Musta**  is currently used for cancer sample data analysis at the [CRS4-NGS Core](https://www.crs4.it/next/)


[Back](#contents)

## Requirements
To install and run Musta, Docker must be presents in your computer.
To install Docker, see [https://docs.docker.com/engine/install](https://docs.docker.com/engine/install) 

[Back](#contents)

## Quick Start
The installation could require several minutes

1 - Clone the repository:

```shell
git clone https://github.com/next-crs4/musta.git
````

2 - Cd into the Musta directory:
```shell
cd musta
```

3 - Bring up the Musta framework

```shell
make bootstrap
```

[Back](#contents)


## Tutorial
In order to test **Musta**, users can download demo dataset from [https://github.com/solida-core/test-data-somatic](https://github.com/solida-core/test-data-somatic)

```yaml
patientA:
  normal_sample_name:
    - N1
  tumor_sample_name:
    - A25
  normal_bam:
    - path/to/test-data-somatic/data/bam/N1.chr22.bam
  tumor_bam:
    - path/to/test-data-somatic/data/bam/A25.chr22.bam
  vcf:
    - path/to/test-data-somatic/data/bam/A25.chr22.vcf
  maf:
    - path/to/test-data-somatic/data/bam/A25.chr22.maf
patientB:
  normal_sample_name:
  tumor_sample_name:
    - B33
  normal_bam:
  tumor_bam:
    - path/to/test-data-somatic/data/bam/B33.chr22.bam
  vcf:
    - path/to/test-data-somatic/data/bam/B33.chr22.vcf
  maf:
    - path/to/test-data-somatic/data/bam/B33.chr22.maf 
```
### Show help

```shell
musta -h
```

```shell
usage: musta [-h] [--config_file PATH] [--logfile PATH]
             [--loglevel {DEBUG,INFO,WARNING,ERROR,CRITICAL}]
             {detect,classify,interpret,end2end} ...

End-to-end pipeline to detect, classify and interpret mutations in cancer

optional arguments:
  -h, --help            show this help message and exit
  --config_file PATH, -c PATH
                        configuration file
  --logfile PATH        log file (default=stderr)
  --loglevel {DEBUG,INFO,WARNING,ERROR,CRITICAL}
                        logger level.

subcommands:
  valid subcommands

  {detect,classify,interpret,end2end}
                        sub-command description
    detect              Somatic Mutations Detection.
                            1.  Multiple Variant Calling: mutect, lofreq, varscan, vardict, muse, strelka.
                            2.  Ensemble consensus approach to combine results and to improve the performance of variant calling
                        
    classify            Variant Annotation
                        Functional annotation of called somatic variants 
                        
    interpret           Somatic Mutations Interpretation:
                            1.  Identification of cancer driver genes 
                            2.  Check for enrichment of known oncogenic pathways.
                            3.  Infer tumor clonality by clustering variant allele frequencies.
                            4.  Deconvolution of Mutational Signatures
                            
    end2end             Run the whole workflow, 
                        from Variant Calling to Deconvolution of Mutational Signatures
```

[Back](#contents)

