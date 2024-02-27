#==============================================================================
# Using OSGeo GDAL container as base

# Podman commands
# ---------------
# # See if the podman machine is initialised
# podman machine info
#
# # If required, initialise the podman machine with a volume mount
# podman machine init -v $HOME:$HOME
#
# # If required, start the podmain machine
# podman machine start
#
# # (Optional) pull the image to local
# podman pull <FROM image>
#
# # Build Image
# podman build -t egs-dc-gdal-image:latest -f Containerfile.gdal-python
#
# # Run image and launch bash
# podman container run -d -it --name egs-dc-gdal-container --env-file .env localhost/egs-dc-gdal-image:latest
#
# # In seperate shell,get the local container id
# podman ps
#
# # Option A attach to the container
# podman attach <container-id>
#
# # Option B execute the launch of a bash shell
# podman exec -it egs-dc-gdal-container /bin/bash
# python /usr/app/egs-dc-pipeline/src/main310.py
#
# # Copy a file into container
# podman cp <local-file> <container-id>:<container-file>
#
# # App is located at /usr/app/egs-dc-pipeline/src/main310.py
#
# # VPN issue with WSL, cannot connect to internet
# # WSL connect issues with VPN https://github.com/microsoft/wsl/issues/4698
#=========================

# Container image https://github.com/OSGeo/gdal/pkgs/container/gdal
FROM ghcr.io/osgeo/gdal:ubuntu-small-3.8.1 AS ubuntu-gdal
# FROM ghcr.io/osgeo/gdal:ubuntu-small-latest-arm64
# # Docker image registry
# FROM osgeo/gdal

ENV APPNAME=egs-dc-pipeline
ENV APPDIR=/usr/app

# Non interactive apt installs
ENV DEBIAN_FRONTEND=noninteractive

WORKDIR $APPDIR

# Update apt-get
RUN apt-get update

# Install python and pip
RUN python3 --version
RUN apt-get install -y python3.10 python3-pip

# Upgrade pip
RUN pip3 install --upgrade pip

# Install git
RUN apt-get install -y  git

# Copy code into the apps venv
COPY requirements-gdal-container.txt $APPDIR/$APPNAME-requirements.txt
COPY src $APPDIR/$APPNAME/src
COPY script $APPDIR/$APPNAME/script

# Manage the NRCan custom certificate to ensure SSL is supported everywhere
COPY NRCAN-Root-2019-B64.cer .
# Add NRCAN-Root-2019-B64.cer to etc/ssl/certs/ca-certificates.crt
RUN cp NRCAN-Root-2019-B64.cer /usr/local/share/ca-certificates/cert.crt && chmod 644 /usr/local/share/ca-certificates/cert.crt && update-ca-certificates

# Set the env vars for the ca bundle
ENV REQUESTS_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt
ENV CURL_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt
ENV AWS_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt
ENV SSL_CERT_FILE=/etc/ssl/certs/ca-certificates.crt

# install dependencies
RUN pip3 install --upgrade -r $APPDIR/$APPNAME-requirements.txt

# Reminder where the app is
RUN echo "The app is here $APPDIR/$APPNAME/src/main310.py."


