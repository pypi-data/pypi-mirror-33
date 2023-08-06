#########
Changelog
#########

2.9.1
=====

Bugfixes
********
- Fixed release metadata.

2.9.0
=====

New Features
************
- New ``ModelDeployment`` class can be used to track status and health of models deployed for
  predictions.

Enhancements
************
- DataRobot API now supports creating 3 new blender types - Random Forest, TensorFlow, LightGBM.
- Multiclass projects now support blenders creation for 3 new blender types as well as Average
  and ENET blenders.
- Models can be trained by requesting a particular row count using the new ``training_row_count``
  argument with `Project.train`, `Model.train` and `Model.request_frozen_model` in non-datetime
  partitioned projects, as an alternative to the previous option of specifying a desired
  percentage of the project dataset. Specifying model size by row count is recommended when
  the float precision of ``sample_pct`` could be problematic, e.g. when training on a small
  percentage of the dataset or when training up to partition boundaries.
- New attributes ``max_train_rows``, ``scaleout_max_train_pct``, and ``scaleout_max_train_rows``
  have been added to :py:class:`datarobot.Project`. ``max_train_rows`` specified the equivalent
  value to the existing ``max_train_pct`` as a row count. The scaleout fields can be used to see how
  far scaleout models can be trained on projects, which for projects taking advantage of scalable
  ingest may exceed the limits on the data available to non-scaleout blueprints.
- Individual features can now be marked as a priori or not a priori using the new `feature_settings`
  attribute when setting the target or specifying datetime partitioning settings on time
  series projects. Any features not specified in the `feature_settings` parameter will be
  assigned according to the `default_to_a_priori` value.
- Three new options have been made availabe in the
  :py:class:`datarobotDatetimePartitioningSpecification` class to fine-tune how time-series projects
  derive modeling features.  `treat_as_exponential` can control whether data is analyzed as
  an exponential trend and transformations like log-transform are applied.
  `differencing_method` can control which differencing method to use for stationary data.
  `periodicities` can be used to specify periodicities occuring within the data.
  All are optional and defaults will be chosen automatically if they are unspecified.

API Changes
***********
- Now ``training_row_count`` is available on non-datetime models as well as "rowCount" based
  datetime models. It reports the number of rows used to train the model (equivalent to
  ``sample_pct``).

2.8.1
=====

Bugfixes
********
- The documented default connect_timeout will now be correctly set for all configuration mechanisms,
  so that requests that fail to reach the DataRobot server in a reasonable amount of time will now
  error instead of hanging indefinitely. If you observe that you have started seeing
  ``ConnectTimeout`` errors, please configure your connect_timeout to a larger value.
- Version of ``trafaret`` library this package depends on is now pinned to ``trafaret>=0.7,<1.1``
  since versions outside that range are known to be incompatible.


2.8.0
=====

New Features
************
- The DataRobot API supports the creation, training, and predicting of multiclass classification
  projects. DataRobot, by default, handles a dataset with a numeric target column as regression.
  If your data has a numeric cardinality of fewer than 11 classes, you can override this behavior to
  instead create a multiclass classification project from the data. To do so, use the set_target
  function, setting target_type='Multiclass'. If DataRobot recognizes your data as categorical, and
  it has fewer than 11 classes, using multiclass will create a project that classifies which label
  the data belongs to.
- The DataRobot API now includes Rating Tables. A rating table is an exportable csv representation
  of a model. Users can influence predictions by modifying them and creating a new model with the
  modified table. See the :ref:`documentation<rating_table>` for more information on how to use
  rating tables.
- `scaleout_modeling_mode` has been added to the `AdvancedOptions` class
  used when setting a project target. It can be used to control whether
  scaleout models appear in the autopilot and/or available blueprints.
  Scaleout models are only supported in the Hadoop enviroment with
  the corresponding user permission set.
