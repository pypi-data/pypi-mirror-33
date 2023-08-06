.. _training_predictions:

Training Predictions
####################
The training predictions interface allows computing and retrieving out-of-sample predictions for a model
using the original project dataset. The predictions can be computed for all the rows, or restricted to validation
or holdout data. As the predictions generated will be out-of-sample, they can be expected to have different
results than if the project dataset were reuploaded as a prediction dataset.

Quick reference
***************
Training predictions generation is an asynchronous process. This means that when starting
predictions with :py:meth:`datarobot.models.Model.request_training_predictions` you will receive back a
:py:class:`datarobot.models.TrainingPredictionsJob` for tracking the process responsible for fulfilling your request.
Actual predictions may be obtained with the help of a
:py:class:`datarobot.models.training_predictions.TrainingPredictions` object returned as the result of
the training predictions job.
There are three ways to retrieve them:

1. Iterate prediction rows one by one as named tuples:

.. code-block:: python

    import datarobot as dr

    # Calculate new training predictions on all dataset
    training_predictions_job = model.request_training_predictions(dr.enums.DATA_SUBSET.ALL)
    training_predictions = training_predictions_job.get_result_when_complete()

    # Fetch rows from API and print them
    for prediction in training_predictions.iterate_rows(batch_size=250):
        print(prediction.row_id, prediction.prediction)

2. Get all prediction rows as a ``pandas.DataFrame`` object:

.. code-block:: python

    import datarobot from dr

    # Calculate new training predictions on holdout partition of dataset
    training_predictions_job = model.request_training_predictions(dr.enums.DATA_SUBSET.HOLDOUT)
    training_predictions = training_predictions_job.get_result_when_complete()

    # Fetch training predictions as data frame
    dataframe = training_predictions.get_all_as_dataframe()

3. Download all prediction rows to a file as a CSV document:

.. code-block:: python

    import datarobot from dr

    # Calculate new training predictions on all dataset
    training_predictions_job = model.request_training_predictions(dr.enums.DATA_SUBSET.ALL)
    training_predictions = training_predictions_job.get_result_when_complete()

    # Fetch training predictions and save them to file
    training_predictions.download_to_csv('my-training-predictions.csv')
