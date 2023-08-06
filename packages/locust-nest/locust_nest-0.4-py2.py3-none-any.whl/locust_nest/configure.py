from helpers import is_int, retry_valid_input
from nest import load_taskset_dir, load_locust_dir
import json
import sys
import os
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.DEBUG)
logger.addHandler(stream_handler)


def make_config(dir_path=None, include_tasksets=False):
    """Guide a user through making a config file for Nest.

    Keyword Arguments:
        dir_path {str (path)} -- Folder with user's Locusts & TaskSets.
                                 (default: {None})

    Returns:
        dict -- Nest config file.

    """

    def default_weight(callee):
        try:
            return callee.weight
        except:
            return 1

    # For each TaskSet found using collect tasksets
    taskset_qs = {}
    total_tasksets = 0
    if include_tasksets:
        tasksets = load_taskset_dir(dir_path)
        for name, callee in tasksets.items():
            t_quantity = retry_valid_input(
                    prompt='How many {}s would you like to have?'.format(name),
                    title='quantity',
                    condition=is_int,
                    default=default_weight(callee),
                    transform=int)
            taskset_qs[name] = t_quantity
            total_tasksets += t_quantity

    # Load locusts
    locust_qs = {}
    total_locusts = 0
    locusts = load_locust_dir(dir_path)
    for name, callee in locusts.items():
        l_quantity = retry_valid_input(
                prompt='How many {}s would you like to have?'.format(name),
                title='quantity',
                condition=is_int,
                default=default_weight(callee),
                transform=int)
        locust_qs[name] = l_quantity
        total_locusts += l_quantity

    config = {
        'tasksets': taskset_qs,
        'total_tasksets': total_tasksets,
        'locusts': locust_qs,
        'total_locusts': total_locusts
    }

    return config


def save_config(config, config_file=None):
    """Helper to save config dict to user-defined location.

    Arguments:
        config {dict} -- Config file.

    Keyword Arguments:
        config_file {str (path)} --
                Path to config file. If not specified will
                ask the user. (default: {None})

    Returns:
        bool -- Successful or not.
    """

    # Specify file path to save the config file to
    if config_file is None:
        config_file = retry_valid_input(
                prompt='What would you like to name this config?',
                title='config file',
                default='config.json')
    logger.info('Saving config to {}'.format(config_file))
    with open(config_file, 'w') as f:
        json.dump(config, f)
    if os.path.exists(config_file):
        return True
    return False
