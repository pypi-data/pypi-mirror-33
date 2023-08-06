##########
QuickStart
##########

.. note::

    You must set up credentials in order to access the DataRobot API. For more information,
    see :ref:`Credentials<credentials>`

All of the modeling within DataRobot happens within a project. Each project has one dataset that is used as the source from which to train models.

There are three steps required to begin modeling:

1. Create an empty project.
2. Upload a data file to model.
3. Select parameters and start training models with the autopilot.

The following command includes these three steps. It is equivalent to choosing all of the default settings recommended by DataRobot.

.. code-block:: python

    import datarobot as dr
    project = dr.Project.start(project_name='My new project',
                            sourcedata='/home/user/data/last_week_data.csv',
                            target='ItemsPurchased')
                            
Where:

* ``name`` is the name of the new DataRobot project.
* ``sourcedata`` is the path to the dataset.
* ``target`` is the name of the target feature column in the dataset.                             

