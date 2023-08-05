import sys
import click
from findreplace.core import findreplace

@click.group()
def cli():
    """findreplace
    """
    if sys.version_info[0] == 2:
        print("Current environment is Python 2.")
        print("Please use a Python 3 virtualenv")
        raise SystemExit


@cli.command('replace')
@click.argument('base_dir', required=True)
@click.argument('find_val', required=True)
@click.argument('replace_val', required=True)
def replace(base_dir, find_val, replace_val):
    find_replace_dict = {}
    find_replace_dict[find_val] = replace_val
    findreplace(base_dir, find_replace_dict)


def main():
    cli()


if __name__ == '__main__':
    main()
