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
max_retries
  This parameter is optional.  It controls the number of retries to attempt for each connection.
  More information can be found in the
  `requests documentation <http://docs.python-requests.org/en/master/api/#requests.adapters.HTTPAdapter>`_.
  By default, errors implying the request never made it to the server are retried always and read
  timeouts (where the request began running and did not finish) are not retried.  More granular
  control by be acquired by passing a `Retry <https://urllib3.readthedocs.io/en/latest/reference/urllib3.util.html#urllib3.util.retry.Retry>`_
  object from urllib3 into a direct instantiation of ``dr.Client``.

  .. code-block:: python

     import datarobot as dr
     dr.Client(endpoint='https://app.datarobot.com/api/v2', token='this-is-a-fake-token',
               max_retries=Retry(connect=3, read=3))

Proxy support
#############
DataRobot API can work behind a non-transparent HTTP proxy server. Please set environment
variable ``HTTP_PROXY`` containing proxy URL to route all the DataRobot traffic through that
proxy server, e.g. ``HTTP_PROXY="http://my-proxy.local:3128" python my_datarobot_script.py``.
