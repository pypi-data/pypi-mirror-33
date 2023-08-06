#!/bin/bash

install_log="/home/guestshell/azure/waagent/install.log"

echo "Installing waagent" > $install_log
cd waagent
echo "going to install rpm" >> $install_log
sudo yum -y localinstall WALinuxAgent-2.2.14.1.6-1.noarch.rpm
echo "Starting waagent daemon" >> $install_log
sudo systemctl enable /usr/lib/systemd/system/waagent.service
sudo service waagent start
systemctl status waagent >> $install_log
echo "Waagent daemon running" >> $install_log
