from robocopy import Robocopy
from pathlib import Path
import yaml
import re
import click


@click.command()
@click.option('--config_path', required=True, type=Path)
def robocopy_yaml(config_path):
    if not isinstance(config_path, Path):
        config_path = Path(config_path)
    with open(config_path, 'r') as file:
        cfg = yaml.load(file, Loader=yaml.SafeLoader)
    defs = cfg['Defaults']

    for job in cfg['Jobs']:
        kwargs = defs.copy()
        kwargs.update(job)

        convert_paths(kwargs)

        log_folder = kwargs.pop('log_folder', None)
        if log_folder is not None and kwargs.get('log', None) is not None:
            kwargs['log'] = log_folder / kwargs['log']

        Robocopy(**kwargs)
    return

def convert_paths(dict):
    regex = re.compile(".*\\\\")
    for key, value in dict.items():
        if isinstance(value, str):
            if regex.match(value):
                dict[key] = Path(value)

if __name__ == '__main__':
    robocopy_yaml()