- The `Feature` object now returns the EDA summary statistics (i.e., mean, median, minum, maximum,
  and standard deviation) for features where this is available (e.g., numeric, date, time,
  currency, and length features). These summary statistics will be formatted in the same format
  as the data it summarizes.
- The DataRobot API now supports Training Predictions workflow. Training predictions are made by a
  model for a subset of data from original dataset. User can start a job which will make those
  predictions and retrieve them. See the :ref:`documentation<training_predictions>`
  for more information on how to use training predictions.
- DataRobot now supports retrieving a :ref:`model blueprint chart<model_blueprint_chart>` and a
  :ref:`model blueprint docs<model_blueprint_doc>`.
- With the introduction of Multiclass Classification projects, DataRobot needed a better way to
  explain the performance of a multiclass model so we created a new Confusion Chart. The API
  now supports retrieving and interacting with confusion charts.

Enhancements
************
- `DatetimePartitioningSpecification` now includes the optional `disable_holdout` flag that can
  be used to disable the holdout fold when creating a project with datetime partitioning.
- When retrieving reason codes on a project using an exposure column, predictions that are adjusted
  for exposure can be retrieved.
- File URIs can now be used as sourcedata when creating a project or uploading a prediction dataset.
  The file URI must refer to an allowed location on the server, which is configured as described in
  the user guide documentation.
- The advanced options available when setting the target have been extended to include the new
  parameter 'events_count' as a part of the AdvancedOptions object to allow specifying the
  events count column. See the user guide documentation in the webapp for more information
  on events count.
- PredictJob.get_predictions now returns predicted probability for each class in the dataframe.
- PredictJob.get_predictions now accepts prefix parameter to prefix the classes name returned in the
  predictions dataframe.

API Changes
***********
- Add `target_type` parameter to set_target() and start(), used to override the project default.

2.7.2
=====

Documentation Changes
*********************

- Updated link to the publicly hosted documentation.

2.7.1
=====

Documentation Changes
*********************

- Online documentation hosting has migrated from PythonHosted to Read The Docs. Minor code changes
  have been made to support this.

2.7.0
=====

New Features
************
- Lift chart data for models can be retrieved using the `Model.get_lift_chart` and
  `Model.get_all_lift_charts` methods.
- ROC curve data for models in classification projects can be retrieved using the
  `Model.get_roc_curve` and `Model.get_all_roc_curves` methods.
- Semi-automatic autopilot mode is removed.
- Word cloud data for text processing models can be retrieved using `Model.get_word_cloud` method.
- Scoring code JAR file can be downloaded for models supporting code generation.

Enhancements
************
- A `__repr__` method has been added to the `PredictionDataset` class to improve readability when
  using the client interactively.
- `Model.get_parameters` now includes an additional key in the derived features it includes,
  showing the coefficients for individual stages of multistage models (e.g. Frequency-Severity
  models).
- When training a `DatetimeModel` on a window of data, a `time_window_sample_pct` can be specified
  to take a uniform random sample of the training data instead of using all data within the window.
- Installing of DataRobot package now has an "Extra Requirements" section that will install all of
  the dependencies needed to run the example notebooks.

Documentation Changes
*********************
- A new example notebook describing how to visualize some of the newly available model insights
  including lift charts, ROC curves, and word clouds has been added to the examples section.
- A new section for `Common Issues` has been added to `Getting Started` to help debug issues related to client installation and usage.


2.6.1
=====

Bugfixes
********

- Fixed a bug with `Model.get_parameters` raising an exception on some valid parameter values.

Documentation Changes
*********************

- Fixed sorting order in Feature Impact example code snippet.

2.6.0
=====

New Features
************
- A new partitioning method (datetime partitioning) has been added. The recommended workflow is to
  preview the partitioning by creating a `DatetimePartitioningSpecification` and passing it into
  `DatetimePartitioning.generate`, inspect the results and adjust as needed for the specific project
  dataset by adjusting the `DatetimePartitioningSpecification` and re-generating, and then set the
  target by passing the final `DatetimePartitioningSpecification` object to the partitioning_method
  parameter of `Project.set_target`.
