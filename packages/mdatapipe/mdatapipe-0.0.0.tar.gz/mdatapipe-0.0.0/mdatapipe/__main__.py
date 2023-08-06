from __future__ import print_function
import click
from mdatapipe import commands
# from mdatapipe.profile import init_yappi


@click.group()
def cli():
    pass


cli.add_command(commands.run)


def main():
    cli()


if __name__ == '__main__':
    # init_yappi()
    main()
