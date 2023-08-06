from __future__ import absolute_import, division, print_function

import importlib
import logging
import os
import sys
from time import sleep

import yaml


def run_task(task, paths):
    script = task['script']
    func = task['func']
    params = task.get('params', [])

    loglevel = task.get('loglevel', None)
    if loglevel is not None:
        logging.getLogger().setLevel(loglevel.upper())

    paths = task['paths']
    sys.path = [x for x in paths]
    for path in paths:
        path = path.replace('~', os.environ['HOME'])
        sys.path.insert(0, path)

    module = importlib.import_module(script)
    main = getattr(module, func)

    kwargs = {}
    for param in params:
        if isinstance(param, dict):
            kwargs.update(param)

    args_str = ', '.join(['{k}={v}'.format(k=k, v=kwargs[k]) for k in kwargs])
    logging.info('evaluating `%s.%s(%s)`', script, func, args_str)

    sleep(0.1)
    result = main(**kwargs)

    return {'task': task, 'result': result}


def run_yaml(fn):
    paths = [x for x in sys.path]
    with open(fn) as f:
        cfg = yaml.load(f.read())
    run_task(cfg, paths)