- When interacting with datetime partitioned projects, `DatetimeModel` can be used to access more
  information specific to models in datetime partitioned projects. See
  :ref:`the documentation<datetime_modeling_workflow>` for more information on differences in the
  modeling workflow for datetime partitioned projects.
- The advanced options available when setting the target have been extended to include the new
  parameters 'offset' and 'exposure' (part of the AdvancedOptions object) to allow specifying
  offset and exposure columns to apply to predictions generated by models within the project.
  See the user guide documentation in the webapp for more information on offset
  and exposure columns.
- Blueprints can now be retrieved directly by project_id and blueprint_id via `Blueprint.get`.
- Blueprint charts can now be retrieved directly by project_id and blueprint_id via
  `BlueprintChart.get`. If you already have an instance of `Blueprint` you can retrieve its
  chart using `Blueprint.get_chart`.
- Model parameters can now be retrieved using `ModelParameters.get`. If you already have an
  instance of `Model` you can retrieve its parameters using `Model.get_parameters`.
- Blueprint documentation can now be retrieved using `Blueprint.get_documents`. It will contain
  information about the task, its parameters and (when available) links and references to
  additional sources.
- The DataRobot API now includes Reason Codes. You can now compute reason codes for prediction
  datasets. You are able to specify thresholds on which rows to compute reason codes for to speed
  up computation by skipping rows based on the predictions they generate. See the reason codes
  :ref:`documentation<reason_codes>` for more information.

Enhancements
************

- A new parameter has been added to the `AdvancedOptions` used with `Project.set_target`. By
  specifying `accuracyOptimizedMb=True` when creating `AdvancedOptions`, longer-running models
  that may have a high accuracy will be included in the autopilot and made available to run
  manually.
- A new option for `Project.create_type_transform_feature` has been added which explicitly
  truncates data when casting numerical data as categorical data.
- Added 2 new blenders for projects that use MAD or Weighted MAD as a metric. The MAE blender uses
  BFGS optimization to find linear weights for the blender that minimize mean absolute error
  (compared to the GLM blender, which finds linear weights that minimize RMSE), and the MAEL1
  blender uses BFGS optimization to find linear weights that minimize MAE + a L1 penalty on the
  coefficients (compared to the ENET blender, which minimizes RMSE + a combination of the L1 and L2
  penalty on the coefficients).

Bugfixes
********

- Fixed a bug (affecting Python 2 only) with printing any model (including frozen and prime models)
  whose model_type is not ascii.
- FrozenModels were unable to correctly use methods inherited from Model. This has been fixed.
- When calling `get_result` for a Job, ModelJob, or PredictJob that has errored, `AsyncProcessUnsuccessfulError` will now be raised instead of `JobNotFinished`, consistently with the behaviour of `get_result_when_complete`.

Deprecation Summary
*******************

- Support for the experimental Recommender Problems projects has been removed. Any code relying on
  `RecommenderSettings` or the `recommender_settings` argument of `Project.set_target` and
  `Project.start` will error.
- ``Project.update``, deprecated in v2.2.32, has been removed in favor of specific updates:
  ``rename``, ``unlock_holdout``, ``set_worker_count``.

Documentation Changes
*********************

- The link to Configuration from the Quickstart page has been fixed.

2.5.1
=====

Bugfixes
********

- Fixed a bug (affecting Python 2 only) with printing blueprints  whose names are
  not ascii.
- Fixed an issue where the weights column (for weighted projects) did not appear
  in the `advanced_options` of a `Project`.


2.5.0
=====

New Features
************

- Methods to work with blender models have been added. Use `Project.blend` method to create new blenders,
  `Project.get_blenders` to get the list of existing blenders and `BlenderModel.get` to retrieve a model
  with blender-specific information.
- Projects created via the API can now use smart downsampling when setting the target by passing
  `smart_downsampled` and `majority_downsampling_rate` into the `AdvancedOptions` object used with
  `Project.set_target`. The smart sampling options used with an existing project will be available
  as part of `Project.advanced_options`.
