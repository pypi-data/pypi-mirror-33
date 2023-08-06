# -*- coding: utf-8 -*-
# *******************************************************
#   ____                     _               _
#  / ___|___  _ __ ___   ___| |_   _ __ ___ | |
# | |   / _ \| '_ ` _ \ / _ \ __| | '_ ` _ \| |
# | |__| (_) | | | | | |  __/ |_ _| | | | | | |
#  \____\___/|_| |_| |_|\___|\__(_)_| |_| |_|_|
#
#  Sign up for free at http://www.comet.ml
#  Copyright (C) 2015-2019 Comet ML INC
#  This file can not be copied and/or distributed without the express
#  permission of Comet ML Inc.
# *******************************************************

"""
Author: Boris Feld

This module contains logging configuration for Comet

"""

import logging
from copy import copy

MSG_FORMAT = "COMET %(levelname)s: %(message)s"
FILE_MSG_FORMAT = "[%(process)d-%(processName)s:%(thread)d] %(relativeCreated)d COMET %(levelname)s [%(filename)s:%(lineno)d]: %(message)s"

GO_TO_DOCS_MSG = " \nFor more details, please refer to: https://www.comet.ml/docs/python-sdk/warnings-errors"

INTERNET_CONNECTION_ERROR = (
    "Failed to establish connection to Comet server. Please check your internet connection. "
    "Your experiment would not be logged"
    + GO_TO_DOCS_MSG
)


INVALID_API_KEY = (
    "The given api key %s is invalid, please check it against the dashboard. "
    "Your experiment would not be logged"
    + GO_TO_DOCS_MSG
)

IPYTHON_NOTEBOOK_WARNING = (
    "Comet.ml support for Ipython Notebook is limited at the moment,"
    " automatic monitoring and stdout capturing is deactivated"
    + GO_TO_DOCS_MSG
)


METRIC_ARRAY_WARNING = (
    "Cannot safely convert %r object to a scalar value, using it string"
    " representation for logging."
)

EXPERIMENT_OPTIMIZER_API_KEY_MISMTACH_WARNING = (
    "WARNING: Optimizer and Experiments API keys mismatch. Please use"
    " the same API key for both."
)


PARSING_ERR_MSG = """We failed to parse your parameter configuration file.

Type casting will be disabled for this run, please fix your configuration file.
"""

CASTING_ERROR_MESSAGE = """Couldn't cast parameter %r, returning raw value instead.
Please report it to comet.ml and use `.raw(%r)` instead of `[%r]` in the meantime."""

NOTEBOOK_MISSING_ID = (
    "We detected that you are running inside a Ipython/Jupyter notebook environment but we cannot save your notebook source code."
    " Please be sure to have installed comet_ml as a notebook server extension by running:\n"
    "jupyter comet_ml enable"
    + GO_TO_DOCS_MSG
)

LOG_IMAGE_OS_ERROR = (
    "We failed to read file %s for uploading.\n"
    "Please double check the file path and permissions"
)

LOG_IMAGE_TOO_BIG = ("File %s is bigger than the upload limit, %s > %s")

LOG_FIGURE_TOO_BIG = ("Figure is bigger than the upload limit, %s > %s")

NATIVE_STD_WRAPPER_NOT_AVAILABLE = (
    "Native output logging mode is not available, fallbacking on basic output logging"
)

UNKOWN_STD_WRAPPER_SPEC = (
    "Unknown output logging mode: %s, fallbacking on basic output logging"
)

EXPERIMENT_LIVE = ("Experiment is live on comet.ml %s\n")


class TracebackLessFormatter(logging.Formatter):

    def format(self, record):
        # Make a copy of the record to avoid altering it
        new_record = copy(record)

        # And delete exception informations so no traceback could be formatted
        # and displayed
        new_record.exc_info = None
        new_record.exc_text = None

        return super(TracebackLessFormatter, self).format(new_record)


WS_ON_OPEN_MSG = "WS Socket connection open"

WS_ON_CLOSE_MSG = "WS connection closed"


def setup(log_file_path=None, file_level=None):
    root = logging.getLogger("comet_ml")
    root.setLevel(logging.DEBUG)

    # Don't send comet-ml to the application logger
    root.propagate = False

    # Add handler
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    console.setFormatter(TracebackLessFormatter(MSG_FORMAT))
    root.addHandler(console)

    # The std* logger might conflicts with the logging if a log record is
    # emitted for each WS message as it would results in an infinite loop. To
    # avoid this issue, all log records after the creation of a message should
    # be at a level lower than info as the console handler is set to info
    # level.

    # Add an additional file handler
    if log_file_path is not None:
        file_handler = logging.FileHandler(log_file_path)

        if file_level is not None:
            file_level = file_level.upper()
            file_handler.setLevel(file_level)
        else:
            file_handler.setLevel(logging.DEBUG)

        file_handler.setFormatter(logging.Formatter(FILE_MSG_FORMAT))
        root.addHandler(file_handler)
