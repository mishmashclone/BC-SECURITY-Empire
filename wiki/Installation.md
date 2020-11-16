# Kali

You can install the latest version of Empire by running the following:

```sh
apt install powershell-empire
```

# Github

To install and run:

```sh
git clone https://github.com/BC-SECURITY/Empire.git
cd Empire
sudo ./setup/install.sh
```

There's also a [quickstart here](http://www.powershellempire.com/?page_id=110) and full [documentation here](http://www.powershellempire.com/?page_id=83).

# Docker
If you want to run Empire using a pre-built docker container:
```bash
docker pull bcsecurity/empire:{version}
docker run -it bcsecurity/empire:{version}

# with persistent storage
docker pull bcsecurity/empire:{version}
docker create -v /empire --name data bcsecurity/empire:{version}
docker run -it --volumes-from data bcsecurity/empire:{version}

# if you prefer to be dropped into bash instead of directly into empire
# docker run -it --volumes-from data bcsecurity/empire:{version} /bin/bash
```

All image versions can be found at: https://hub.docker.com/r/bcsecurity/empire/
* The last commit from master will be deployed to the `latest` tag
* The last commit from the dev branch will be deployed to the `dev` tag
* All github tagged releases will be deployed using their version numbers (v3.0.0, v3.1.0, etc)