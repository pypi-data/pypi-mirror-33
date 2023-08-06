# encoding: utf-8

import inspect
import logging_helper
from future.utils import iteritems

logging = logging_helper.setup_logging()

CONVERTER = u'converter'


def convert(value,
            converter,
            permitted_conversion_results=(u'', u'-', u'n/a', None),
            **kwargs):

    """
    Used to convert a value using the supplied conversion function

    :param value: value to convert
    :param converter: conversion function or a function dictionary
    :param permitted_conversion_results: a list of values that don't
                                         cause exceptions to be logged
    :param **kwargs parameter values for the converter function

    might be used for calling the function

       def epoch_to_time(ep = None,
                         format = u'%d-%m-%y %H:%M:%S')

    value is used as the the first parameter

        convert(value = datetime.now(),
                converter = epoch_to_time,
                format = u'%d-%m-%y')

    is equivalent to calling

        epoch_to_time(datetime.now(),
                    format = u'%d-%m-%y')

    """
    try:
        return converter(value,
                         **kwargs)
    except Exception as e:
        if value not in permitted_conversion_results:
            source = inspect.getsource(converter)
            logging.warning(u'Failed to convert value ({value}) '
                            u'using {function}. ({source})\n'
                            .format(value = value,
                                    function = converter,
                                    source = source))
            logging.exception(e)
    return value


def convert_to_unicode(source_string):
    # TODO: Is this required for Py3??
    return source_string if isinstance(source_string, unicode) else unicode(source_string)


