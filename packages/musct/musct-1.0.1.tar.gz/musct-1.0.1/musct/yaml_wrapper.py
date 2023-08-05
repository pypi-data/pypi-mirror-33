from yaml import safe_load


def parse_text(yaml_data) -> object:
    obj = safe_load(yaml_data)
    return obj


def parse_file(file_path: str) -> object:
    with open(file_path, mode='r') as in_file:
        txt = in_file.read()
        obj = parse_text(txt)
        return obj
