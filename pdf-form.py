#!/usr/bin/env python

import click

from core.cli import create, attach, fill


@click.group()
@click.help_option("--help", "-h", help="Show this message and exit.")
def cli():
    pass


cli.add_command(create)
cli.add_command(attach)
cli.add_command(fill)

if __name__ == "__main__":
    cli()
