#!/usr/bin/env python2.7
#
# Copyright 2013 Cards with Friends LLC. All Rights Reserved.

"""Helpful utilities."""

__author__ = "mqian@caltech.edu (Mike Qian)"

import collections
import json
import os
import re

_LABEL_TYPES = {
    "array": list,
    "boolean": bool,
    "float": float,
    "integer": int,
    "string": unicode,
}
_NON_ALPHANUM_RE = re.compile(r"[^A-Za-z0-9]+")
_ROOT_DIR = os.getcwd()
_WHITESPACE_RE = re.compile(r"\s", flags=re.UNICODE)


class AttributeDict(dict):
  """Allow keys of a dictionary to be accessed like attributes."""
  def __init__(self, *args, **kwargs):
    super(AttributeDict, self).__init__(*args, **kwargs)
    self.__dict__ = self


def CheckJSON(doc, doc_type, fields):
  if "type" not in doc:
    raise KeyError("Invalid JSON config, missing key 'type'")
  if doc.type != doc_type:
    raise ValueError("Invalid JSON {}, got type '{}'".format(doc_type, doc.type))
  for field in fields:
    if field not in doc:
      raise KeyError("Missing JSON {} key '{}'".format(doc_type, field))


def CheckPath(path, basedir=None):
  """Make sure the given path exists and does not break out of the root directory."""
  if basedir is not None:
    path = os.path.join(basedir, path)
  if not os.path.abspath(path).startswith(_ROOT_DIR) or not os.path.exists(path):
    # TODO(mqian): Raise a more meaningful error.
    raise IOError("Invalid path '{}'".format(path))
  return os.path.normpath(path)


def ConvertLabel(label, label_type):
  try:
    return _LABEL_TYPES[label_type](label)
  except KeyError:
    return label


def FindCard(cards, **props):
  """Find a card given its properties within some sequence of cards. Returns the first match.

  If card is not found, the result is False.
  """
  try:
    return next(c for c in cards if all(getattr(c, k, None) == v for k, v in props.items()))
  except StopIteration:
    return False


def Flatten(lst):
  """Flattens a multi-dimensional (possibly irregular) list."""
  for elem in lst:
    if isinstance(elem, collections.Iterable) and not isinstance(elem, basestring):
      for subelem in Flatten(elem):
        yield subelem
    else:
      yield elem


def Sanitize(string, repl="-"):
  if not isinstance(string, basestring):
    raise TypeError("Expected string argument, got type '{}'".format(type(string)))
  return string
  # return _NON_ALPHANUM_RE.sub(repl, string)
  # return _WHITESPACE_RE.sub(repl, string)