.. _model_deployment:

################
Model Deployment
################

Model deployments are records that we create when user deploys a model to dedicated prediction
cluster.

.. warning::
    Model Deployments feature is in beta state and requires additional configuration for proper usage.
    Please contact Support/CFDS for help with setup and usage of model deployment functionality.

.. warning::
    Users can still predict using models which have NOT been deployed. Deployment, in the current state
    of the system, only means making database records which we then associate monitoring data with.
    In other words, users can’t access monitoring info for predictions using models without an
    associated model deployment record.

Creating Model Deployment
*************************

To create new ``ModelDeployment`` we need to have a ``project_id`` and ``model_id`` we want to deploy.
If we are going to create ``ModelDeployment`` of ``Model`` that is deployed to `instance` we need
``instance_id`` of this `instance`.
For creation of new ``ModelDeployment`` we will use ``ModelDeployment.create``. For new ``ModelDeployment``
we will need to set some readable ``label``. It can also have custom ``description`` and ``status``.

.. code-block:: python

    import datarobot as dr

    project_id = '5506fcd38bd88f5953219da0'
    model_id = '5506fcd98bd88f1641a720a3'
    instance_id = '5a8d4bf9962d7415f7cce05a'
    label = 'New Model Deployment'

    model_deployment = dr.ModelDeployment.create(label=label, model_id=model_id,
                                                 project_id=project_id, instance_id=instance_id)

    print(model_deployment.id)
    >>> '5a8eabe8962d743607c5009'


Get list of Model Deployments
*****************************

To retrieve list of all ``ModelDeployment`` items we use ``ModelDeployment.list``.
List could be queried using ``query`` parameter, ordered by ``order_by`` and filtered by ``status`` parameters.
Also we can slice results using ``limit`` and ``offset`` parameters.

.. code-block:: python

    import datarobot as dr

    model_deployments = dr.ModelDeployment.list()
    print(model_deployments)
    >>> [<datarobot.models.model_deployment.ModelDeployment object at 0x7efebf513c10>,
    <datarobot.models.model_deployment.ModelDeployment object at 0x7efebf513a50>,
    <datarobot.models.model_deployment.ModelDeployment object at 0x7efebf513ad0>]


Get single ModelDeployment
**************************

To get ``ModelDeployment`` instance we use ``ModelDeployment.get`` with ``model_deployment_id`` as an argument.

.. code-block:: python

    import datarobot as dr

    model_deployment_id = '5a8eabe8962d743607c5009'

    model_deployment = dr.ModelDeployment.get(model_deployment_id)

    print(model_deployment.service_health_messages)
    >>> [{'message': 'No successful predictions in 24 hours', 'msg_id': 'NO_GOOD_REQUESTS', :level': 'passing'}]


When we have an instance of ``ModelDeployment`` we can update its ``label``, ``description`` or ``status``.
You can chose ``status`` value from ``datarobot.enums.MODEL_DEPLOYMENT_STATUS``

.. code-block:: python

    from datarobot.enums import MODEL_DEPLOYMENT_STATUS

    model_deployment.update(label='Old deployment', description='Deactivated model deployment',
                            status=MODEL_DEPLOYMENT_STATUS.ARCHIVED)


We can also get service health of ``ModelDeployment`` instance using ``get_service_statistics`` method.
It accepts ``start_data`` and ``end_date`` as  optional parameters for setting period of statistics

.. code-block:: python

    model_deployment.get_service_statistics(start_date='2017-01-01')
    >>> {'consumers': 0,
         'load': {'median': 0.0, 'peak': 0.0},
         'period': {'end': datetime.datetime(2018, 2, 22, 12, 5, 40, 764294, tzinfo=tzutc()),
         'start': datetime.datetime(2017, 1, 1, 0, 0, tzinfo=tzutc())},
         'server_error_rate': {'current': 0.0, 'previous': 0.0},
         'total_requests': 0,
         'user_error_rate': {'current': 0.0, 'previous': 0.0}}


History of ``ModelDeployment`` instance is available via ``action_log`` method


.. code-block:: python

    model_deployment.action_log()
    >>> [{'action': 'created',
          'performed_at': datetime.datetime(2018, 2, 21, 12, 4, 5, 804305),
          'performed_by': {'id': '5a86c0e0e7c354c960cd0540',
           'username': 'user@datarobot.com'}},
         {'action': 'deployed',
          'performed_at': datetime.datetime(2018, 2, 22, 11, 39, 20, 34000),
          'performed_by': {'id': '5a86c0e0e7c354c960cd0540',
           'username': 'user@datarobot.com'}}]

