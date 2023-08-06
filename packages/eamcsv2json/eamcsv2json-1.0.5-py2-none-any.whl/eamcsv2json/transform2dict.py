import configparser

def parse_transform_config(config_file_name):
    return dict(_parse_transform_config(config_file_name))

def _parse_transform_config(config_file_name):
    config = configparser.ConfigParser()
    config.read(config_file_name)
    for raw_section_name in config.sections():
        config_values = config[raw_section_name]
        section_name = (
            raw_section_name.replace('-v02_fields', '')
            if '-v02_fields' in raw_section_name
            else raw_section_name
        )
        if 'FIELDS' in config_values:
            fields = [
                f.strip()
                for f in config[raw_section_name]['FIELDS'].split(',')
            ]
            yield (section_name, fields)
