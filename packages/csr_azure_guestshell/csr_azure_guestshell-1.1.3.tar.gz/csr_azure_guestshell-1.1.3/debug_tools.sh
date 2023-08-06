#!/bin/sh

# Use this script to create a tar ball of debug information for the guestshell package

tool_status="/home/guestshell/azure/tools/tool_status.log"
tar_file="/home/guestshell/azure/tools/tools_debug.tar"

# Write the status of each of the daemon processes running under guestshell
systemctl status waagent.service > $tool_status
systemctl status auth-token.service >> $tool_status
/sbin/service atd status >> $tool_status

# Check on the MSI extension
systemctl status azuremsixtn >> $tool_status
# Is it installed?
sudo ls /var/log/azure >> $tool_status
ls /etc/systemd/system/azuremsixtn.service >> $tool_status

# List all running processes
ps -ef >> $tool_status

# Gather all the log files together in a tar ball
cd /home/guestshell/azure
tar -c /bootflash/cvac.log /var/log/messages /var/log/waagent.log ./tools/tool_status.log ./tools/install.log ./tools/MetadataMgr/metadata.json ./tools/TokenMgr/tokenMgr.log ./waagent/install.log > $tar_file

# Copy the file to /bootflash
cp ./tools/tools_debug.tar /bootflash

# Clean up
rm $tool_status

