# Makefile for Sectify

up:
	docker-compose up -d

down:
	docker-compose down

clean: 
	rm -rf ./uploads/* ./models/*