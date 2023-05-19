BUILD_DIR=build

.PHONY: all

all:
	mkdir -p ${BUILD_DIR}
	cp robots.txt ${BUILD_DIR}
	cp *.css ${BUILD_DIR}
	cp *.js ${BUILD_DIR}
	python3 make-website.py -B ${BUILD_DIR}

start-test-server:
	python3 -m http.server -d ${BUILD_DIR} 8080

clean:
	rm -rf ${BUILD_DIR}