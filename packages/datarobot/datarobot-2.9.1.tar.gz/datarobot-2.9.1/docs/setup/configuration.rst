#############
Configuration
#############

This section describes all of the settings that can be configured in the DataRobot
configuration file. This file is by default looked for inside the user's home
directory at ``~/.config/datarobot/drconfig.yaml``, but the default location can be
overridden by specifying an environment variable ``DATAROBOT_CONFIG_FILE``, or within
the code by setting the global client with ``dr.Client(config_path='/path/to/config.yaml')``.

Configurable Variables
######################
These are the variables available for configuration for the DataRobot client:

endpoint
  This parameter is required. It is the URL of the DataRobot endpoint. For example,
  the default endpoint on the
  cloud installation of DataRobot is ``https://app.datarobot.com/api/v2``
token
  This parameter is required. It is the token of your DataRobot account. This can be
  found in the user settings page of DataRobot
connect_timeout
  This parameter is optional. It specifies the number of seconds that the
  client should be willing to wait to establish a connection to the remote server.
  Users with poor connections may need to increase this value. By default DataRobot
  uses the value ``6.05``.
ssl_verify
  This parameter is optional. It controls the SSL certificate verification of the
  DataRobot client. DataRobot is built with the
  python ``requests`` library, and this variable is used as the ``verify`` parameter in that
  library. More information can be found in their
  `documentation <http://docs.python-requests.org/en/master/user/advanced/>`_. The default
  value is ``true``, which means that ``requests`` will use your computer's set of trusted
  certificate chains by default.

Proxy support
#############
DataRobot API can work behind a non-transparent HTTP proxy server. Please set environment
variable ``HTTP_PROXY`` containing proxy URL to route all the DataRobot traffic through that
proxy server, e.g. ``HTTP_PROXY="http://my-proxy.local:3128" python my_datarobot_script.py``.
