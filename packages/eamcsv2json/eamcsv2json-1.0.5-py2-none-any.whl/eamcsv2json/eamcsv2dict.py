"""
Converts EAM CSV to python dictionaries
"""

import collections
import csv
import logging

logger = logging.getLogger(__name__)


class EamCsv2Dict(object):
    """
    Handles converting from an input file to generator of dictionaries. When
    encountering errors both logs and optionally sends 3 lines of context to
    configurable error file.
    """

    def __init__(
            self,
            input_file_name,
            error_file_name=None,
            type_mappings=None,
            type_column=4,
    ):
        """
        :param input_file_name: input file to read during conversion
        :type input_file_name: str

        :param error_file_name: (optional) error file to send faulty CSV
            lines to
        :type error_file_name: str

        :param type_mappings: (optional) hash lookup from type list of fields
        :type type_mappings: dict[str, list[str]]

        :param type_column: type column number, zero based
        :type type_column: int
        """
        self._file_reader = _ErrorLineReader(input_file_name, error_file_name)
        self._type_mappings = type_mappings
        self._type_column = type_column
        self._running = False

    def convert(self):
        self._running = True
        with self._file_reader as r:
            csv_reader = (
                csv.reader(
                    r,
                    delimiter=',',
                    doublequote=False,
                    escapechar='\\',
                    quotechar='"',
                    strict=False,
                )
                if self._type_mappings
                else csv.DictReader(r)
            )
            while self._running:
                # noinspection PyBroadException
                try:
                    csv_values = next(csv_reader)
                    if self._type_mappings:
                        source_type = (csv_values[self._type_column])
                        names = self._type_mappings[source_type]
                        result = dict(zip(names, csv_values))
                    else:
                        result = csv_values
                except StopIteration:
                    break
                except:
                    logger.exception("Unexpected error recording context...")
                    r.record_errors()
                else:
                    yield result
        self._running = False

    def stop(self):
        self._running = False


class _ErrorLineReader(object):
    def __init__(self, input_file_name, error_file_name):
        self.error_file_name = error_file_name
        self.input_file_name = input_file_name
        self._buffer = collections.deque(maxlen=3)

    def __enter__(self):
        self.line_number = 0
        self._i = open(self.input_file_name, 'r')
        self._e = (
            open(self.error_file_name, 'a')
            if self.error_file_name
            else None
        )
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._i.close()
        if self._e:
            self._e.close()

    def __iter__(self):
        return self

    def __next__(self):
        line = next(self._i)
        self.line_number += 1
        self._buffer.append(line)
        return line

    def record_errors(self):
        msg = "# Error line {}".format(self.line_number)
        if self._e:
            self._e.write(msg)
            self._e.writelines(self._buffer)
        logger.error(msg)
        logger.error(self._buffer)
