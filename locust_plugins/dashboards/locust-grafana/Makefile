TAG=3
IMAGE_NAME=cyberw/locust-grafana:$(TAG)

build:
	docker build --progress plain . -t $(IMAGE_NAME)

push:
	docker push $(IMAGE_NAME)

run:
	docker run -p 3000:3000 $(IMAGE_NAME)

shell:
	docker run -p 3000:3000 -it --entrypoint=/bin/bash $(IMAGE_NAME)