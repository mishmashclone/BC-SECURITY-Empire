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
FROM python:3.9.9-buster

# extra metadata
LABEL maintainer="bc-security"
LABEL description="Dockerfile for Empire server and client. https://bc-security.gitbook.io/empire-wiki/quickstart/installation#docker"

# env setup
ENV STAGING_KEY=RANDOM
ENV DEBIAN_FRONTEND=noninteractive

# set the def shell for ENV
SHELL ["/bin/bash", "-c"]

RUN apt-get update && \
      apt-get -y install \
        sudo \
	    python3-dev \
	    python3-pip \
	    apt-transport-https \
    && rm -rf /var/lib/apt/lists/*

RUN wget https://packages.microsoft.com/config/debian/10/packages-microsoft-prod.deb && \
    sudo dpkg -i packages-microsoft-prod.deb && \
    sudo apt-get update && \
    sudo apt-get install -y powershell \
    && rm -rf /var/lib/apt/lists/*

RUN wget https://packages.microsoft.com/config/debian/10/packages-microsoft-prod.deb -O packages-microsoft-prod.deb && \
    sudo dpkg -i packages-microsoft-prod.deb && \
    sudo apt-get update && \
    sudo apt-get install -y apt-transport-https dotnet-sdk-3.1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /empire

COPY pyproject.toml /empire

COPY . /empire

RUN mkdir -p /usr/local/share/powershell/Modules && \
    cp -r ./empire/server/powershell/Invoke-Obfuscation /usr/local/share/powershell/Modules

RUN sudo pip install poetry && sudo poetry config virtualenvs.create false && sudo poetry install

RUN /empire/setup/reset.sh
RUN rm -rf /empire/server/data/empire*

ENTRYPOINT ["./ps-empire"]
CMD ["server"]
