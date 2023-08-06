# encoding: utf-8

# Get module version
from ._metadata import __version__

# Import key items from module
from .convert import (CONVERTER,
                      convert,
                      convert_to_unicode)

from .date_and_time_conversions import (MONDAY,
                                        TUESDAY,
                                        WEDNESDAY,
                                        THURSDAY,
                                        FRIDAY,
                                        SATURDAY,
                                        SUNDAY,
                                        datetime_to_epoch,
                                        epoch_to_time,
                                        string_to_time,
                                        day_of_week,
                                        next_day,
                                        previous_day,
                                        get_datetime_conversion)
from .dx import dx
from .ex import ex

from .storage import (BYTES,
                      KILOBYTES,
                      KIBIBYTES,
                      MEGABYTES,
                      MEBIBYTES,
                      GIGABYTES,
                      GIBIBYTES,
                      TERABYTES,
                      TEBIBYTES,
                      PETABYTES,
                      PEBIBYTES,
                      EXABYTES,
                      EXBIBYTES,
                      ZETTABYTES,
                      ZEBIBYTES,
                      YOTTABYTES,
                      YOBIBYTES,
                      convert_storage_size)

from .modify import modify_fields

from .excel_to_json import workbook_to_json

from .text.asciify import ASCIIfy
from .text.fullwidth import convert_to_full_width_characters

# Set default logging handler to avoid "No handler found" warnings.
from logging import NullHandler, getLogger
getLogger(__name__).addHandler(NullHandler())
