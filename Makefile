PROTOC = python -m grpc_tools.protoc
PROTO_DIR = ./protos
PYTHON = python

init:
	sudo apt install protobuf-compiler
	pip install -r requirements.txt

build:
	rm -f $(PROTO_DIR)/*_pb2.py
	$(PROTOC) -I=$(PROTO_DIR) --python_out=$(PROTO_DIR) --grpc_python_out=$(PROTO_DIR) $(PROTO_DIR)/*.proto

run-server: build
	cd server; PYTHONPATH=${CURDIR} python main.py --sources=localhost:50090

run-test-client-app: build
	cd test; PYTHONPATH=${CURDIR} python client_app.py --grpc_port=50090

run-web-server: build
	cd webserver; PYTHONPATH=${CURDIR} python main.py