"""dragonfly-radiance commands which will be added to the dragonfly CLI."""
import click

from dragonfly.cli import main
from .translate import translate


# command group for all radiance extension commands.
@click.group(help='dragonfly radiance commands.')
def radiance():
    pass


# add sub-commands for radiance
radiance.add_command(translate)

# add radiance sub-commands to dragonfly CLI
main.add_command(radiance)
