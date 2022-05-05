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
	@echo "  "

init:
	@mkdir -p ~/.local/bin
	@export PATH=$PATH:~/.local/bin
	@chmod +x `pwd`/scripts/musta.sh
	@ln -sf `pwd`/scripts/musta.sh ~/.local/bin/musta

bootstrap: init
	@docker build -t "musta:Dockerfile" --build-arg USER_ID=${USERID} --build-arg GROUP_ID=${GROUPID} --no-cache .
	@echo "\nReady to start. Try:"
	@echo "\tmusta --help"

clean:
	@docker rmi -f musta:Dockerfile