VENV=.venv
GET_PIP=get-pip.py
GET_PIP_URL=https://bootstrap.pypa.io/$(GET_PIP)

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

schema:
	cqlsh -f config/keyspace.cql
	cqlsh -f config/schema.cql

schema-ec2:
	cqlsh -f config/keyspace-ec2.cql
	cqlsh -f config/schema.cql

drop:
	cqlsh -f config/drop.cql

.PHONY: venv
