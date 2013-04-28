#!/usr/bin/env python2.7
#
# Copyright 2013 Cards with Friends LLC. All Rights Reserved.

"""Helpful utilities."""

__author__ = "mqian@caltech.edu (Mike Qian)"

import collections
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
CARD_IMG_BASE = "card_images"
DECK_BASE = "decks"


class AttributeDict(dict):
  """Allow keys of a dictionary to be accessed like attributes."""
  def __init__(self, *args, **kwargs):
    super(AttributeDict, self).__init__(*args, **kwargs)
    self.__dict__ = self


def CheckJSON(doc, type_, fields):
  if "type" not in doc:
    raise KeyError("Invalid JSON config, missing key 'type'")
  if doc.type != type_:
    raise ValueError("Invalid JSON {}, got type '{}'".format(type_, doc.type))
  for field in fields:
    if field not in doc:
      raise KeyError("Missing JSON {} key '{}'".format(type_, field))


def CheckPath(path, basedir=None):
  """Make sure the given path exists and does not break out of the root base directory."""
  if basedir is not None:
    path = os.path.join(basedir, path)
  if not os.path.abspath(path).startswith(_ROOT_DIR) or not os.path.exists(path):
    # TODO(mqian): Raise a more meaningful error.
    raise IOError("Invalid path '{}'".format(path))
  return os.path.normpath(path)


def ConvertLabel(label, type_):
  try:
    return _LABEL_TYPES[type_](label)
  except KeyError:
    return label


def Sanitize(string, repl="-"):
  return string
  # return _NON_ALPHANUM_RE.sub(repl, string)
  # return _WHITESPACE_RE.sub(repl, string)