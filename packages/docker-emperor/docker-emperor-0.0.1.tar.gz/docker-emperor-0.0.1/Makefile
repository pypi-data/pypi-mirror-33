deploy:
	make pypi_upload

pypi_upload:
	python setup.py sdist upload -r pypi || echo 'docker-emperor is up-to-date'

develop:
	python setup.py develop --user