- Support for frozen models, which use tuning parameters from a parent model for more efficient
  training, has been added. Use `Model.request_frozen_model` to create a new frozen model,
  `Project.get_frozen_models` to get the list of existing frozen models and `FrozenModel.get` to
  retrieve a particular frozen model.

Enhancements
************

- The inferred date format (e.g. "%Y-%m-%d %H:%M:%S") is now included in the Feature object. For
  non-date features, it will be None.
- When specifying the API endpoint in the configuration, the client will now behave correctly for
  endpoints with and without trailing slashes.


2.4.0
=====

New Features
************

- The premium feature `DataRobot Prime` has been added. You can now approximate a model
  on the leaderboard and download executable code for it. See documentation for further details, or
  talk to your account representative if the feature is not available on your account.
- (Only relevant for on-premise users with a Standalone Scoring cluster.) Methods
  (`request_transferable_export` and `download_export`) have been added to the `Model` class for exporting models (which will only work if model export is turned on). There is a new class `ImportedModel` for managing imported models on a Standalone
  Scoring cluster.
- It is now possible to create projects from a WebHDFS, PostgreSQL, Oracle or MySQL data source. For more information see the
  documentation for the relevant `Project` classmethods: `create_from_hdfs`, `create_from_postgresql`,
  `create_from_oracle` and `create_from_mysql`.
- `Job.wait_for_completion`, which waits for a job to complete without returning anything, has been added.

Enhancements
************

- The client will now check the API version offered by the server specified in configuration, and
  give a warning if the client version is newer than the server version. The DataRobot server is
  always backwards compatible with old clients, but new clients may have functionality that is
  not implemented on older server versions. This issue mainly affects users with on-premise deployments
  of DataRobot.

Bugfixes
********

- Fixed an issue where `Model.request_predictions` might raise an error when predictions finished
  very quickly instead of returning the job.

API Changes
***********

- To set the target with quickrun autopilot, call `Project.set_target` with `mode=AUTOPILOT_MODE.QUICK` instead of
  specifying `quickrun=True`.

Deprecation Summary
*******************

- Semi-automatic mode for autopilot has been deprecated and will be removed in 3.0.
  Use manual or fully automatic instead.
- Use of the `quickrun` argument in `Project.set_target` has been deprecated and will be removed in
  3.0. Use `mode=AUTOPILOT_MODE.QUICK` instead.

Configuration Changes
*********************

- It is now possible to control the SSL certificate verification by setting the parameter
  `ssl_verify` in the config file.

Documentation Changes
*********************

- The "Modeling Airline Delay" example notebook has been updated to work with the new 2.3
  enhancements.
- Documentation for the generic `Job` class has been added.
- Class attributes are now documented in the `API Reference` section of the documentation.
- The changelog now appears in the documentation.
- There is a new section dedicated to configuration, which lists all of the configuration
  options and their meanings.


2.3.0
=====

New Features
************

- The DataRobot API now includes Feature Impact, an approach to measuring the relevance of each feature
  that can be applied to any model. The `Model` class now includes methods `request_feature_impact`
  (which creates and returns a feature impact job) and `get_feature_impact` (which can retrieve completed feature impact results).
- A new improved workflow for predictions now supports first uploading a dataset via `Project.upload_dataset`,
  then requesting predictions via `Model.request_predictions`. This allows us to better support predictions on
  larger datasets and non-ascii files.
- Datasets previously uploaded for predictions (represented by the `PredictionDataset` class) can be listed from
  `Project.get_datasets` and retrieve and deleted via `PredictionDataset.get` and `PredictionDataset.delete`.
- You can now create a new feature by re-interpreting the type of an existing feature in a project by
  using the `Project.create_type_transform_feature` method.
- The `Job` class now includes a `get` method for retrieving a job and a `cancel` method for
  canceling a job.
