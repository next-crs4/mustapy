#!/bin/bash

mkdir -p /volumes/workdir
mkdir -p /volumes/inputs
mkdir -p /volumes/outputs
mkdir -p /volumes/resources
mkdir -p /volumes/logs

chown -R appuser /volumes/logs
chown -R appuser /volumes/logs
chmod +x /code/src/bin/musta