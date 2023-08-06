import argparse
import logging
import signal

from eamcsv2json.dict2json import dict_to_json_generator
from eamcsv2json.eamcsv2dict import EamCsv2Dict
from eamcsv2json.transform2dict import parse_transform_config

logger = logging.getLogger(__name__)

_DESC = """
EAM (Splunk) CSV to JSON conversion script meant to handle larger files with
potential errors. New lines and quotes are handled gracefully when data
fields are quoted in double quotes (") and escaped with backslash (\). This
is outside RFC-4180 specification.

Configuration file is of the form
```
[ProcessRollup2]
FIELDS = timestamp, cid, aid, aip, name, event_simpleName, ...

...
```

Optional the string `-v02_fields` will be removed from section names
```
[ProcessRollup2-v02_fields]
FIELDS = timestamp, cid, aid, aip, name, event_simpleName, ...
```
"""


def main():
    parser = argparse.ArgumentParser(
        description=_DESC,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        '-i', '--input',
        required=True,
        help='CSV file name to be read'
    )
    parser.add_argument(
        '-o', '--output',
        default='',
        help='(optional) Output file name; else stdout',
    )
    parser.add_argument(
        '-e', '--errors',
        default='',
        help='(optional) Error file name; when provided CSV 3 lines of'
             ' context will be printed. Default is content to log file only'
    )
    parser.add_argument(
        '-l', '--log',
        default='',
        help='(optional) Log file name; when provided log message will go'
             ' to file. Default is stderr'
    )
    parser.add_argument(
        '-c', '--config',
        default='',
        help='(optional) Configuration for type mappings; else first row is'
             ' considered for labels. When provided type column setting is'
             ' used',
    )
    parser.add_argument(
        '-t', '--type-column',
        default=4,
        type=int,
        help='(optional) When config set use this column to expect type '
             'mapping. Default 4',
    )
    pargs = parser.parse_args()

    # configure logging
    logging_config = (
        dict(filename=pargs.log, filemode="a")
        if pargs.log
        else dict()
    )
    logging.basicConfig(**logging_config)

    # read configuration
    mappings = (
        parse_transform_config(pargs.config)
        if pargs.config
        else None
    )

    # prep conversion system
    dict_converter = EamCsv2Dict(
        input_file_name=pargs.input,
        error_file_name=pargs.errors,
        type_mappings=mappings,
        type_column=pargs.type_column,
    )

    # graceful ctrl-c handling
    def _term_handler(_, __):
        logger.warning("received sigterm")
        dict_converter.stop()

    signal.signal(signal.SIGINT, _term_handler)
    signal.signal(signal.SIGTERM, _term_handler)

    # stream output of results
    if pargs.output:
        with open(pargs.output, 'w') as f:
            for line in dict_to_json_generator(dict_converter.convert()):
                f.write(line)
                f.write('\n')
    else:
        for output in dict_to_json_generator(dict_converter.convert()):
            print(output)

    # flush log handlers on exit; helps with console out with ctl-c
    for handler in logger.handlers:
        handler.flush()


if __name__ == "__main__":
    main()
