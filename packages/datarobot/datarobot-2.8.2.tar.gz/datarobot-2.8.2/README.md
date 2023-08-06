# DataRobot Python Client

datarobot is a Python library for working with the
[DataRobot](!http://datarobot.com) platform API.

This README is primarily intended for those developing the client. There is
also documentation intended for users of the client contained in the `docs`
directory of this repository.


## Getting Started
You need to have

    - Git
    - Python (2.7, 3.4+)
    - DataRobot account
    - pip

For building the documentation, you'll also need:

    - LaTeX
    - Pandoc (via `apt-get`, `brew`, etc.)

We recommend using a virtualenv to keep dependencies from conflicting with
projects you may have on your machine.

## Installation
```console
git clone git@github.com:datarobot/public_api_client.git
cd public_api_client
pip install -e .[dev]
```
Note: This may have to be run as `root` or with `--user` flag if you are not
using python virtual environment.

## Installation of pyOpenSSL
On versions of Python earlier than 2.7.9 you might have 
[InsecurePlatformWarning](https://urllib3.readthedocs.org/en/latest/security.html#insecureplatformwarning)
in your output.
To prevent this without updating your Python version you should install 
[pyOpenSSL](https://urllib3.readthedocs.org/en/latest/security.html#pyopenssl) package:

```console
pip install pyopenssl ndg-httpsclient pyasn1
```

## Build the documentation
DataRobot has extensive documentation, which you can build locally for your
own reference, like this:

```console
cd docs
make clean html
```

The documentation will then be built in a subdirectory, and can be viewed with
your web browser.

Alternatively, see https://datarobot.atlassian.net/wiki/display/APIS/Release+Tracker
for pre-built documentation for the curent cloud release and all enterprise
releases, as well as guidance on which version of the API goes with which
enterprise release.

To build a PDF of the docs for release:

```console
cd docs
make clean xelatexpdf
```


## Topics
 * Setup topics:
    * [Common DataRobot Client setup](#datarobot-client-setup)
        * [Setup with cfg file](#setup-with-cfg-file)
        * [Setup explicitly in code](#setup-explicitly-in-code)
        * [Setup with environment variables](#setup-with-environment-variables)
 * Building the documentation
 * Development:
    * [Setup datarobot sdk locally](#setup-locally)
    * [Running tests](#running-tests)

### DataRobot Client Setup
There are three different ways to set up the client to authenticate with the
server: through a config file, through environment variables, or explicitly in
the code.

You must specify an endpoint and an API token.  You can manage your API tokens in the DataRobot
webapp, in your profile.  If you access the DataRobot webapp at `https://app.datarobot.com`, then
the correct endpoint to specify would be `https://app.datarobot.com/api/v2`.

#### Setup with cfg file
The client will look for a config file `~/.config/datarobot/drconfig.yaml` by default. You can also
change that default to look for a config file at a different
path by using the using environment variable `DATAROBOT_CONFIG_FILE`.  Note that if you specify a
filepath it should be an absolute path so that the API client will work when run from any location.

This is an example of what that config file should look like.
```file
token: your_token
endpoint: https://app.datarobot.com/api/v2
```

#### Setup explicitly in code

Explicitly set up in code using your token:
```python
import datarobot as dr
dr.Client(token='your_token', endpoint='https://app.datarobot.com/api/v2')
```

You can also specify the location of a YAML config file to use:
```python
import datarobot as dr
dr.Client(config_path='/home/user/my_datarobot_config.yaml')
```

#### Setup with environment variables
Setup endpoint from environment variables in UNIX shell:
```shell
export DATAROBOT_API_TOKEN='MY_TOKEN'
export DATAROBOT_ENDPOINT='https://app.datarobot.com/api/v2'
```

## Running tests
This will run all tests on both Python 2 and 3 using [tox](https://testrun.org/tox/):
```console
make test
```
If you don't have Python 3 installed, you can use docker to run Python 3.4 tests:
```console
make test-docker-py3
```
You can also use [green](https://github.com/CleanCut/green) test runner to check all tests
on your default Python version:
```console
make test-green
```