- All of the jobs classes (`Job`, `ModelJob`, `PredictJob`) now include the following new methods:
  `refresh` (for refreshing the data in the job object), `get_result` (for getting the
  completed resource resulting from the job), and `get_result_when_complete` (which waits until the job
  is complete and returns the results, or times out).
- A new method `Project.refresh` can be used to update
  `Project` objects with the latest state from the server.
- A new function `datarobot.async.wait_for_async_resolution` can be
  used to poll for the resolution of any generic asynchronous operation
  on the server.


Enhancements
************

- The `JOB_TYPE` enum now includes `FEATURE_IMPACT`.
- The `QUEUE_STATUS` enum now includes `ABORTED` and `COMPLETED`.
- The `Project.create` method now has a `read_timeout` parameter which can be used to
  keep open the connection to DataRobot while an uploaded file is being processed.
  For very large files this time can be substantial. Appropriately raising this value
  can help avoid timeouts when uploading large files.
- The method `Project.wait_for_autopilot` has been enhanced to error if
  the project enters a state where autopilot may not finish. This avoids
  a situation that existed previously where users could wait
  indefinitely on their project that was not going to finish. However,
  users are still responsible to make sure a project has more than
  zero workers, and that the queue is not paused.
- Feature.get now supports retrieving features by feature name. (For backwards compatibility,
  feature IDs are still supported until 3.0.)
- File paths that have unicode directory names can now be used for
  creating projects and PredictJobs. The filename itself must still
  be ascii, but containing directory names can have other encodings.
- Now raises more specific JobAlreadyRequested exception when we refuse a model fitting request as a duplicate.
  Users can explicitly catch this exception if they want it to be ignored.
- A `file_name` attribute has been added to the `Project` class, identifying the file name
  associated with the original project dataset. Note that if the project was created from
  a data frame, the file name may not be helpful.
- The connect timeout for establishing a connection to the server can now be set directly. This can be done in the
  yaml configuration of the client, or directly in the code. The default timeout has been lowered from 60 seconds
  to 6 seconds, which will make detecting a bad connection happen much quicker.

Bugfixes
********

- Fixed a bug (affecting Python 2 only) with printing features and featurelists whose names are
  not ascii.

API Changes
***********

- Job class hierarchy is rearranged to better express the relationship between these objects. See
  documentation for `datarobot.models.job` for details.
- `Featurelist` objects now have a `project_id` attribute to indicate which project they belong
  to. Directly accessing the `project` attribute of a `Featurelist` object is now deprecated
- Support INI-style configuration, which was deprecated in v2.1, has been removed. yaml is the only supported
  configuration format.
- The method `Project.get_jobs` method, which was deprecated in v2.1, has been removed. Users should use
  the `Project.get_model_jobs` method instead to get the list of model jobs.

Deprecation Summary
*******************

- `PredictJob.create` has been deprecated in favor of the alternate workflow using `Model.request_predictions`.
- Feature.converter (used internally for object construction) has been made private.
- Model.fetch_resource_data has been deprecated and will be removed in 3.0. To fetch a model from
   its ID, use Model.get.
- The ability to use Feature.get with feature IDs (rather than names) is deprecated and will
  be removed in 3.0.
- Instantiating a `Project`, `Model`, `Blueprint`, `Featurelist`, or `Feature` instance from a `dict`
  of data is now deprecated. Please use the `from_data` classmethod of these classes instead. Additionally,
  instantiating a `Model` from a tuple or by using the keyword argument `data` is also deprecated.
- Use of the attribute `Featurelist.project` is now deprecated. You can use the `project_id`
  attribute of a `Featurelist` to instantiate a `Project` instance using `Project.get`.
- Use of the attributes `Model.project`, `Model.blueprint`, and `Model.featurelist` are all deprecated now
  to avoid use of partially instantiated objects. Please use the ids of these objects instead.
