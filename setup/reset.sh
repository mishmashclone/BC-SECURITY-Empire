#!/bin/bash

if [[ $EUID -ne 0 ]]; then
   echo " [!] This script must be run as root" 1>&2
   exit 1
fi

IFS='/' read -a array <<< pwd

# remove generated-stagers
rm -rf empire/client/generated-stagers/*

# remove the debug file if it exists
cd empire/server

# delete the default named empire.db
rm data/empire.db

if [ -e empire.debug ]
then
	rm empire.debug
fi

# remove the download folders
rm -rf ./downloads/*

# remove the compiled csharp folders
if [ -d ./csharp/Covenant/bin ]
then
	rm -rf ./csharp/Covenant/bin
fi
if [ -d ./csharp/Covenant/obj ]
then
	rm -rf ./csharp/Covenant/obj
fi

# remove compiled csharp tasks
rm -rf ./csharp/Covenant/Data/Tasks/CSharp/Compiled/net35/*
rm -rf ./csharp/Covenant/Data/Tasks/CSharp/Compiled/net40/*
rm -rf ./csharp/Covenant/Data/Tasks/CSharp/Compiled/netcoreapp3.0/*

# remove invoke-obfuscation files and re-add
rm -rf /usr/local/share/powershell/Modules/Invoke-Obfuscation/
mkdir -p /usr/local/share/powershell/Modules
cp -r ./powershell/Invoke-Obfuscation /usr/local/share/powershell/Modules
cd ../..
