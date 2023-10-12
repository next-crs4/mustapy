# musta
A novel affordable and reliable framework for accurate detection and comprehensive analysis of somatic mutations in cancer

## Contents
- [Overview](#overview)
- [Requirements](#requirements)
- [Quick Start](#quick-start)
- [Tutorial](#tutorial)

## Overview
Accurate detection and comprehensive analysis of somatic variants are a major task in cancer sample data analysis, 
which is routinely carried out combining different software packages with specific software dependencies and with the 
need of laborious and  time-consuming data format conversions. 

To overcome these limitations, we developed Musta, an end-to-end pipeline to detect, classify 
and interpret mutations in cancer. 

Musta is based on a Python command-line tool that easily handles matched tumor-normal or tumor-only samples for 
accurate detection and comprehensive analysis of somatic mutations. 
This user-friendly approach allows researchers, without specific computer programming experience, 
to process cancer data by using a single command line.

The core is a Snakemake based workflow that contains all analysis steps commonly performed in cancer genomics, 
following GATK Best Practices Somatic Pipeline and exploiting mafTools R package. 
In details, Musta is thus able to perform in an integrated way the following tasks:

- **Variant Calling.** Calls somatic SNVs and indels. Users can choose between two modes:
(i) tumor-normal mode, where a tumor sample is matched with a normal sample in analysis and (ii) tumor-only mode, 
where a single sample's alignment data is analyzed.

- **Variant Annotation.** Functional annotation of called somatic variants based on a set of data sources, 
each with its own matching criteria. 

- **Driver Gene Detection.** Identification of cancer driver genes based on positional clustering. 
The output contains the list of genes ordered according to their p-values and a weighted scatter plot.

- **Pathway Analysis.** Check for enrichment of known oncogenic pathways. The output contains a fraction of the affected
pathway and samples and an oncoplot of the oncogenic pathway.

- **Estimation of Tumor Heterogeneity.** Inferring tumor clonality by clustering variant allele frequencies. 
The output contains clustering results and the related density plot.

- **Deconvolution of Mutational Signatures.** De-novo extraction of mutational signatures followed by a comparison 
with the reference COSMIC signatures by means of similarity score. 
The output contains deconvoluted signatures, cosine similarities, aetiologies, best match and a barplot of 
decomposed mutational signatures.

Musta, whose reliability was extensively tested on different cohorts from The Cancer Genome Atlas (TGCA), 
is currently used for cancer sample data analysis at the [CRS4-NGS Core](http://next.crs4.it), 
one of the largest sequencing facilities in Italy. 

Musta, both in tests and routine analysis, has proven to be a robust and flexible pipeline for accurate detection and 
comprehensive analysis of somatic variants in cancer.

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

4 - Run the demo 

4.1 DryRun

```shell
musta demo -w /path/to/workdir -d
```

4.2 Run
```shell
musta demo -w /path/to/workdir
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

### Variant Calling
Calls somatic SNVs and indels following the [GATK Best Practices for somatic variant calling](https://gatk.broadinstitute.org/hc/en-us/articles/360035894731-Somatic-short-variant-discovery-SNVs-Indels-)

![Variant Calling](docs/images/call-workflow.png)

This step requires BAM files for each input tumor and normal sample. 

#### samples.yml

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
patientB:
  normal_sample_name:
  tumor_sample_name:
    - B33
  normal_bam:
  tumor_bam:
    - path/to/test-data-somatic/data/bam/B33.chr22.bam
```

#### musta call -h

```shell
usage: musta call [-h] --workdir PATH --samples-file PATH --reference-file
                  PATH --bed-file PATH --variant-file PATH --germline-resource
                  PATH [--force] [--dryrun]

optional arguments:
  -h, --help            show this help message and exit
  --workdir PATH, -w PATH
                        working folder path
  --samples-file PATH, -s PATH
                        sample list file in YAML format
  --reference-file PATH, -r PATH
                        reference FASTA file
  --bed-file PATH, -b PATH
                        reference FASTA file
  --variant-file PATH, -v PATH
                        VCF file containing variants and allele frequencies
  --germline-resource PATH, -g PATH
                        Population vcf of germline sequencing containing
                        allele fractions.
  --force, -f           force all output files to be re-created
  --dryrun, -d          Workflow will be only described.
```

#### Run

```shell
musta call -w /path/to/workdir \
-s /path/to/samples.yml \
-r /path/to/test-data-somatic/resources/chr22.fa \
-v /path/to/test-data-somatic/resources/somatic-b37_small_exac_common_3.ucsc.chr22.vcf \
-g /path/to/test-data-somatic/resources/somatic-b37_af-only-gnomad.raw.sites.ucsc.chr22.vcf \
-b /path/to/test-data-somatic/resources/chr22_testbed.bed
```

#### check outputs in `/path/to/workdir/outputs`

results in `/path/to/workdir/outputs/results`

logs in`/path/to/workdir/outputs/logs`

report in `/path/to/workdir/outputs/report.html`

[back](#contents)

### Variant Annotations
Functional annotation of called somatic variants 

This step requires a VCF file for each patient. 

#### samples.yml

```yaml
patientA:
  normal_sample_name:
    - N1
  tumor_sample_name:
    - A25
  normal_bam:
  tumor_bam:
  vcf:
    - /path/to/test-data-somatic/data/vcf/patientA.chr22.vcf
patientB:
  normal_sample_name:
  tumor_sample_name:
    - B33
  normal_bam:
  tumor_bam:
  vcf:
    - /path/to/test-data-somatic/data/vcf/patientB.chr22.vcf
```

#### musta annotate -h

```shell
usage: musta annotate [-h] --workdir PATH --samples-file PATH --reference-file
                      PATH --data-source PATH [--ref-version {hg19,hg38}]
                      [--force] [--dry_run]

optional arguments:
  -h, --help            show this help message and exit
  --workdir PATH, -w PATH
                        working folder path
  --samples-file PATH, -s PATH
                        sample list file in YAML format
  --reference-file PATH, -r PATH
                        reference FASTA file
  --data-source PATH, -ds PATH
                        The path to a data source folder for Variant
                        Annotations
  --ref-version {hg19,hg38}, -rf {hg19,hg38}
                        The version of the Human Genome reference to use.
  --force, -f           overwrite directories and files if they exist in the
                        destination
  --dry_run, -d         Workflow will be only described.
```

#### Run

```shell
musta annotate -w /path/to/workdir \
-s /path/to/samples.yml \
-r /path/to/test-data-somatic/resources/chr22.fa \
-ds /path/to/data-source \
-rf gf19
```

#### Check outputs in `/path/to/workdir/outputs`

Results in `/path/to/workdir/outputs/results`

Logs in`/path/to/workdir/outputs/logs`

Report in `/path/to/workdir/outputs/report.html`

[Back](#contents)


### Driver Gene Detection
Identification of cancer driver genes based on positional clustering. 
The output contains the list of genes ordered according to their p-values and a weighted scatter plot.

This step requires a MAF file for each patient or cohort.

#### samples.yml

```yaml
patientBRCA:
  maf:
    - /path/to/test-data-somatic/data/maf/BRCA_subset_25_samples.maf
```

#### musta detect -h

```shell
usage: musta detect [-h] --workdir PATH --samples-file PATH [--force]
                    [--dryrun]

optional arguments:
  -h, --help            show this help message and exit
  --workdir PATH, -w PATH
                        working folder path
  --samples-file PATH, -s PATH
                        sample list file in YAML format
  --force, -f           overwrite directories and files if they exist in the
                        destination
  --dryrun, -d          Workflow will be only described.

```

#### Run
```shell
musta detect -w /path/to/workdir \
-s /path/to/samples.yml 
```

#### Check outputs in `/path/to/workdir/outputs`

Results in `/path/to/workdir/outputs/results`

Logs in`/path/to/workdir/outputs/logs`

Report in `/path/to/workdir/outputs/report.html`

[Back](#contents)

### Pathway Analysis
heck for enrichment of known oncogenic pathways. The output contains a fraction of the affected
pathway and samples and an oncoplot of the oncogenic pathway.


This step requires a MAF file for each patient or cohort.

#### samples.yml

```yaml
patientBRCA:
  maf:
    - /path/to/test-data-somatic/data/maf/BRCA_subset_25_samples.maf
```

#### musta pathway -h

```shell
usage: musta pathway [-h] --workdir PATH --samples-file PATH [--force]
                     [--dryrun]

optional arguments:
  -h, --help            show this help message and exit
  --workdir PATH, -w PATH
                        working folder path
  --samples-file PATH, -s PATH
                        sample list file in YAML format
  --force, -f           overwrite directories and files if they exist in the
                        destination
  --dryrun, -d          Workflow will be only described.

```

#### Run
```shell
musta pathway -w /path/to/workdir \
-s /path/to/samples.yml 
```

#### Check outputs in `/path/to/workdir/outputs`

Results in `/path/to/workdir/outputs/results`

Logs in`/path/to/workdir/outputs/logs`

Report in `/path/to/workdir/outputs/report.html`

[Back](#contents)

### Estimation of Tumor Heterogeneity
Inferring tumor clonality by clustering variant allele frequencies.
The output contains clustering results and the related density plot.

This step requires a MAF file for each patient or cohort.

#### samples.yml

```yaml
patientBRCA:
  maf:
    - /path/to/test-data-somatic/data/maf/BRCA_subset_25_samples.maf
```

#### musta heterogeneity -h

```shell
usage: musta heterogeneity [-h] --workdir PATH --samples-file PATH [--force]
                           [--dryrun]

optional arguments:
  -h, --help            show this help message and exit
  --workdir PATH, -w PATH
                        working folder path
  --samples-file PATH, -s PATH
                        sample list file in YAML format
  --force, -f           overwrite directories and files if they exist in the
                        destination
  --dryrun, -d          Workflow will be only described.

```

#### Run
```shell
musta heterogeneity -w /path/to/workdir \
-s /path/to/samples.yml 
```

#### Check outputs in `/path/to/workdir/outputs`

Results in `/path/to/workdir/outputs/results`

Logs in`/path/to/workdir/outputs/logs`

Report in `/path/to/workdir/outputs/report.html`

[Back](#contents)

### Deconvolution of Mutational Signatures
De-novo extraction of mutational signatures followed by a comparison
with the reference COSMIC signatures by means of similarity score.
The output contains deconvoluted signatures, cosine similarities, 
aetiologies, best match and a barplot of decomposed mutational signatures.


This step requires a MAF file for each patient or cohort.

#### samples.yml

```yaml
patientBRCA:
  maf:
    - /path/to/test-data-somatic/data/maf/BRCA_subset_25_samples.maf
```

#### musta signature -h

```shell
usage: musta signature [-h] --workdir PATH --samples-file PATH [--force]
                           [--dryrun]

optional arguments:
  -h, --help            show this help message and exit
  --workdir PATH, -w PATH
                        working folder path
  --samples-file PATH, -s PATH
                        sample list file in YAML format
  --force, -f           overwrite directories and files if they exist in the
                        destination
  --dryrun, -d          Workflow will be only described.
```

#### Run
```shell
musta signature -w /path/to/workdir \
-s /path/to/samples.yml 
```

#### Check outputs in `/path/to/workdir/outputs`

Results in `/path/to/workdir/outputs/results`

Logs in`/path/to/workdir/outputs/logs`

Report in `/path/to/workdir/outputs/report.html`

[Back](#contents)

