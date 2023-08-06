import glob
import inspect
import json
import logging
import os
import random
import sys

from locust import HttpLocust, TaskSet, task
from locust.main import load_locustfile, load_tasksetfile

logger = logging.getLogger(__name__)


def load_dir(dir_path, func, ignore_prefix='_'):
    """Searches the directory at *dir_path* and subdirectories for all
    sub-classes not starting with *ignore_prefix* and specified by func,
    finds and imports all classes and returns dictionary with name and class
    callable.

    Arguments:
        dir_path {string} -- path to the directory to import TaskSet classes.
        ignore_file_prefix {string} -- Ignore all files starting with prefix.

    Returns: dict -- {__doc__:class callable} for each *.py file in *dir_path*.
    """

    classes = {}
    filepaths = (glob.glob('{}**/*.py'.format(dir_path)) +
                 glob.glob('{}/*.py'.format(dir_path)))
    if not filepaths:
        err = 'No .py files found in "{}"'.format(filepaths)
        logger.warning(err)
        return None

    for filepath in filepaths:
        _, filename = os.path.split(filepath)
        if not filename.startswith(ignore_prefix):
            logger.info('Checking {}'.format(filepath))
            _, t2 = func(filepath)
            classes.update(t2)
    return classes


def load_taskset_dir(dir_path='tasksets/', ignore_prefix='_'):
    """Searches the directory at *dir_path* and subdirectories for all TaskSet
    sub-classes not starting with *ignore_prefix*, finds and imports all
    classes and returns dictionary with name and class callable.

    Arguments:
        dir_path {string} -- path to the directory to import TaskSet classes.
        ignore_file_prefix {string} -- Ignore all files starting with prefix.

    Returns: dict -- {__doc__:class callable} for each *.py file in *dir_path*.
    """
    tasksets = load_dir(dir_path, load_tasksetfile, ignore_prefix)
    return tasksets


def load_locust_dir(dir_path='locusts/', ignore_prefix='_'):
    """Searches the directory at *dir_path* and subdirectories for all Locust
    sub-classes not starting with *ignore_prefix*, finds and imports all
    classes and returns dictionary with name and class callable.

    Arguments:
        dir_path {string} -- path to the directory to import TaskSet classes.
        ignore_file_prefix {string} -- Ignore all files starting with prefix.

    Returns: dict -- {__doc__:class callable} for each *.py file in *dir_path*.
    """
    locusts = load_dir(dir_path, load_locustfile, ignore_prefix)
    return locusts


def load_config(config_file):
    config = {}
    if os.path.exists(config_file):
        with open(config_file, 'r') as f:
            try:
                config = json.load(f)
            except ValueError:
                # Config format invalid
                logger.warning('Config file ({}) format invalid.'.format(config_file))
    return config


def collect_tasksets(dir_path='tasksets/', config_file='config.json'):
    """Load tasksets into a dictionary format used by TaskSets to specify
    tasks and their weights. Adds the stop() method to the tasks of all
    TaskSets imported in this way.

    Returns:
        dict -- {class callable : weight, ... }
                OR empty dict if no TaskSets are found.

    """

    config = load_config(config_file)
    if config=={}:
        logger.info('No config file found, will use defaults.')
    tasksets = load_taskset_dir(dir_path)
    if not tasksets:
        return {}
    nest_tasks = {}
    weights = config.get('tasksets', None)
    for key, callee in tasksets.items():
        try:
            weight = weights[key]
        except TypeError:
            msg = """No weight given for {} TaskSet in config,
                     using default from TaskSet.""".format(key)
            logger.info(msg)
            try:
                weight = callee.weight
            except AttributeError:
                msg = """No default weight given for {} TaskSet in TaskSet
                         definition {}.weight, using 1.""".format(key, key)
                logger.info(msg)
                weight = 1
        # If weight is zero, don't add taskset

        def stop(self):
            self.interrupt()

        if weight is not None:
            if weight > 0:
                callee.tasks.append(stop)
                nest_tasks[callee] = weight
    logger.info("Found following tasksets and weights: {}".format(nest_tasks))
    return nest_tasks


def collect_locusts(dir_path='locusts/', config_file='config.json'): # From config file get weights for each of the locust classes
    config = load_config(config_file)
    if not config:
        logger.info('No config file found, will use defaults.')

    # Find all the Locust classes
    locusts = load_locust_dir(dir_path)

    if not locusts:
        return []
    locust_classes = []

    weights = config.get('locusts', None)
    for key, callee in locusts.items():
        try:
            weight = weights[key]
        except TypeError:
            msg = "No weight given for {} Locust in config, using default from Locust.".format(key)
            logger.info(msg)
            try:
                weight = callee.weight
            except AttributeError:
                msg = """No default weight given for {} TaskSet in TaskSet definition {}.weight, using 1.""".format(key, key)
                logger.info(msg)
                weight = 1
        if weight is None:
            weight = 1
        if weight:
            setattr(locusts[key], 'weight', weight)
            if weight > 0:
                locust_classes.append(locusts[key])
    locust_weights = [(callee, callee.weight) for callee in locust_classes]
    logger.info("Found the following Locusts and weights: {}".format(locust_weights))
    return locust_weights
