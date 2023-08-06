#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Created by pat on 7/5/18
"""
.. currentmodule:: logging
.. moduleauthor:: Pat Daburu <pat@daburu.net>

This module contains the basic logging extensions.
"""
from abc import ABC, abstractmethod
import logging
from typing import Any, NamedTuple


class LogppMessage(NamedTuple):
    """
    This is a logging record, suitable to pass on to a logger as the primary
    logging message.
    """
    summary: str  #: the message summary
    detail: Any  #: the message detail object

    def __str__(self):
        return self.summary


class LogppHandler(logging.Handler, ABC):
    """
    Extend this class to create handlers specific to :py:class:`LogppMessage`
    messages.
    """
    def emit(self, record: logging.LogRecord):
        """
        This is the standard logging handler method that will filter out any
        messages that aren't :py:class:`LogppMessage` instances.  When you
        extend this type of handler, override the
        :py:func:`LogppHandler.emit_logpp` method.

        :param record: the logging record
        """
        # If the message within the record is a LogppMessage...
        if isinstance(record.msg, LogppMessage):
            # ...we'll pass it on.
            self.emit_logpp(record.msg)

    @abstractmethod
    def emit_logpp(self, msg_: LogppMessage):
        """
        Override this method to handle :py:class:`LogppMessage` messages when
        they are logged.

        :param msg_: the logpp logging message
        """
        pass  # pragma: no cover


def msg(summary: str, detail: Any) -> LogppMessage:
    """
    Create a logging record.

    :param summary: the principal summary of the logging event
    :param detail: the message detail data object
    :return: a logging record
    """
    return LogppMessage(summary=summary, detail=detail)
