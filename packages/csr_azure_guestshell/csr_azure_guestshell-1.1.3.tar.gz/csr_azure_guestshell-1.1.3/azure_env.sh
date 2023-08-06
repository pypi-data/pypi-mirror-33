#!/bin/sh

# Set up an environment and directories for Azure tools
#
# This script assumes the guestshell has been configured and enabled on
# the CSR.

# Set up the environment for supporting Azure tools in the guestshell

# Set up a directory tree for Azure stuff
if [ ! -d /home/guestshell/azure ]; then
    sudo mkdir /home/guestshell/azure
    sudo chown guestshell /home/guestshell/azure
fi

if [ ! -d /home/guestshell/azure/tools ]; then
    sudo mkdir /home/guestshell/azure/tools
    sudo chown guestshell /home/guestshell/azure/tools
fi

if [ ! -d /home/guestshell/azure/waagent ]; then
    sudo mkdir /home/guestshell/azure/waagent
    sudo chown guestshell /home/guestshell/azure/waagent
fi
