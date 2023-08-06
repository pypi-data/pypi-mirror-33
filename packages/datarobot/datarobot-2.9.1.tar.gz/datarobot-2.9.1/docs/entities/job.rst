####
Jobs
####

The **Job** (:doc:`API reference </api/job>`) class is a generic representation of jobs running
through a project's queue.  Many tasks involved in modeling, such as creating a new model or
computing feature impact for a model, will use a job to track the worker usage and progress of
the associated task.

Checking the Contents of the Queue
**********************************
To see what jobs running or waiting in the queue for a project, use the ``Project.get_all_jobs``
method.

.. code-block:: python

    from datarobot.enums import QUEUE_STATUS

    jobs_list = project.get_all_jobs()  # gives all jobs queued or inprogress
    jobs_by_type = {}
    for job in jobs_list:
        if job.job_type not in jobs_by_type:
            jobs_by_type[job.job_type] = [0, 0]
        if job.status == QUEUE_STATUS.QUEUE:
            jobs_by_type[job.job_type][0] += 1
        else:
            jobs_by_type[job.job_type][1] += 1
    for type in jobs_by_type:
        (num_queued, num_inprogress) = jobs_by_type[type]
        print('{} jobs: {} queued, {} inprogress'.format(type, num_queued, num_inprogress)')

Cancelling a Job
****************
If a job is taking too long to run or no longer necessary, it can be cancelled easily from the
``Job`` object.

.. code-block:: python

    from datarobot.enums import QUEUE_STATUS

    project.pause_autopilot()
    bad_jobs = project.get_all_jobs(status=QUEUE_STATUS.QUEUE)
    for job in bad_jobs:
        job.cancel()
    project.unpause_autopilot()

Retrieving Results From a Job
*****************************
Once you've found a particular job of interest, you can retrieve the results once it is complete.
Note that the type of the returned object will vary depending on the ``job_type``.  All return types
are documented in ``Job.get_result``.

.. code-block:: python

    from datarobot.enums import JOB_TYPE

    time_to_wait = 60 * 60  # how long to wait for the job to finish (in seconds) - i.e. an hour
    assert my_job.job_type == JOB_TYPE.MODEL
    my_model = my_job.get_result_when_complete(max_wait=time_to_wait)
