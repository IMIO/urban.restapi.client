#!/usr/bin/make
#

options =

all: run

.PHONY: bootstrap
bootstrap:
	virtualenv -p python3 .
	./bin/python bootstrap.py

.PHONY: buildout
buildout:
	if ! test -f bin/buildout;then make bootstrap;fi
	bin/buildout -vt 60

.PHONY: run
run:
	if ! test -f bin/mon_script;then make buildout;fi
	bin/mon_script load_configuration_example.cfg

.PHONY: cleanall
cleanall:
	rm -fr bin develop-eggs downloads eggs parts .installed.cfg

