.. _predictions:

###########
Predictions
###########

Predictions generation is an asynchronous process. This means that when starting
predictions with ``Model.request_predictions`` you will receive back a PredictJob for tracking
the process responsible for fulfilling your request.

With this object you can get info about the predictions generation process before it
has finished and be rerouted to the predictions themselves when the
process is finished. For this you should use the **PredictJob**
(:doc:`API reference </api/predict_job>`) class.

Starting predictions generation
*******************************
Before actually requesting predictions, you should upload the dataset you wish to predict via
``Project.upload_dataset``.  Previously uploaded datasets can be seen under ``Project.get_datasets``.
When uploading the dataset you can provide the path to a local file, a file object, raw file content,
a ``pandas.DataFrame`` object, or the url to a publicly available dataset.


To start predicting on new data using a finished model use ``Model.request_predictions``.
It will create a new predictions generation process and return a PredictJob object tracking this process.
With it, you can monitor an existing PredictJob and retrieve generated predictions when the corresponding
PredictJob is finished.

.. code-block:: python

    import datarobot as dr

    project_id = '5506fcd38bd88f5953219da0'
    model_id = '5506fcd98bd88f1641a720a3'
    project = dr.Project.get(project_id)
    model = dr.Model.get(project=project_id,
                         model_id=model_id)

    # Using path to local file to generate predictions
    dataset_from_path = project.upload_dataset('./data_to_predict.csv')

    # Using file object to generate predictions
    with open('./data_to_predict.csv') as data_to_predict:
        dataset_from_file = project.upload_dataset(data_to_predict)

    predict_job_1 = model.request_predictions(dataset_from_path.id)
    predict_job_2 = model.request_predictions(dataset_from_file.id)


Get an existing PredictJob
**************************

To retrieve an existing PredictJob use the ``PredictJob.get`` method. This will give you
a PredictJob matching the latest status of the job if it has not completed.

If predictions have finished building, ``PredictJob.get`` will raise a ``PendingJobFinished``
exception.


.. code-block:: python

    import time

    import datarobot as dr

    predict_job = dr.PredictJob.get(project_id=project_id,
                                    predict_job_id=predict_job_id)
    predict_job.status
    >>> 'queue'

    # wait for generation of predictions (in a very inefficient way)
    time.sleep(10 * 60)
    predict_job = dr.PredictJob.get(project_id=project_id,
                                    predict_job_id=predict_job_id)
    >>> dr.errors.PendingJobFinished

    # now the predictions are finished
    predictions = dr.PredictJob.get_predictions(project_id=project.id,
                                                predict_job_id=predict_job_id)

Get generated predictions
*************************

After predictions are generated, you can use ``PredictJob.get_predictions``
to get newly generated predictions.

If predictions have not yet been finished, it will raise a ``JobNotFinished`` exception.

.. code-block:: python

    import datarobot as dr

    predictions = dr.PredictJob.get_predictions(project_id=project.id,
                                                predict_job_id=predict_job_id)

Wait for and Retrieve results
*****************************
If you just want to get generated predictions from a PredictJob, you
can use the ``PredictJob.get_result_when_complete`` function.
It will poll the status of predictions generation process until it has finished, and
then will return predictions.

.. code-block:: python

    dataset = project.get_datasets()[0]
    predict_job = model.request_predictions(dataset.id)
    predictions = predict_job.get_result_when_complete()
