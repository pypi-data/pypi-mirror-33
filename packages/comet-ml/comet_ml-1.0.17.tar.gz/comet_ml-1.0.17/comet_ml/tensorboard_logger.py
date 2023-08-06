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


import logging
import sys

from comet_ml import config

LOGGER = logging.getLogger(__name__)
DISABLED = False


TENSORFLOW_ALREADY_IMPORTED_MSG = (
    "Please import comet before importing any Tensorflow modules"
)

def extract_from_add_summary(file_writer, summary, global_step):
    from tensorflow.core.framework import summary_pb2

    extracted_values = {}

    if isinstance(summary, bytes):
        summ = summary_pb2.Summary()
        summ.ParseFromString(summary)
        summary = summ

    for value in summary.value:
        field = value.WhichOneof("value")

        if field == "simple_value":
            extracted_values[value.tag] = value.simple_value

    return extracted_values, global_step


def add_summary_logger(real_add_summary):

    def wrapper(*args, **kwargs):
        ret_val = real_add_summary(*args, **kwargs)
        try:
            disabled_monkey_patching = config.experiment.disabled_monkey_patching
            if (
                config.experiment
                and disabled_monkey_patching is False
                and DISABLED is False
            ):
                LOGGER.debug("TENSORBOARD LOGGER CALLED")
                params, step = extract_from_add_summary(*args, **kwargs)
                config.experiment.log_multiple_metrics(params, step=step)
        except Exception as e:
            LOGGER.error(
                "Failed to extract parameters from add_summary()", exc_info=True
            )
        finally:
            return ret_val

    return wrapper


ADD_SUMMARY = [
    ("tensorflow.python.summary.writer.writer", "SummaryToEventTransformer.add_summary")
]


def patch(module_finder):
    if "tensorflow" in sys.modules or "tensorboard" in sys.modules:
        LOGGER.warning(TENSORFLOW_ALREADY_IMPORTED_MSG)

    # Register the fit methods
    for module, object_name in ADD_SUMMARY:
        module_finder.register(module, object_name, add_summary_logger)


if "tensorboard" in sys.modules:
    raise SyntaxError("Please import comet before importing any tensorboard modules")
