from __future__ import absolute_import, division, print_function

import sys
import logging

from move_carrots import run_yaml

if __name__ == '__main__':
    for yaml_fn in sys.argv[1:]:
        logging.info('run_task on %s', yaml_fn)
        run_yaml(yaml_fn)
