#!/usr/bin/env python2.7
#
# Copyright 2013 Cards with Friends LLC. All Rights Reserved.

"""Helpful utilities."""

__author__ = "mqian@caltech.edu (Mike Qian)"

import collections
import os

_LABEL_TYPES = {
    "array": list,
    "boolean": bool,
    "float": float,
    "integer": int,
    "string": unicode,
}
_ROOT_DIR = os.getcwd()


class AttributeDict(dict):
  """Allow keys of a dictionary to be accessed like attributes."""
  def __init__(self, *args, **kwargs):
    super(AttributeDict, self).__init__(*args, **kwargs)
    self.__dict__ = self


def CheckJSON(doc, type, fields):
  if "type" not in doc:
    raise KeyError("Invalid JSON config, missing key 'type'")
  if doc.type != type:
    raise ValueError("Invalid {}, got type '{}'".format(type, doc.type))
  for field in fields:
    if field not in doc:
      raise KeyError("Missing JSON {} key '{}'".format(type, field))


def CheckPath(basedir, path):
  """Make sure the given path exists and does not break out of the root base directory."""
  path = os.path.join(basedir, path)
  if not os.path.abspath(path).startswith(_ROOT_DIR) or not os.path.exists(path):
    # TODO(mqian): Raise a more meaningful error.
    raise ValueError("Invalid path '{}'".format(path))
  return os.path.normpath(path)


def ConvertLabel(label, type):
  try:
    return _LABEL_TYPES[type](label)
  except KeyError:
    return label