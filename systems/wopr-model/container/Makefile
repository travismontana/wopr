test:
	docker build . -t wopr-model-local
	docker run -p 8000:8000 -v /remote/wopr:/remote/wopr wopr-model-local:latest
