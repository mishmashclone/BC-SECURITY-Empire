The following operating systems have been tested for Empire compatibility. We will be unable to provide support for other OSs at this time. Consider using our [Prebuilt Docker containers](#Docker) which can run on any system.
- Kali Linux
- Ubuntu
- Debian

## Kali

You can install the latest version of Empire by running the following:

```sh
apt install powershell-empire
```

## Github
_Debian, Kali, Ubuntu_

To install and run:

```sh
git clone https://github.com/BC-SECURITY/Empire.git
cd Empire
sudo ./setup/install.sh
sudo poetry install
sudo poetry run python empire --rest -n
```

## Docker
If you want to run Empire using a pre-built docker container:
```bash
docker pull bcsecurity/empire:{version}
docker run -it -p 1337:1337 -p 5000:5000 bcsecurity/empire:{version}

# with persistent storage
docker pull bcsecurity/empire:{version}
docker create -v /empire --name data bcsecurity/empire:{version}
docker run -it -p 1337:1337 -p 5000:5000 --volumes-from data bcsecurity/empire:{version}

# if you prefer to be dropped into bash instead of directly into empire
# docker run -it -p 1337:1337 -p 5000:5000 --volumes-from data bcsecurity/empire:{version} /bin/bash
```

All image versions can be found at: https://hub.docker.com/r/bcsecurity/empire/
* The last commit from master will be deployed to the `latest` tag
* The last commit from the dev branch will be deployed to the `dev` tag
* All github tagged releases will be deployed using their version numbers (v3.0.0, v3.1.0, etc)

# Community-Supported Operating Systems
At this time, we are choosing to only support Kali, Debian, and Ubuntu installations, however we will accept pull requests that fix issues or provide installation scripts specific to other operating systems to this wiki.

<!---
## Fedora
-->
