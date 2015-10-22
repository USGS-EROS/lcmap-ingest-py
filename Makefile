VENV=.venv
CCM_VENV=.venv-ccm
GET_PIP=get-pip.py
GET_PIP_URL=https://bootstrap.pypa.io/$(GET_PIP)

.PHONY: venv ccm

$(VENV):
	python3.4 -m venv $(VENV) --without-pip --system-site-packages
	wget $(GET_PIP_URL)
	. $(VENV)/bin/activate && \
	python $(GET_PIP) && \
	rm $(GET_PIP)

deps: $(VENV)
	. $(VENV)/bin/activate && \
	pip install -r requirements.txt

venv: deps

schema-local:
	cqlsh -f db/keyspace-local.cql
	cqlsh -f db/schema.cql

schema-dc:
	cqlsh -f db/keyspace-dc.cql
	cqlsh -f db/schema.cql

schema-ec2:
	cqlsh -f db/keyspace-ec2.cql
	cqlsh -f db/schema.cql

schema-ccm:
	. $(CCM_VENV)/bin/activate && \
	~/.ccm/testcluster/node1/bin/cqlsh -f db/keyspace-local.cql && \
	~/.ccm/testcluster/node1/bin/cqlsh -f db/schema.cql

drop:
	cqlsh -f db/drop.cql

drop-ccm:
	~/.ccm/testcluster/node1/bin/cqlsh -f db/drop.cql

$(CCM_VENV):
	virtualenv --python=python2.7 --system-site-packages --no-pip $(CCM_VENV)
	wget $(GET_PIP_URL)
	. $(CCM_VENV)/bin/activate && \
	python $(GET_PIP) && \
	rm $(GET_PIP)

ccm: $(CCM_VENV)
	. $(CCM_VENV)/bin/activate && \
	pip install ccm && \
	pip install -r requirements.txt && \
	pip install ~/.ccm/repository/2.2.1/pylib/ && \
	ccm create testcluster -v 2.2.1 && \
	ccm populate -n 3 \
	ccm start
	make schema-ccm

ccm-start:
	. $(CCM_VENV)/bin/activate && \
	ccm start

