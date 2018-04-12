#!/bin/bash
#bebop build install script
mkdir Bebop-SDK
cd Bebop-SDK
sudo apt install -y git build-essential autoconf libtool python python3 libavahi-client-dev libavcodec-dev libavformat-dev libswscale-dev libncurses5-dev mplayer repo
repo init -u https://github.com/Parrot-Developers/arsdk_manifests.git -m release.xml
repo sync
./build.sh -p arsdk-native -t build-sdk -j
./build.sh -p arsdk-native -t build-sample-BebopSample -j