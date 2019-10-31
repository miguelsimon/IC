py_dirs = assemble_jobs
py_files = $(wildcard assemble_jobs/*.py)


.PHONY: fmt
fmt: env_ok
	env/bin/isort -sp .isort.cfg $(py_files)
	env/bin/black $(py_files)


.PHONY: test
test: check
	env/bin/python -m unittest discover $(py_dirs) -p "*.py" -v


.PHONY: check
check: env_ok
	env/bin/python -m mypy \
		--check-untyped-defs \
		--ignore-missing-imports \
		assemble_jobs
	env/bin/python -m flake8 --select F $(py_dirs)
	env/bin/isort  -sp .isort.cfg  --check $(py_files)
	env/bin/black --check $(py_files)


env_ok: requirements.txt
	rm -rf env env_ok
	python3 -m venv env
	env/bin/pip install -r requirements.txt
	touch env_ok


.PHONY: clean
clean:
	rm -rf env env_ok


.PHONY: fly_remote_login
fly_remote_login:
	fly -t remote login \
	  -c https://gpu1next.ific.uv.es

.PHONY: fly_execute
fly_execute:
	fly -t local execute \
		--include-ignored \
		--input IC=../ \
		--config run-tests.yml

.PHONY: set_local_pr_pipeline
set_local_pr_pipeline: credentials/github_access_token credentials/key_concourse
	fly -t local set-pipeline \
    --pipeline IC-pull-request \
    --config pr-pipeline.yml \
		-v "SSH_PRIVATE_KEY=$$(cat credentials/key_concourse)" \
		-v github_access_token=$$(cat credentials/github_access_token)

.PHONY: set_pr_pipeline
set_pr_pipeline: credentials/github_access_token credentials/key_concourse
	fly -t remote set-pipeline \
    --pipeline IC-pull-request \
    --config pr-pipeline.yml \
		-v "SSH_PRIVATE_KEY=$$(cat credentials/key_concourse)" \
		-v github_access_token=$$(cat credentials/github_access_token)


.PHONY: launch_prod_concourse
launch_prod_concourse: credentials/CONCOURSE_TEST_PASSWORD
	docker-compose -f prod-docker-compose.yml down -v --remove-orphans
	docker-compose -f prod-docker-compose.yml run make_dummy_certs
	CONCOURSE_TEST_PASSWORD=$$(credentials/CONCOURSE_TEST_PASSWORD) docker-compose -f prod-docker-compose.yml up -d nginx
	docker-compose -f prod-docker-compose.yml run erase_certs
	docker-compose -f prod-docker-compose.yml run create_certs
	docker-compose -f prod-docker-compose.yml exec nginx nginx -s reload
