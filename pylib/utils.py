#!/usr/bin/env python2.7
#
# Copyright 2013 Cards with Friends LLC. All Rights Reserved.

"""Helpful utilities."""

__author__ = "mqian@caltech.edu (Mike Qian)"

import collections
import json
import os
import re
import socket
import card_frontend

_BUFSIZE = 4096
_LABEL_TYPES = {
    "array": list,
    "boolean": bool,
    "float": float,
    "integer": int,
    "string": unicode,
}
_MESSAGE_SEP = "\r\n\r\n"
_NON_ALPHANUM_RE = re.compile(r"[^A-Za-z0-9]+")
_ROOT_DIR = os.getcwd()
_WHITESPACE_RE = re.compile(r"\s", flags=re.UNICODE)


class AttributeDict(dict):
  """Allow keys of a dictionary to be accessed like attributes."""
  def __init__(self, *args, **kwargs):
    super(AttributeDict, self).__init__(*args, **kwargs)
    self.__dict__ = self


class MessageMixin(object):
  """Mixin for message-passing."""

  # Notification handlers.
  _NOTICES = {
      "add_card": card_frontend.PlayerAddToHand,
      "clear_hand": card_frontend.PlayerClearHand,
      "clear_taken": card_frontend.PlayerClearTaken,
      "display_message": card_frontend.PlayerDisplayMessage,
      "played_card": card_frontend.AddToTrickArea,
      "remove_card": card_frontend.PlayerRemoveFromHand,
      "take_trick": card_frontend.PlayerTakeTrick,
      "update_money": card_frontend.PlayerUpdateMoney,
      "update_score": card_frontend.PlayerUpdateScore,
  }

  # Request handlers.
  _REQUESTS = {
      "get_bid": card_frontend.GetBidFromPlayer,
      "get_play": card_frontend.GetCardFromPlayer,
  }

  def __init__(self):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(("", 0))
    self.__buffer = ""
    self.__port = sock.getsockname()[-1]
    self.__socket = sock

  def Notify(self, player, action, **params):
    if action not in self._NOTICES:
      raise ValueError("Notification '{}' not supported".format(action))
    self._NOTICES[action](player, **params)

  def Request(self, player, action, **params):
    if action not in self._REQUESTS:
      raise ValueError("Request '{}' not supported".format(action))
    return self._REQUESTS[action](player, **params)

  def ReceiveMessage(self):
    while _MESSAGE_SEP not in self.__buffer:
      self.__buffer += self.__socket.recv(_BUFSIZE)
    data, self.__buffer = self.__buffer.split(_MESSAGE_SEP, 1)
    return json.loads(data)

  def SendMessage(self, **kwargs):
    bytes = 0
    data = json.dumps(kwargs) + _MESSAGE_SEP
    while data:
      sent = self.__socket.sendto(data[:_BUFSIZE], ("localhost", self.__port))
      data = data[sent:]
      bytes += sent
    return bytes


def CheckJSON(doc, type_, fields):
  if "type" not in doc:
    raise KeyError("Invalid JSON config, missing key 'type'")
  if doc.type != type_:
    raise ValueError("Invalid JSON {}, got type '{}'".format(type_, doc.type))
  for field in fields:
    if field not in doc:
      raise KeyError("Missing JSON {} key '{}'".format(type_, field))


def CheckPath(path, basedir=None):
  """Make sure the given path exists and does not break out of the root directory."""
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


def FindCard(cards, **props):
  """Find a card given its properties within some sequence of cards. Returns the first match.

  If card is not found, the result is False.
  """
  try:
    return next(c for c in cards if all(getattr(c, k, None) == v for k, v in props.items()))
  except StopIteration:
    return False


def Sanitize(string, repl="-"):
  if not isinstance(string, (str, unicode)):
    raise TypeError("Expected string argument, got type '{}'".format(type(string)))
  return string
  # return _NON_ALPHANUM_RE.sub(repl, string)
  # return _WHITESPACE_RE.sub(repl, string)