UNAME_S := $(shell uname -s)
USERID=$(shell id -u)

ifeq ($(UNAME_S), Darwin)
GROUPID=1000
else
GROUPID=$(shell id -g)
endif

help:
	@echo "Please use \`make <target>\` where <target> is one of"
	@echo "  bootstrap               build the musta image"
	@echo "  clean                   remove the musta image from your computer"
	@echo "  purge                   remove all unused containers, networks, images and volumes"
	@echo "  "

init:
	@mkdir -p ~/.local/bin
	@export PATH=$PATH:~/.local/bin
	@chmod +x `pwd`/scripts/musta.sh
	@ln -sf `pwd`/scripts/musta.sh ~/.local/bin/musta
	@ln -sf `pwd`/scripts/musta_lib.sh ~/.local/bin/musta_lib.sh

bootstrap: init
	@docker build -t "musta:Dockerfile" --build-arg USER_ID=${USERID} --build-arg GROUP_ID=${GROUPID} --no-cache .
	@echo "\nReady to start. Try:"
	@echo "\tmusta --help"

clean:
	@docker rmi -f musta:Dockerfile
	@docker volume prune -f
	@rm ~/.local/bin/musta

purge: clean
	@docker system prune  -a -f
	@docker system prune  -a --volumes -f