- Using a `Project` instance as an argument in `Featurelist.get` is now deprecated.
  Please use a project_id instead. Similarly, using a `Project` instance in `Model.get` is also deprecated,
  and a project_id should be used in its place.

Configuration Changes
*********************

- Previously it was possible (though unintended) that the client configuration could be mixed through
  environment variables, configuration files, and arguments to `datarobot.Client`. This logic is now
  simpler - please see the `Getting Started` section of the documentation for more information.


2.2.33
======

Bugfixes
********

- Fixed a bug with non-ascii project names using the package with Python 2.
- Fixed an error that occurred when printing projects that had been constructed from an ID only or
  printing printing models that had been constructed from a tuple (which impacted printing PredictJobs).
- Fixed a bug with project creation from non-ascii file names. Project creation from non-ascii file names
  is not supported, so this now raises a more informative exception. The project name is no longer used as
  the file name in cases where we do not have a file name, which prevents non-ascii project names from
  causing problems in those circumstances.
- Fixed a bug (affecting Python 2 only) with printing projects, features, and featurelists whose names are
  not ascii.


2.2.32
======

New Features
************

- ``Project.get_features`` and ``Feature.get`` methods have been added for feature retrieval.
- A generic ``Job`` entity has been added for use in retrieving the entire queue at once. Calling
  ``Project.get_all_jobs`` will retrieve all (appropriately filtered) jobs from the queue. Those
  can be cancelled directly as generic jobs, or transformed into instances of the specific
  job class using ``ModelJob.from_job`` and ``PredictJob.from_job``, which allow all functionality
  previously available via the ModelJob and PredictJob interfaces.
- ``Model.train`` now supports ``featurelist_id`` and ``scoring_type`` parameters, similar to
  ``Project.train``.

Enhancements
************

- Deprecation warning filters have been updated. By default, a filter will be added ensuring that
  usage of deprecated features will display a warning once per new usage location. In order to
  hide deprecation warnings, a filter like
  `warnings.filterwarnings('ignore', category=DataRobotDeprecationWarning)`
  can be added to a script so no such warnings are shown. Watching for deprecation warnings
  to avoid reliance on deprecated features is recommended.
- If your client is misconfigured and does not specify an endpoint, the cloud production server is
  no longer used as the default as in many cases this is not the correct default.
- This changelog is now included in the distributable of the client.

Bugfixes
********

- Fixed an issue where updating the global client would not affect existing objects with cached clients.
  Now the global client is used for every API call.
- An issue where mistyping a filepath for use in a file upload has been resolved. Now an error will be
  raised if it looks like the raw string content for modeling or predictions is just one single line.

API Changes
***********

- Use of username and password to authenticate is no longer supported - use an API token instead.
- Usage of ``start_time`` and ``finish_time`` parameters in ``Project.get_models`` is not
  supported both in filtering and ordering of models
- Default value of ``sample_pct`` parameter of ``Model.train`` method is now ``None`` instead of ``100``.
  If the default value is used, models will be trained with all of the available *training* data based on
  project configuration, rather than with entire dataset including holdout for the previous default value
  of ``100``.
- ``order_by`` parameter of ``Project.list`` which was deprecated in v2.0 has been removed.
- ``recommendation_settings`` parameter of ``Project.start`` which was deprecated in v0.2 has been removed.
- ``Project.status`` method which was deprecated in v0.2 has been removed.
- ``Project.wait_for_aim_stage`` method which was deprecated in v0.2 has been removed.
- ``Delay``, ``ConstantDelay``, ``NoDelay``, ``ExponentialBackoffDelay``, ``RetryManager``
  classes from ``retry`` module which were deprecated in v2.1 were removed.
- Package renamed to ``datarobot``.

Deprecation Summary
*******************

- ``Project.update`` deprecated in favor of specific updates:
  ``rename``, ``unlock_holdout``, ``set_worker_count``.

Documentation Changes
*********************

- A new use case involving financial data has been added to the ``examples`` directory.
- Added documentation for the partition methods.

2.1.31
======

