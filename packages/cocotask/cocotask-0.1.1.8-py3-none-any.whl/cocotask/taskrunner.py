import argparse
import importlib
from cocotask import CocoConsumerManager
import logging
import json
from jsmin import jsmin
import sys
import codecs

def class_for_name(module_name, class_name, path):
    sys.path.append(path)
    # load the module, will raise ImportError if module cannot be loaded
    m = importlib.import_module(module_name)
    # get the class, will raise AttributeError if class cannot be found
    c = getattr(m, class_name)
    return c


def load_config(path):
    with codecs.open(path, 'r', 'utf-8') as f:
        config = json.loads(jsmin(f.read()))


    return config


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('config', help = 'define config file path')
    parser.add_argument('module', help = 'define the module name')
    parser.add_argument('worker', help = 'define the worker class name')
    parser.add_argument('worker_number', help = 'number of workers to work', type=int)
    parser.add_argument('--logginglevel', help = 'define logging level')
    parser.add_argument('--modulepath', default = '.', help = 'path to the module. Default to .')

    args = parser.parse_args()

    if args.logginglevel:
        level = getattr(logging, args.logginglevel.upper(), None)
        logging.basicConfig(level=level)

    config = load_config(args.config)

    worker_class = class_for_name(args.module, args.worker, args.modulepath)

    manager = CocoConsumerManager(config, worker_class, args.worker_number)
    manager.start()


if __name__ == '__main__':  # pragma: no cover
    main()