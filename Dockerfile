# NOTE: Only use this when you want to build image locally
#       else use `docker pull bcsecurity/empire:{VERSION}`
#       all image versions can be found at: https://hub.docker.com/r/bcsecurity/empire/

# -----BUILD COMMANDS----
# 1) build command: `docker build -t bcsecurity/empire .`
# 2) create volume storage: `docker create -v /empire --name data bcsecurity/empire`
# 3) run out container: `docker run -ti --volumes-from data bcsecurity/empire /bin/bash`

# -----RELEASE COMMANDS----
# Handled by GitHub Actions

# -----BUILD ENTRY-----

# image base
FROM python:3.7.5-buster

# extra metadata
LABEL maintainer="bc-security"
LABEL description="Dockerfile base for Empire server."

# env setup
ENV STAGING_KEY=RANDOM
ENV DEBIAN_FRONTEND=noninteractive

# set the def shell for ENV
SHELL ["/bin/bash", "-c"]

RUN apt-get update && \
      apt-get -y install \
        sudo \
        lsb-release \
	    make \
	    g++ \
	    python3-dev \
	    swig \
	    python-pip \
	    libxml2-dev \
	    default-jdk \
	    libffi-dev \
	    libssl1.1 \
	    libssl-dev \
	    build-essential \
	    apt-transport-https \
	    curl \
	    gnupg

RUN wget https://packages.microsoft.com/config/debian/10/packages-microsoft-prod.deb && \
    sudo dpkg -i packages-microsoft-prod.deb && \
    sudo apt-get update && \
    sudo apt-get install -y powershell

WORKDIR /empire

COPY setup/requirements.txt /empire

RUN pip install -r requirements.txt

COPY . /empire

RUN rm -rf /empire/data/empire*

RUN cd setup && ./reset.sh

RUN cd setup && ./cert.sh

CMD ["python", "empire", "--rest"]