Bugfixes
********

- In Python 2, using a unicode token to instantiate the client will
  now work correctly.


2.1.30
======

Bugfixes
********

- The minimum required version of ``trafaret`` has been upgraded to 0.7.1
  to get around an incompatibility between it and ``setuptools``.


2.1.29
======

Enhancements
************

- Minimal used version of ``requests_toolbelt`` package changed from 0.4 to 0.6


2.1.28
======

New Features
************

- Default to reading YAML config file from `~/.config/datarobot/drconfig.yaml`
- Allow `config_path` argument to client
- ``wait_for_autopilot`` method added to Project. This method can be used to
  block execution until autopilot has finished running on the project.
- Support for specifying which featurelist to use with initial autopilot in
  ``Project.set_target``
- ``Project.get_predict_jobs`` method has been added, which looks up all prediction jobs for a
  project
- ``Project.start_autopilot`` method has been added, which starts autopilot on
  specified featurelist
- The schema for ``PredictJob`` in DataRobot API v2.1 now includes a ``message``. This attribute has
  been added to the PredictJob class.
- ``PredictJob.cancel`` now exists to cancel prediction jobs, mirroring ``ModelJob.cancel``
- ``Project.from_async`` is a new classmethod that can be used to wait for an async resolution
  in project creation. Most users will not need to know about it as it is used behind the scenes
  in ``Project.create`` and ``Project.set_target``, but power users who may run
  into periodic connection errors will be able to catch the new ProjectAsyncFailureError
  and decide if they would like to resume waiting for async process to resolve

Enhancements
************

- ``AUTOPILOT_MODE`` enum now uses string names for autopilot modes instead of numbers

Deprecation Summary
*******************

- ``ConstantDelay``, ``NoDelay``, ``ExponentialBackoffDelay``, and ``RetryManager`` utils are now deprecated
- INI-style config files are now deprecated (in favor of YAML config files)
- Several functions in the `utils` submodule are now deprecated (they are
  being moved elsewhere and are not considered part of the public interface)
- ``Project.get_jobs`` has been renamed ``Project.get_model_jobs`` for clarity and deprecated
- Support for the experimental date partitioning has been removed in DataRobot API,
  so it is being removed from the client immediately.

API Changes
***********

- In several places where ``AppPlatformError`` was being raised, now ``TypeError``, ``ValueError`` or
  ``InputNotUnderstoodError`` are now used. With this change, one can now safely assume that when
  catching an ``AppPlatformError`` it is because of an unexpected response from the server.
- ``AppPlatformError`` has gained a two new attributes, ``status_code`` which is the HTTP status code
  of the unexpected response from the server, and ``error_code`` which is a DataRobot-defined error
  code. ``error_code`` is not used by any routes in DataRobot API 2.1, but will be in the future.
  In cases where it is not provided, the instance of ``AppPlatformError`` will have the attribute
  ``error_code`` set to ``None``.
- Two new subclasses of ``AppPlatformError`` have been introduced, ``ClientError`` (for 400-level
  response status codes) and ``ServerError`` (for 500-level response status codes). These will make
  it easier to build automated tooling that can recover from periodic connection issues while polling.
- If a ``ClientError`` or ``ServerError`` occurs during a call to ``Project.from_async``, then a
  ``ProjectAsyncFailureError`` (a subclass of AsyncFailureError) will be raised. That exception will
  have the status_code of the unexpected response from the server, and the location that was being
  polled to wait for the asynchronous process to resolve.


2.0.27
======

New Features
************

- ``PredictJob`` class was added to work with prediction jobs
- ``wait_for_async_predictions`` function added to `predict_job` module

Deprecation Summary
*******************

- The `order_by` parameter of the ``Project.list`` is now deprecated.


0.2.26
======

Enhancements
************

- ``Projet.set_target`` will re-fetch the project data after it succeeds,
  keeping the client side in sync with the state of the project on the
  server
