import pathlib
from subprocess import getstatusoutput

import click
import toml

from .show import current
from .sources import sources


@click.group()
def cli():
    pass


@cli.command(short_help='List trusted sources')
def list():
    for name in sources:
        print(f'{sources[name].name:20}{sources[name].url}')


@cli.command(short_help='Show the current source')
def show():
    print(current())


@cli.command(short_help='Change the source with the name specificed')
@click.argument('name')
def use(name: str):
    if not pathlib.Path('Pipfile').exists():
        print("It's not a pipenv's directory")
        return
    if name not in sources:
        print(f'Unknown source name {name}')
        return
    config = toml.load('Pipfile')
    config['source'][0]['name'] = name
    config['source'][0]['url'] = sources[name].url
    toml.dump(config, open('Pipfile', 'w'))
    status, output = getstatusoutput('pipenv install --skip-lock')
    if status:
        print(output)
    else:
        status, output = getstatusoutput('pipenv lock')
        print(f"Changed Pipfile's source to {name}")


def main():
    cli.add_command(list)
    cli.add_command(show)
    cli()


if __name__ == '__main__':
    main()
