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
      apt-get -y install sudo && \
      apt-get -y install lsb-release

COPY . /empire

RUN cd /empire/setup/ && \
    ./install.sh && \
    rm -rf /empire/data/empire*

RUN python /empire/setup/setup_database.py

WORKDIR /empire

CMD ["python", "empire"]