- ``Project.create_featurelist`` now throws ``DuplicateFeaturesError``
  exception if passed list of features contains duplicates
- ``Project.get_models`` now supports snake_case arguments to its
  order_by keyword

Deprecation Summary
*******************

- ``Project.wait_for_aim_stage`` is now deprecated, as the REST Async
  flow is a more reliable method of determining that project creation has
  completed successfully
- ``Project.status`` is deprecated in favor of ``Project.get_status``
- ``recommendation_settings`` parameter of ``Project.start`` is
  deprecated in favor of ``recommender_settings``

Bugfixes
********

- ``Project.wait_for_aim_stage`` changed to support Python 3
- Fixed incorrect value of ``SCORING_TYPE.cross_validation``
- Models returned by ``Project.get_models`` will now be correctly
  ordered when the order_by keyword is used


0.2.25
======

- Pinned versions of required libraries

0.2.24
======

Official release of v0.2

0.1.24
======

- Updated documentation
- Renamed parameter `name` of `Project.create` and `Project.start` to `project_name`
- Removed `Model.predict` method
- `wait_for_async_model_creation` function added to `modeljob` module
- `wait_for_async_status_service` of `Project` class renamed to `_wait_for_async_status_service`
- Can now use auth_token in config file to configure SDK


0.1.23
======

- Fixes a method that pointed to a removed route


0.1.22
======

- Added `featurelist_id` attribute to `ModelJob` class


0.1.21
======

- Removes `model` attribute from `ModelJob` class


0.1.20
======

- Project creation raises `AsyncProjectCreationError` if it was unsuccessful
- Removed `Model.list_prime_rulesets` and `Model.get_prime_ruleset` methods
- Removed `Model.predict_batch` method
- Removed `Project.create_prime_model` method
- Removed `PrimeRuleSet` model
- Adds backwards compatibility bridge for ModelJob async
- Adds ModelJob.get and ModelJob.get_model


0.1.19
======

- Minor bugfixes in `wait_for_async_status_service`


0.1.18
======

- Removes `submit_model` from Project until serverside implementation is improved
- Switches training URLs for new resource-based route at /projects/<project_id>/models/
- Job renamed to ModelJob, and using modelJobs route
- Fixes an inconsistency in argument order for `train` methods


0.1.17
======

- `wait_for_async_status_service` timeout increased from 60s to 600s


0.1.16
======

- `Project.create` will now handle both async/sync project creation


0.1.15
======

- All routes pluralized to sync with changes in API
- `Project.get_jobs` will request all jobs when no param specified
- dataframes from `predict` method will have pythonic names
- `Project.get_status` created, `Project.status` now deprecated
- `Project.unlock_holdout` created.
- Added `quickrun` parameter to `Project.set_target`
- Added `modelCategory` to Model schema
- Add `permalinks` featrue to Project and Model objects.
- `Project.create_prime_model` created


0.1.14
======

- `Project.set_worker_count` fix for compatibility with API change in project update.


0.1.13
======

- Add positive class to `set_target`.
- Change attributes names of `Project`, `Model`, `Job` and `Blueprint`
    - `features` in `Model`, `Job` and `Blueprint` are now `processes`
    - `dataset_id` and `dataset_name` migrated to `featurelist_id` and `featurelist_name`.
    - `samplepct` -> `sample_pct`
- `Model` has now `blueprint`, `project`, and `featurlist` attributes.
- Minor bugfixes.


0.1.12
======

- Minor fixes regarding rename `Job` attributes. `features` attributes now named `processes`, `samplepct` now is `sample_pct`.


0.1.11
======

(May 27, 2015)

- Minor fixes regarding migrating API from under_score names to camelCase.


0.1.10
======

(May 20, 2015)

- Remove `Project.upload_file`, `Project.upload_file_from_url` and `Project.attach_file` methods. Moved all logic that uploading file to `Project.create` method.


0.1.9
=====

(May 15, 2015)

- Fix uploading file causing a lot of memory usage. Minor bugfixes.
