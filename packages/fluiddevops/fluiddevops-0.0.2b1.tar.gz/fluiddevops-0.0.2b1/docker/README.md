# Building and running Docker containers

This repository contains Dockerfiles for various FluidDyn containers.

Dockerfiles are text files that contain the instructions for building a Docker
image.

## Installation
The containers were all built using Docker 1.13.x.  
Go to https://www.docker.com for information on how to install docker.

## Building and running containers

To build a container, run:

```$ make build image=python3-stable```

To launch a container, run:

```$ make run image=python3-stable```

To launch Travis Ubuntu (precise) container for testing Python

```$ make run_travis```

See the Docker documentaion for information on the different docker commands
that you can use.

## Docker hub

Images of all the containers listed here are available on Docker Hub:
https://hub.docker.com/u/fluiddyn.

For example, running:

```$ docker pull fluiddyn/python3-stable```

will retrieve the Docker official python 3.6 installation along with extra
libraries from Debian Jessie repos and python packages from PyPI required for
FluidDyn.

```$ docker run -it fluiddyn/python3-stable /bin/bash```

And the image will be downloaded from Docker Hub if it is not already present on your machine
and then run.

## Ingredients

Note: Extra libraries (from official Debian Jessie repos) are not the most
recent versions.

see `apt_requirements.txt`, `requirements.txt` and `requirements_extra.txt`
for the list of packages being pre-installed into the Docker images.
