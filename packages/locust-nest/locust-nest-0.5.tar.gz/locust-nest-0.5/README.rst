locust-nest
===========
|license| |versions| |pypi| |contributors|

.. |license| image:: https://img.shields.io/github/license/ps-george/locust-nest.svg
  :alt: license
  :target: https://github.com/ps-george/locust-nest/blob/master/LICENSE

.. |versions| image:: https://img.shields.io/pypi/v/locust-nest.svg 
  :alt: PyPI
  :target: https://pypi.org/project/locust-nest/

.. |pypi| image:: https://img.shields.io/pypi/pyversions/locust-nest.svg
  :alt: PyPI
  :target: https://pypi.org/project/locust-nest/

.. |contributors| image:: https://img.shields.io/github/contributors/ps-george/locust-nest.svg
  :alt: GitHub contributors
  :target: https://github.com/ps-george/locust-nest/graphs/contributors

Locust wrapper. Import Locust classes from a folder and run Locust using those classes with weights determined in a config file,
with an option to guide the generation of the config file.

- `locust-nest docs`_
- `locust-nest pip package`_
- `locust-nest source code`_

`Locust.io`_
------------- 

- `Locust docs`_
- `Locust source code`_

.. _`locust-nest docs`: https://ps-george.github.io/locust-nest
.. _`locust-nest pip package`: https://pypi.org/project/locust-nest/
.. _`locust-nest source code`: https://github.com/ps-george/locust-nest

.. _`Locust.io`: https://locust.io
.. _`Locust docs`: https://docs.locust.io/en/stable/
.. _`Locust source code`: https://github.com/locustio/locust

What is locust-nest for?
========================

locust-nest is a wrapper around Locust to simplify load testing.

Use locust-nest for *load generation*.

Unit tests or live user testing will tell you if your system works for 1 user, locust-nest will show you if it can scale to 100, 1000 or 100,000 simultaneous users.

It allows you to configure the weighting of each of your Locust classes so that you can run different load scenarios without changing any Python code.


Installation
============

.. code-block:: bash

    pip install locust-nest

The following will create an example file and script in the [example/] dir:

.. code-block:: bash

    locust-nest install [example/]

Note: At the moment locust-nest uses pslocust_ to provide more current Locust features than the current Locust release.

.. _pslocust: https://pypi.org/project/pslocust/

Quick start
===========

locust-nest is designed to provide a framework for simulating a specified load on a system.

Behaviour models are codified using Locust, an open-source load testing tool that allows abitrarily complex user behaviour modelling since all tasks are written in Python. 

This wrapper searches all `.py` files in the :code:`--model_dir (-d)` directory and subdirectories for subclasses of `Locust` and runs Locust with all of those classes.

To run locust-nest, simply use locust-nest command with default Locust arguments:

.. code-block:: bash

  locust-nest --model_dir=models/ --host=https://www.example.com ...

To be guided through the generation of a config file, use the :code:`--configure` flag: 

.. code-block:: bash
  
  locust-nest --configure --host=https://www.example.com ...


An example structure for one of these TaskSets is:

.. code-block:: python

  from locust import TaskSet, task

  class ModelBehaviour(TaskSet):
    weight = 0
    def on_start(self):
      # Log in & save token

      # retrieve bulk information needed for other tasks

      # other to-dos on starting this group of tasks
      pass

    def on_stop(self):
      # unclaim resources e.g. username
      pass
    
    @task(5) # task decorator with relative weight of executing the task
    def model_action(self):
      # codified behaviour of a particular action this model may perform
      # e.g. registering a customer
      return
    

If the :code:`--include-tasksets (-T)` flag is used, it will also find all subclasses of `TaskSet` and add these to a `NestTaskset`,
which packages all the tasks with their desired weights into a `HTTPLocust` class.
of those classes, with weights specified in a :code:`--config_file`.
Note: Python 2 does not have support for recursive subdirectories, so at the moment only searches 1 directory deep :code:`{model_dir}/*/`

Workflow
--------

1. locust-nest will import all TaskSets from `models/` into one NestLocust, weighting according to :code:`--config_file`.
2. locust-nest will find all Locust's, weighting according to :code:`--config_file`.
3. Display weightings that will be used with confirmation prompt (skippable with some commandline argument).
4. Run Locust with weightings set from config for the Locusts and NestLocust classes
5. locust-nest will have an option to automatically manage distributed resources for Locust master-slave mode. (NOT IMPLEMENTED)

Example TaskSet
---------------

.. code-block:: python

    from locust import TaskSet, task

    class ExampleModel(TaskSet):
        weight = 0

        def on_start(self):
            """Set up before running tasks.

            For example:
            * Log in & save token
            * Retrieve bulk information needed for other tasks

            """
            return

        def on_stop(self):
            """Teardown: unclaim resources e.g. claimed user.

            """

            return

        # task decorator with relative weight of executing the task
        @task(5) 
        def model_action(self):
            """Codified behaviour of a particular action this model may perform
            e.g. registering a customer

            """
            self.client.get("/")
            return


Aims of locust-nest
===================

1. Users will be able to place any number of directories containing TaskSets 
   and Locusts with each representing an encapsulated group of tasks.
2. locust-nest will find all TaskSets contained in a specified directory
   and group them into one Locust class with corresponding weights specified
   in a config file, allowing easy modularity in adding or removing TaskSets
   without needing to change any code in the locust-nest repository. Locusts
   will also be found and configured with specific weights.
3. There will be an interactive configure option which creates a config file
   that specifies the relative weights of each TaskSet, allowing users to easily
   adjust the different ratios of TaskSet types, but still allowing non-interactive 
   use of the system when the config file has been created.
4. locust-nest will be automatable, ideally callable with a git hook for load-testing
   continuous integration or in response to a Slack command. The results will be human readable,
   ideally some kind of index of scalability of the system, so that the evolution of the system
   under test's scalability can be tracked.
5. locust-nest will be able to automatically deploy to AWS Lambda or equivalent and
   run load testing under the distributed master-slave variant in order to be able
   to easily scale arbitrarily.
   
