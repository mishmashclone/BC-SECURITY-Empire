#!/bin/bash
function install_powershell() {
  echo -e "x1b[1;34m[*] Installing Powershell\x1b[0m"
  if [ $OS_NAME == "DEBIAN" ]; then
    wget https://packages.microsoft.com/config/debian/10/packages-microsoft-prod.deb
    sudo dpkg -i packages-microsoft-prod.deb
    sudo apt-get update
    sudo apt-get install -y powershell
  elif [ $OS_NAME == "UBUNTU" ]; then
    sudo apt-get update
    sudo apt-get install -y wget apt-transport-https software-properties-common
    wget -q https://packages.microsoft.com/config/ubuntu/20.04/packages-microsoft-prod.deb
    sudo dpkg -i packages-microsoft-prod.deb
    sudo apt-get update
    sudo add-apt-repository universe
    sudo apt-get install -y powershell
  elif [ $OS_NAME == "KALI" ]; then
    apt update && apt -y install powershell
  fi
}

function install_xar() {
  # xar-1.6.1 has an incompatibility with libssl 1.1.x that is patched here
  wget https://github.com/BC-SECURITY/xar/archive/xar-1.6.1-patch.tar.gz
  rm -rf xar-1.6.1
  rm -rf xar-1.6.1-patch/xar
  tar -xvf xar-1.6.1-patch.tar.gz && mv xar-xar-1.6.1-patch/xar/ xar-1.6.1/
  (cd xar-1.6.1 && ./autogen.sh)
  (cd xar-1.6.1 && ./configure)
  (cd xar-1.6.1 && make)
  (cd xar-1.6.1 && sudo make install)
}

function install_bomutils() {
  rm -rf bomutils
  git clone https://github.com/BC-SECURITY/bomutils.git
  (cd bomutils && make)
  (cd bomutils && sudo make install)
  chmod 755 bomutils/build/bin/mkbom && sudo cp bomutils/build/bin/mkbom /usr/local/bin/.
}

export DEBIAN_FRONTEND=noninteractive
set -e

apt-get update && apt-get install -y wget sudo

sudo -v

OS_NAME=
VERSION_ID=
if grep "10.*" /etc/debian_version 2>/dev/null; then
  echo -e "\x1b[1;34m[*] Detected Debian 10\x1b[0m"
  OS_NAME=DEBIAN
  VERSION_ID=$(cat /etc/debian_version)
elif grep -i "NAME=\"Ubuntu\"" /etc/os-release 2>/dev/null; then
  OS_NAME=UBUNTU
  VERSION_ID=$(grep -i VERSION_ID /etc/os-release | grep -o -E [[:digit:]]+\\.[[:digit:]]+)
  if [ $VERSION_ID != "20.04" ]; then
    echo -e '\x1b[1;31m[!] Ubuntu must be 20.04\x1b[0m' && exit
  fi
  echo -e "\x1b[1;34m[*] Detected Ubuntu 20.04\x1b[0m"
elif grep -i "Kali" /etc/os-release 2>/dev/null; then
  echo -e "\x1b[1;34m[*] Detected Kali\x1b[0m"
  OS_NAME=KALI
  VERSION_ID=KALI_ROLLING
else
  echo -e '\x1b[1;31m[!] Unsupported OS. Exiting.\x1b[0m' && exit
fi

if [ $OS_NAME == "DEBIAN" ]; then
  sudo apt-get update
  sudo apt-get -y install -y python3-dev python3-pip
elif [ $OS_NAME == "UBUNTU" ] && [ $VERSION_ID == "20.04" ]; then
  sudo apt-get update
  sudo apt-get -y install -y python3-dev python3-pip
elif [ $OS_NAME == "KALI" ]; then
  apt-get update
  sudo apt-get -y install -y python3-dev python3-pip
fi

install_powershell

echo -n -e "\x1b[1;33m[>] Do you want to install xar and bomutils? They are only needed to generate a .dmg stager (y/N)? \x1b[0m"
read answer
if [ "$answer" != "${answer#[Yy]}" ] ;then
  sudo apt-get install -y make autoconf g++ git zlib1g-dev libxml2-dev libssl1.1 libssl-dev
  install_xar
  install_bomutils
else
    echo -e "\x1b[1;34m[*] Skipping xar and bomutils\x1b[0m"
fi

echo -n -e "\x1b[1;33m[>] Do you want to install OpenJDK? It is only needed to generate a .jar stager (y/N)? \x1b[0m"
read answer
if [ "$answer" != "${answer#[Yy]}" ] ;then
  sudo apt-get install -y default-jdk
  echo -e "\x1b[1;34m[*] Installing OpenJDK\x1b[0m"
else
  echo -e "\x1b[1;34m[*] Skipping OpenJDK\x1b[0m"
fi

echo -n -e "\x1b[1;33m[>] Do you want to install dotnet? It is needed to use CSharp agents and CSharp modules (y/N)? \x1b[0m"
read answer
if [ "$answer" != "${answer#[Yy]}" ] ;then
  if [ $OS_NAME == "DEBIAN" ]; then
    wget https://packages.microsoft.com/config/debian/10/packages-microsoft-prod.deb -O packages-microsoft-prod.deb
    sudo dpkg -i packages-microsoft-prod.deb
    sudo apt-get update
    sudo apt-get install -y apt-transport-https dotnet-sdk-3.1
  elif [ $OS_NAME == "UBUNTU" ]; then
    wget https://packages.microsoft.com/config/ubuntu/20.04/packages-microsoft-prod.deb -O packages-microsoft-prod.deb
    sudo dpkg -i packages-microsoft-prod.deb
    sudo apt-get update
    sudo apt-get install -y apt-transport-https dotnet-sdk-3.1
  elif [ $OS_NAME == "KALI" ]; then
    wget https://packages.microsoft.com/config/debian/10/packages-microsoft-prod.deb -O packages-microsoft-prod.deb
    sudo dpkg -i packages-microsoft-prod.deb
    sudo apt-get update
    sudo apt-get install -y apt-transport-https dotnet-sdk-3.1
  fi
else
  echo -e "\x1b[1;34m[*] Skipping dotnet\x1b[0m"
fi

echo -e "\x1b[1;34m[*] Checking Python version\x1b[0m"
python_version=($(python3 -c 'import sys; print("{} {}".format(sys.version_info.major, sys.version_info.minor))'))

if [ "${python_version[0]}" -eq 3 ] && [ "${python_version[1]}" -lt 7 ]; then
  echo -e "\x1b[1;34m[*] Python3 version less than 3.7, installing 3.7\x1b[0m"
  apt-get install python3.7 python3.7-dev
  python3.7 -m pip install poetry
else
  python3 -m pip install poetry
fi

echo -e "\x1b[1;34m[[*] Installing Poetry\x1b[0m"
poetry install

echo -e '\x1b[1;34m[*] Install Complete!\x1b[0m'
echo -e '\x1b[1;34m[*] poetry run python empire.py server\x1b[0m'
echo -e '\x1b[1;34m[*] poetry run python empire.py client\x1b[0m'
