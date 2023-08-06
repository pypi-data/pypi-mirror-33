#!/bin/sh

# Use this script to create a tar ball of debug information for the csr_azure_ha package

ha_status="/home/guestshell/azure/HA/ha_status.log"
tar_file="/home/guestshell/azure/HA/ha_debug.tar"

# Write the status of each of the daemon processes running under guestshell
systemctl status azure-ha.service > $ha_status
crontab -l >> $ha_status

# Gather all the log files together in a tar ball
cd /home/guestshell/azure/HA
tar -c ha_status.log install.log azha.log node_file ./events/* > $tar_file

# Compress the file
#gunzip -r $tar_file

# Copy the file to /bootflash
cp ha_debug.tar /bootflash

# Clean up
rm $ha_status