#!/bin/bash

mkdir -p /volumes/workdir
mkdir -p /volumes/workdir/inputs
mkdir -p /volumes/workdir/results
mkdir -p /volumes/workdir/resources
mkdir -p /volumes/workdir/workflow
mkdir -p /volumes/logs
mkdir -p /volumes/tmp

chown -R appuser /volumes/workdir
chown -R appuser /volumes/logs
chown -R appuser /volumes/tmp
chmod +x /code/src/bin/musta