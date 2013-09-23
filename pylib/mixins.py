#!/usr/bin/env python2.7
#
# Copyright 2013 Cards with Friends LLC. All Rights Reserved.

"""Mixin classes."""

__author__ = "mqian@caltech.edu (Mike Qian)"

import socket

_BUFSIZE = 4096
_MESSAGE_SEP = "\r\n\r\n"


class MessageMixin(object):
  """Mixin for message-passing."""

  __buffer = ""
  __socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
  __socket.bind(("", 0))
  __port = __socket.getsockname()[-1]

  # Default message handlers.
  _notify_handlers = {}
  _request_handlers = {}

  @classmethod
  def ReceiveMessage(cls):
    while _MESSAGE_SEP not in cls.__buffer:
      cls.__buffer += cls.__socket.recv(_BUFSIZE)
    data, cls.__buffer = cls.__buffer.split(_MESSAGE_SEP, 1)
    return json.loads(data)

  @classmethod
  def RegisterHandler(cls, kind, **handlers):
    if kind == "notify":
      cls._notify_handlers.update(handlers)
    elif kind == "request":
      cls._request_handlers.update(handlers)
    else:
      raise ValueError("Invalid handler kind '{}', expected 'notify' or 'request'".format(kind))

  @classmethod
  def SendMessage(cls, **kwargs):
    bytes = 0
    data = json.dumps(kwargs) + _MESSAGE_SEP
    while data:
      sent = cls.__socket.sendto(data[:_BUFSIZE], ("localhost", cls.__port))
      data = data[sent:]
      bytes += sent
    return bytes

  def Notify(self, action, **params):
    if action not in self._notify_handlers:
      raise ValueError("Notification type '{}' not supported".format(action))
    self._notify_handlers[action](**params)

  def Request(self, action, **params):
    if action not in self._request_handlers:
      raise ValueError("Request type '{}' not supported".format(action))
    return self._request_handlers[action](**params)
