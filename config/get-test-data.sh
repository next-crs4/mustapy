#!/bin/bash


cd /musta || exit 1;

git clone https://github.com/solida-core/test-data-somatic.git

sed -i -e 's|test-data-somatic|/musta/test-data-somatic|g;' /musta/config/samples.tsv


