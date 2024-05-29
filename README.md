# musta
A novel affordable and reliable framework for accurate detection and comprehensive analysis of somatic mutations in cancer

## Contents
- [Overview](#overview)
- [Requirements](#requirements)
- [Quick Start](#quick-start)

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
To install and run **Musta**, it is essential to have Docker installed on your computer.
Docker is a containerization platform that ensures consistency and compatibility in running **Musta**
across different computing environments.

If you do not have Docker installed,
you can download and install it by following the instructions provided in the official Docker documentation:
[Docker Installation Guide](https://docs.docker.com/engine/install).

Please ensure that Docker is properly configured and running on your system before proceeding with the installation of **Musta**.

[Back](#contents)

## Quick Start
The installation process may take several minutes.

1. Clone the repository:

    ```shell
    git clone https://github.com/next-crs4/musta.git
    ```

2. Change into the Musta directory:

    ```shell
    cd musta
    ```

3. Initialize the Musta framework:

    ```shell
    make bootstrap
    ```

4. Confirm the Musta Docker image has been built:

    ```shell
    docker images
    ```

    You should see an output similar to:

    ```text
    REPOSITORY   TAG          IMAGE ID         CREATED       SIZE
    musta        Dockerfile   bb170cfc6546     2 hours ago   2.48GB
    ```

    This indicates the Musta Docker image is successfully built.

5. Verify the Musta Command Line Interface (CLI) installation:

    ```shell
    musta --help
    ```

    You should see an output like this:

    ```text
    usage: musta [-h] [--config_file PATH] [--logfile PATH]
                 [--loglevel {DEBUG,INFO,WARNING,ERROR,CRITICAL}]
                 {detect,classify,interpret} ...

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

      {detect,classify,interpret}
                            sub-command description
        detect              Somatic Mutations Detection.
                                1.  Multiple Variant Calling: mutect, lofreq, varscan, 
                                    vardict, muse, strelka.
                                2.  Ensemble consensus approach to combine results and 
                                    to improve the performance of variant calling
        classify            Variant Annotation
                            Functional annotation of called somatic variants 
                            
        interpret           Somatic Mutations Interpretation:
                                1.  Identification of cancer driver genes 
                                2.  Check for enrichment of known oncogenic pathways.
                                3.  Infer tumor clonality by clustering variant allele frequencies.
                                4.  Deconvolution of Mutational Signatures
    ```

    This indicates the Musta CLI is correctly installed and ready for use. You can now proceed with using Musta for somatic mutation analysis in cancer research by following the instructions provided in the [User Guide](https://next-crs4.github.io/mustapy/). 

[Back](#contents)

