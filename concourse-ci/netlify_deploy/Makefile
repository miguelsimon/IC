.PHONY: build
build:
	docker build -t netlify_deploy .

.PHONY: deploy
deploy:
	cd .. && \
		docker run -it --rm \
			-v $$(pwd)/comparison_outputs:/comparison_outputs:ro \
			netlify_deploy \
			netlify deploy \
				-d /comparison_outputs \
	    	-p \
	    	-s "$$(cat credentials/NETLIFY_SITE_ID)" \
	    	-a "$$(cat credentials/NETLIFY_AUTH_TOKEN)"
