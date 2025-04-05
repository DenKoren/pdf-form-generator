#!/usr/bin/env python

import click

from core.cli import attach, fill


@click.group()
def cli():
    pass

cli.add_command(attach)
cli.add_command(fill)

if __name__ == "__main__":
    cli()
