image ?= python3-stable
tag := $(shell date -I'date'| tr -d "[:punct:]")

define STR_HELP
This makefile can be used to build images and start containers.

Examples
--------
$ make start  # starts Docker service
$ make pull   # pulls a Docker image fron Docker hub
$ make build  # by default builds python3-stable image
$ make run
$ make build image=python2-stable
$ make cleanall  # clean (unnecessary, not all) containers and images

endef

export STR_HELP

.PHONY: help

help:
	@echo "$$STR_HELP"

start:
	systemctl start docker

dockermako:
	python make_files_with_mako.py
	
cleanmako:
	python -c 'from make_files_with_mako import clean; clean()'

build: dockermako
	docker build -f $(image).Dockerfile -t fluiddyn/$(image) .
	docker tag fluiddyn/$(image) fluiddyn/$(image):$(tag)

build_nocache: dockermako
	docker build -f $(image).Dockerfile -t fluiddyn/$(image) . --no-cache
	docker tag fluiddyn/$(image) fluiddyn/$(image):$(tag)

onbuild: dockermako
	docker build -f $(image).onbuild.Dockerfile -t fluiddyn/$(image):onbuild .

pull:
	docker pull fluiddyn/$(image)

push:
	docker push fluiddyn/$(image)

hgpush:
	hg book 'docker-$(tag)'
	hg push -B 'docker-$(tag)'

list:
	@printf "\nImages: "
	docker images
	@printf "\nContainers: "
	docker ps

run:
	docker run --name $(image) --restart always -it fluiddyn/$(image) bash

run_again:
	docker start $(image)
	docker attach $(image)

run_travis:
	docker run --name travis -it travisci/ci-python bash -c "su - travis"

run_travis_old:
	docker run --name travis_old -it quay.io/travisci/travis-python bash -c "su - travis"

cleancontainers:
	@echo "Clean exited containers."
	for cont in $$(docker ps -a | awk 'NR>1{print $$1}'); do docker stop $$cont; docker rm $$cont; done

cleanimages:
	@echo "Clean dangling images with no tag."
	for img in $$(docker images -qf "dangling=true"); do docker rmi -f $$img; done

cleanall: cleanmako cleancontainers cleanimages
