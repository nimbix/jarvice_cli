# CentOS 6

## Install the following packages with yum:

yum install -y \
    python-pip \
    python-devel \
    openssl-devel \
    libffi-devel \
    python-argparse

## Use PIP to install the jarviceclient from PyPI

### Install locally with --user

pip install --user jarviceclient

### Install globally with sudo

sudo pip install jarviceclient

