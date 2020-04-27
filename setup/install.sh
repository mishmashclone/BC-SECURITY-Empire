#!/bin/bash
function install_powershell() {
	# Deb 10.x
	if cat /etc/debian_version | grep 10.* ; then
    # Download the Microsoft repository GPG keys
    wget https://packages.microsoft.com/config/debian/10/packages-microsoft-prod.deb

    # Register the Microsoft repository GPG keys
    sudo dpkg -i packages-microsoft-prod.deb

    # Update the list of products
    sudo apt-get update

    # Install PowerShell
    sudo apt-get install -y powershell
	# Deb 9.x
	elif cat /etc/debian_version | grep 9.* ; then
		# Install system components
		sudo apt-get install -y apt-transport-https curl
		# Import the public repository GPG keys
		curl https://packages.microsoft.com/keys/microsoft.asc | sudo apt-key add -
		# Register the Microsoft Product feed
		sudo sh -c 'echo "deb [arch=amd64] https://packages.microsoft.com/repos/microsoft-debian-stretch-prod stretch main" > /etc/apt/sources.list.d/microsoft.list'
		# Update the list of products
		sudo apt-get update
		# Install PowerShell
		sudo apt-get install -y powershell
	# Deb 8.x
	elif cat /etc/debian_version | grep 8.* ; then
		# Install system components
		sudo apt-get install -y apt-transport-https curl gnupg
		# Import the public repository GPG keys
		curl https://packages.microsoft.com/keys/microsoft.asc | sudo apt-key add -
		# Register the Microsoft Product feed
		sudo sh -c 'echo "deb [arch=amd64] https://packages.microsoft.com/repos/microsoft-debian-jessie-prod jessie main" > /etc/apt/sources.list.d/microsoft.list'
		# Update the list of products
		sudo apt-get update
		# Install PowerShell
		sudo apt-get install -y powershell
	#Ubuntu
	elif lsb_release -d | grep -q "Ubuntu"; then
		# Read Ubuntu version
		local ubuntu_version=$( grep 'DISTRIB_RELEASE=' /etc/lsb-release | grep -o -E [[:digit:]]+\\.[[:digit:]]+ )
		# Install system components
		sudo apt-get install -y apt-transport-https curl
		# Import the public repository GPG keys
		curl https://packages.microsoft.com/keys/microsoft.asc | sudo apt-key add -
		# Register the Microsoft Ubuntu repository
		curl https://packages.microsoft.com/config/ubuntu/$ubuntu_version/prod.list | sudo tee /etc/apt/sources.list.d/microsoft.list
		# Update the list of products
		sudo apt-get update
		# Install PowerShell
		sudo apt-get install -y powershell
	#Kali Linux
	elif lsb_release -d | grep -q "Kali"; then
		apt update && apt -y install powershell
	fi
	if ls /opt/microsoft/powershell/*/DELETE_ME_TO_DISABLE_CONSOLEHOST_TELEMETRY; then
		rm /opt/microsoft/powershell/*/DELETE_ME_TO_DISABLE_CONSOLEHOST_TELEMETRY
	fi
	mkdir -p /usr/local/share/powershell/Modules
	cp -r ../lib/powershell/Invoke-Obfuscation /usr/local/share/powershell/Modules
}

function install_xar() {
	# xar-1.6.1 has an incompatability with libssl 1.1.x that is patched here
	# for older OS on libssl 1.0.x, we continue to use 1.6.1
	if is_libssl_1_0; then
		wget https://github.com/BC-SECURITY/xar/archive/xar-1.6.1.tar.gz
		tar -xvf xar-1.6.1.tar.gz && mv xar-xar-1.6.1/xar/ xar-1.6.1/
	else
		wget https://github.com/BC-SECURITY/xar/archive/xar-1.6.1-patch.tar.gz
		tar -xvf xar-1.6.1-patch.tar.gz && mv xar-xar-1.6.1-patch/xar/ xar-1.6.1/
	fi
	(cd xar-1.6.1 && ./autogen.sh)
	(cd xar-1.6.1 && ./configure)
	(cd xar-1.6.1 && make)
	(cd xar-1.6.1 && sudo make install)
}

function install_bomutils() {
	git clone https://github.com/hogliux/bomutils.git
	(cd bomutils && make)
	(cd bomutils && make install)
	chmod 755 bomutils/build/bin/mkbom && sudo cp bomutils/build/bin/mkbom /usr/local/bin/.
}

# Because of some dependencies (xar) needing to know which OS has libssl 1.0
# and because some OS are locked into 1.0, we are checking for Ubuntu < 18 and Debian < 9 here.
function is_libssl_1_0() {
	if lsb_release -d | grep -q "Ubuntu"; then
		if [ $(lsb_release -rs | cut -d "." -f 1) -lt 18 ]; then
			return
		fi
	fi

	if [ $(cut -d "." -f 1 /etc/debian_version) -lt 9 ]; then
		return
	fi

	false
}

# Ask for the administrator password upfront so sudo is no longer required at Installation.
sudo -v

IFS='/' read -a array <<< pwd

if [[ "$(pwd)" != *setup ]]
then
	cd ./setup
fi

Pip_file="requirements.txt"

if lsb_release -d | grep -q "Kali"; then
	apt-get update
	sudo apt-get install -y make autoconf g++ python3-dev swig python3-pip libxml2-dev default-jdk zlib1g-dev libssl1.1 build-essential libssl-dev libxml2-dev zlib1g-dev
elif lsb_release -d | grep -q "Ubuntu"; then
	if is_libssl_1_0; then
		LibSSL_pkgs="libssl1.0.0 libssl-dev"
		Pip_file="requirements_libssl1.0.txt"
	else
		LibSSL_pkgs="libssl1.1 libssl-dev"
	fi
	sudo apt-get update
	sudo apt-get install -y make autoconf g++ python3-dev swig python3-pip libxml2-dev default-jdk $LibSSL_pkgs build-essential
else
	echo "Unknown distro - Debian/Ubuntu Fallback"
	if is_libssl_1_0; then
		LibSSL_pkgs="libssl1.0.0 libssl-dev"
		Pip_file="requirements_libssl1.0.txt"
	else
		LibSSL_pkgs="libssl1.1 libssl-dev"
	fi
	sudo apt-get update
	sudo apt-get install -y make autoconf g++ python3-dev swig python3-pip libxml2-dev default-jdk libffi-dev $LibSSL_pkgs build-essential
fi

install_xar

install_bomutils

install_powershell

if ls /usr/bin/ | grep -q "python3"; then
	if ! type pip3 > /dev/null; then
		sudo apt-get --assume-yes install python3-pip
	fi
	sudo pip3 install -r $Pip_file
fi

# set up the database schema
python3 ./setup_database.py

# generate a cert
./cert.sh

cd ..

echo -e '\n [*] Setup complete!\n'
