.. _reason_codes:

============
Reason Codes
============

To compute reason codes you need to have :ref:`feature impact<feature_impact-label>` computed for a
model, and :doc:`predictions</entities/predict_job>` for an uploaded dataset computed with a
selected model.

Computing reason codes is a resource-intensive task, but you can configure it with maximum codes,
and prediction value thresholds to speed up the process.

Quick Reference
***************

.. code-block:: python

    import datarobot as dr
    # Get project
    my_projects = dr.Project.list()
    project = my_projects[0]
    # Get model
    models = project.get_models()
    model = models[0]
    # Compute feature impact
    impact_job = model.request_feature_impact()
    impact_job.wait_for_completion()
    # Upload dataset
    dataset = project.upload_dataset('./data_to_predict.csv')
    # Compute predictions
    predict_job = model.request_predictions(dataset.id)
    predict_job.wait_for_completion()
    # Initialize reason codes
    rci_job = dr.ReasonCodesInitialization.create(project.id, model.id)
    rci_job.wait_for_completion()
    # Compute reason codes with default parameters
    rc_job = dr.ReasonCodes.create(project.id, model.id, dataset.id)
    rc = rc_job.get_result_when_complete()
    # Iterate through predictions with reason codes
    for row in rc.get_rows():
        print row.prediction
        print row.reason_codes
    # download to a CSV file
    rc.download_to_csv('reason_codes.csv')

List Reason Codes
*****************
You can use the ``ReasonCodes.list()`` method to return a list of reason codes computed for
a project's models:

.. code-block:: python

    import datarobot as dr
    reason_codes = dr.ReasonCodes.list('58591727100d2b57196701b3')
    print(reason_codes)
    >>> [ReasonCodes(id=585967e7100d2b6afc93b13b,
                     project_id=58591727100d2b57196701b3,
                     model_id=585932c5100d2b7c298b8acf),
         ReasonCodes(id=58596bc2100d2b639329eae4,
                     project_id=58591727100d2b57196701b3,
                     model_id=585932c5100d2b7c298b8ac5),
         ReasonCodes(id=58763db4100d2b66759cc187,
                     project_id=58591727100d2b57196701b3,
                     model_id=585932c5100d2b7c298b8ac5),
         ...]
    rc = reason_codes[0]

    rc.project_id
    >>> u'58591727100d2b57196701b3'
    rc.model_id
    >>> u'585932c5100d2b7c298b8acf'

You can pass following parameters to filter the result:

* ``model_id`` -- str, used to filter returned reason codes by model_id.
* ``limit`` -- int, limit for number of items returned, default: no limit.
* ``offset`` -- int, number of items to skip, default: 0.

**List Reason Codes Example:**

.. code-block:: python

    dr.ReasonCodes.list('pid', model_id='model_id', limit=20, offset=100)


Initialize Reason Codes
***********************
In order to compute reason codes you have to initialize it for a particular model.

.. code-block:: python

    dr.ReasonCodesInitialization.create(project_id, model_id)

Compute Reason Codes
********************
If all prerequisites are in place, you can compute reason codes in the following way:

.. code-block:: python

    import datarobot as dr
    project_id = '5506fcd38bd88f5953219da0'
    model_id = '5506fcd98bd88f1641a720a3'
    dataset_id = '5506fcd98bd88a8142b725c8'
    rc_job = dr.ReasonCodes.create(project_id, model_id, dataset_id,
                                   max_codes=2, threshold_low=0.2, threshold_high=0.8)
    rc = rc_job.get_result_when_complete()

Where:

* ``max_codes`` are the maximum number of reason codes to compute for each row.
* ``threshold_low`` and ``threshold_high`` are thresholds for the value of the prediction of the
  row. Reason codes will be computed for a row if the row's prediction value is higher than
  ``threshold_high`` or lower than ``threshold_low``. If no thresholds are specified, reason codes
  will be computed for all rows.

Retrieving Reason Codes
***********************
You have three options for retrieving reason codes.

.. note:: ``ReasonCodes.get_all_as_dataframe()`` and ``ReasonCodes.download_to_csv()`` reformat
          reason codes to match the schema of CSV file downloaded from UI (RowId, Prediction,
          Reason 1 Strength, Reason 1 Feature, Reason 1 Value, ..., Reason N Strength,
          Reason N Feature, Reason N Value)

Get reason codes rows one by one as :class:`dr.models.reason_codes.ReasonCodesRow` objects:

.. code-block:: python

    import datarobot as dr
    project_id = '5506fcd38bd88f5953219da0'
    reason_codes_id = '5506fcd98bd88f1641a720a3'
    rc = dr.ReasonCodes.get(project_id, reason_codes_id)
    for row in rc.get_rows():
        print row.reason_codes

Get all rows as ``pandas.DataFrame``:

.. code-block:: python

    import datarobot as dr
    project_id = '5506fcd38bd88f5953219da0'
    reason_codes_id = '5506fcd98bd88f1641a720a3'
    rc = dr.ReasonCodes.get(project_id, reason_codes_id)
    reason_codes_df = rc.get_all_as_dataframe()

Download all rows to a file as CSV document:

.. code-block:: python

    import datarobot as dr
    project_id = '5506fcd38bd88f5953219da0'
    reason_codes_id = '5506fcd98bd88f1641a720a3'
    rc = dr.ReasonCodes.get(project_id, reason_codes_id)
    rc.download_to_csv('reason_codes.csv')

Adjusted Predictions In Reason Codes
************************************
In some projects such as insurance projects, the prediction adjusted by exposure is more useful
compared with raw prediction. For example, the raw prediction (e.g. claim counts) is divided by
exposure (e.g. time) in the project with exposure column. The adjusted prediction provides insights
with regard to the predicted claim counts per unit of time. To include that information, set
`exclude_adjusted_predictions` to False in correspondent method calls.

.. code-block:: python

    import datarobot as dr
    project_id = '5506fcd38bd88f5953219da0'
    reason_codes_id = '5506fcd98bd88f1641a720a3'
    rc = dr.ReasonCodes.get(project_id, reason_codes_id)
    rc.download_to_csv('reason_codes.csv', exclude_adjusted_predictions=False)
    reason_codes_df = rc.get_all_as_dataframe(exclude_adjusted_predictions=False)
