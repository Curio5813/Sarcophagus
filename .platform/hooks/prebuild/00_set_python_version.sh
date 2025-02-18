#!/bin/bash
echo "Setting Python 3.11 as default..."
sudo alternatives --set python /usr/bin/python3.11
sudo yum install -y python3.11-venv

