#!/bin/sh

# Install tools and programs to run the CSR in the Azure cloud
#
# This script assumes the guestshell has been configured and enabled on
# the CSR.

install_log="/home/guestshell/azure/tools/install.log"

echo "Start copying Azure tools files" > $install_log

# Copy files from the package to guestshell
cp install_tools.sh /home/guestshell/azure/tools
sudo chown guestshell /home/guestshell/azure/tools/install_tools.sh
cp debug_tools.sh /home/guestshell/azure/tools
sudo chown guestshell /home/guestshell/azure/tools/debug_tools.sh

cd examples
sudo mkdir /home/guestshell/azure/tools/examples
sudo chown guestshell /home/guestshell/azure/tools/examples
cp * /home/guestshell/azure/tools/examples

cd ../csr_azure_guestshell
cp azure_dbg.py /home/guestshell/azure/tools

cd bin
sudo mkdir /home/guestshell/azure/tools/bin
sudo chown guestshell /home/guestshell/azure/tools/bin
cp * /home/guestshell/azure/tools/bin

cd ../TokenMgr
sudo mkdir /home/guestshell/azure/tools/TokenMgr
sudo chown guestshell /home/guestshell/azure/tools/TokenMgr
cp at_command_file /home/guestshell/azure/tools/TokenMgr
cp auth-token.service /home/guestshell/azure/tools/TokenMgr

cd ../MetadataMgr
sudo mkdir /home/guestshell/azure/tools/MetadataMgr
sudo chown guestshell /home/guestshell/azure/tools/MetadataMgr
cp * /home/guestshell/azure/tools/MetadataMgr

echo "Azure tools file copy complete" >> $install_log

echo "Start installation of Azure tools" >> $install_log

'''
# Install the Azure CLI 2.0
if [ ! -e /usr/bin/az ]; then  
    sudo rpm --import https://packages.microsoft.com/keys/microsoft.asc

    sudo sh -c 'echo -e "[azure-cli]\nname=Azure CLI\nbaseurl=https://packages.microsoft.com/yumrepos/azure-cli\nenabled=1\ngpgcheck=1\ngpgkey=https://packages.microsoft.com/keys/microsoft.asc" > /etc/yum.repos.d/azure-cli.repo'

    yum check-update
    sudo yum install azure-cli -y
fi

#echo "Installed Azure CLI 2.0" >> $install_log
'''

# Install packages required for Managed Service Identity (MSI)
echo "Install configparser package via pip" >> $install_log
sudo pip install configparser >> $install_log 2>&1

echo "Install azure package via pip" >> $install_log
sudo pip install azure-storage >> $install_log 2>&1

echo "Install requests package via pip" >> $install_log
sudo pip install requests >> $install_log 2>&1

echo "Install pathlib package via pip" >> $install_log
sudo pip install pathlib >> $install_log 2>&1

echo "Install at package via yum" >> $install_log
sudo yum install at -y >> $install_log 2>&1

echo "Enable atd service" >> $install_log
sudo systemctl enable atd >> $install_log 2>&1

echo "Start atd service" >> $install_log
sudo systemctl start atd >> $install_log 2>&1

echo "Install crontab package via pip" >> $install_log
sudo pip install python-crontab

echo "Install urllib package via pip" >> $install_log
sudo pip install urllib3[secure]

echo "Azure tool installation complete" >> $install_log

# Set up the path to python scripts
export GS_PY_PATH=/home/guestshell/.local/lib/python2.7/site-packages/csr_azure_guestshell:/home/guestshell/.local/lib/python2.7/site-packages/csr_azure_guestshell/TokenMgr:/home/guestshell/.local/lib/python2.7/site-packages/csr_azure_guestshell/MetadataMgr:/home/guestshell/.local/lib/python2.7/site-packages/csr_azure_guestshell/bin

echo 'export PYTHONPATH=$PYTHONPATH:/home/guestshell/.local/lib/python2.7/site-packages/csr_azure_guestshell:/home/guestshell/.local/lib/python2.7/site-packages/csr_azure_guestshell/TokenMgr:/home/guestshell/.local/lib/python2.7/site-packages/csr_azure_guestshell/MetadataMgr:/home/guestshell/.local/lib/python2.7/site-packages/csr_azure_guestshell/bin' >> /home/guestshell/.bashrc
source /home/guestshell/.bashrc
export PATH=$PATH:$GS_PY_PATH

echo "Installing version $1 of csr_azure_guestshell package" >> $install_log
echo "Show the current PATH" >> $install_log
echo $PATH >> $install_log
echo "Show the current PYTHONPATH" >> $install_log
echo $PYTHONPATH >> $install_log
echo "Show the python sites" >> $install_log
python -m site >> $install_log

# Move the unit file for the auth-token service
sudo mv /home/guestshell/azure/tools/TokenMgr/auth-token.service /etc/systemd/user

# Start the token server
echo "Starting the auth-token service" >> $install_log
sudo systemctl enable /etc/systemd/user/auth-token.service
sudo systemctl start auth-token.service
sudo systemctl status auth-token >> $install_log

echo "Azure tool installation complete" >> $install_log
