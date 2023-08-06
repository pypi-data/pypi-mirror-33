# Documentation

## Build HTML documentation

The following will run on OSX, Linux, and Windows. There is a Unix style `Makefile`, as well as `make.bat` for Windows users.

### Install dependencies
```
pip install sphinx
```

### Generate documentation
```
# generate RST docs
sphinx-apidoc -f -o docs/source e3db
# remove missing environment variable errors
export REGISTRATION_TOKEN=FOO
export DEFAULT_API_URL=FOO
# generate html docs from RST ones
make html
```

# Formatting

The e3db-python SDK uses flake8 for style enforcement against the pep8 standard, as well as programming standards. Flake8 configuration is stored in `.flake8`

## Install Flake8

```
pip install flake8
```

## Use Flake8
```
flake8 e3db/
```

# Tests

## Install dependencies
Tests for the e3db-python SDK use pytest. This can be installed by running the following:
```bash
pip install pytest pytest-cov
```

## Setup environment variables

We need to set a few environment variables that the integration tests require.
The tests will dynamically generate a few clients, and use the server specified
in `DEFAULT_API_URL`.

```bash
export REGISTRATION_TOKEN=<TOKEN>
export DEFAULT_API_URL=<https://api.url>
```

## Run tests and generate a verbose report output

```bash
pytest --cov-report term-missing --cov -v e3db
```

# Build Docker containers

```bash
docker build -t tozny/e3db-python:debian .
```

## Run Docker container for testing

This container was built in the previous step, and will have the current code base in the repo running inside it. It is currently necessary to re-build the docker container for code changes due to the python `setuptools` configuration. This typically takes 2 to 3 minutes. After the above build step, you can run the container with the following command:

```bash
docker run -it --rm \
  --entrypoint=sh \
  -e REGISTRATION_TOKEN=<TOKEN> \
  -e DEFAULT_API_URL=<URL> \
  tozny/e3db-python sh
```
