#!/bin/sh

# Install tools and programs to run the CSR in the Azure cloud
#
# This script assumes the guestshell has been configured and enabled on
# the CSR.

# Set up a directory tree for HA
if [ ! -d /home/guestshell/azure/HA ]; then
    sudo mkdir /home/guestshell/azure/HA
    sudo chown guestshell /home/guestshell/azure/HA
fi

if [ ! -d /home/guestshell/azure/HA/events ]; then
    sudo mkdir /home/guestshell/azure/HA/events
    sudo chown guestshell /home/guestshell/azure/HA/events
fi

install_log="/home/guestshell/azure/HA/install.log"

echo "Installing the Azure high availability package" >> $install_log

# Copy files from the package to guestshell

cp ha_tools.sh /home/guestshell/azure/HA
cp debug_ha.sh /home/guestshell/azure/HA
cp azure-ha.service /home/guestshell/azure/HA
touch /home/guestshell/azure/HA/azha.log

#cd client_api
#sudo mkdir /home/guestshell/azure/HA/client_api
#sudo chown guestshell /home/guestshell/azure/HA/client_api
cp client_api/revert_nodes.sh /home/guestshell/azure/HA

#cd ../server
#sudo mkdir /home/guestshell/azure/HA/server
#sudo chown guestshell /home/guestshell/azure/HA/server
#cp * /home/guestshell/azure/HA/server

# Set up the path to python scripts
export HA_PY_PATH=/home/guestshell/.local/lib/python2.7/site-packages/csr_azure_ha/client_api:/home/guestshell/.local/lib/python2.7/site-packages/csr_azure_ha/server

echo 'export PYTHONPATH=$PYTHONPATH:/home/guestshell/.local/lib/python2.7/site-packages/csr_azure_ha/client_api:/home/guestshell/.local/lib/python2.7/site-packages/csr_azure_ha/server' >> /home/guestshell/.bashrc
echo 'export PATH=$PATH:/home/guestshell/.local/lib/python2.7/site-packages/csr_azure_ha/client_api' >> /home/guestshell/.bashrc
source /home/guestshell/.bashrc

echo "Show the current PATH" >> $install_log
echo $PATH >> $install_log
echo "Show the current PYTHONPATH" >> $install_log
echo $PYTHONPATH >> $install_log
echo "Show the python sites" >> $install_log
python -m site >> $install_log

# Move the unit file for the azure-ha service
sudo mv /home/guestshell/azure/HA/azure-ha.service /etc/systemd/user

# Start the high availability server
echo "Starting the high availability service" >> $install_log
sudo systemctl enable /etc/systemd/user/azure-ha.service
sudo systemctl start azure-ha.service
sudo systemctl status azure-ha >> $install_log

# Add a cron job to periodically revert nodes for primary routers
croncmd="bash /home/guestshell/.local/lib/python2.7/site-packages/csr_azure_ha/client_api/revert_nodes.sh"
cronjob="*/5 * * * * $croncmd"
( crontab -l | grep -v -F "$croncmd" ; echo "$cronjob" ) | crontab -
echo "Added cron job for HA node reversion" >> $install_log
