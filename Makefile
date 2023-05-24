BUILD_DIR=build

.PHONY: all static

all: static
	python3 make-website.py -B ${BUILD_DIR}

static:
	mkdir -p ${BUILD_DIR}
	cp -r static/* ${BUILD_DIR}/

start-test-server:
	python3 test-server.py

clean:
	rm -rf ${BUILD_DIR}
