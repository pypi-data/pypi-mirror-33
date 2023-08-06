''' This utility module allow to instantiate object from a given package/path '''

import importlib
import pkgutil
import logging

from .caseinsensitivedict import CaseInsensitiveDict

CLASS_NAME_ATTR = '__dynamoclass__'

_logger = logging.getLogger(__name__)
_dynamo_cache = CaseInsensitiveDict()

def load_classes(package_str):
    '''Load all classes from modules of a given `package_str`. All class instances are stored in a case-insensitive `dict`
    and returned. If a package doesn't contain any class `None` is returned'''

    _logger.debug('Loading all modules from %s', package_str)
    package = importlib.import_module(package_str)
    package_path = package.__path__
    _logger.debug('Searching for modules in package %s (%s)', package_str, package_path)
    for _, name, ispkg in pkgutil.iter_modules(package_path, package_str + "."):
        if not ispkg:
            _logger.debug('Found module: %s', name)
            module = importlib.import_module(name)
            if hasattr(module, CLASS_NAME_ATTR):
                class_name = getattr(module, CLASS_NAME_ATTR)
                _logger.debug('Found class: %s', class_name)
                clasz = getattr(module, class_name)

                if package_str not in _dynamo_cache:
                    _dynamo_cache[package_str] = CaseInsensitiveDict()
                
                if class_name not in _dynamo_cache[package_str]:
                    _dynamo_cache[package_str][class_name] = clasz
                    _logger.debug('Correctly loaded class: %s from: "%s"', class_name, package_str)
                else:
                    _logger.warning('Already loaded class: %s from: "%s"', class_name, package_str)
            else:
                _logger.warning('Module inside %s does not contain required attribute: %s', package_str, CLASS_NAME_ATTR)
        else:
            _logger.warning('Ignoring package: %s', name)

    if package_str in _dynamo_cache:
        return _dynamo_cache[package_str]
    else:
        return None


def get_all(package_str):
    '''Retrieve all classes of a given package. All arguments are case-insensitive''' 
    if (package_str in _dynamo_cache):
        return _dynamo_cache[package_str]
    return None

def get(package_str, classname):
    '''Retrieve from the internal cache a class instance. All arguments are case-insensitive''' 
    if (package_str in _dynamo_cache) and (classname in _dynamo_cache[package_str]):
        return _dynamo_cache[package_str][classname]
    return None
        
        