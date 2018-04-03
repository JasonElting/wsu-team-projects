#!/bin/bash
sudo apt-get install patch xsltproc gcc libreadline-dev python-dev
git clone https://github.com/gotthardp/python-mercuryapi.git
cd python-mercuryapi
make
sudo make install
sudo usermod -a -G dialout $(whoami)
