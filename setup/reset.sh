#!/bin/bash

if [[ $EUID -ne 0 ]]; then
   echo " [!] This script must be run as root" 1>&2
   exit 1
fi

IFS='/' read -a array <<< pwd

# remove the debug file if it exists
cd empire/server

if [ -e empire.debug ]
then
	rm empire.debug
fi

# remove the download folders
if [ -d ./downloads/ ]
then
	rm -rf ./downloads/
fi

# remove the compiled csharp folders
if [ -d ./csharp/Covenant/bin ]
then
	rm -rf ./csharp/Covenant/bin
fi
if [ -d ./csharp/Covenant/obj ]
then
	rm -rf ./csharp/Covenant/obj
fi

cd ../..
