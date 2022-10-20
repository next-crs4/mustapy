#!/bin/bash

mkdir -p /volumes/workdir
mkdir -p /volumes/inputs
mkdir -p /volumes/workdir/outputs
mkdir -p /volumes/resources
mkdir -p /volumes/datasource
#mkdir -p /volumes/workdir/workflow
mkdir -p /volumes/logs
mkdir -p /volumes/tmp

chown -R appuser /volumes/workdir
chown -R appuser /volumes/resources
chown -R appuser /volumes/datasource
chown -R appuser /volumes/inputs
chown -R appuser /volumes/logs
chown -R appuser /volumes/tmp
chmod +x /code/src/bin/musta
