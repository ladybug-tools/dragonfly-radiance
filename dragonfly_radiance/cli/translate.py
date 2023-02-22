"""dragonfly radiance translation commands."""
import click
import sys
import logging

from dragonfly.model import Model


_logger = logging.getLogger(__name__)


@click.group(help='Commands for translating Dragonfly files to/from Radiance.')
def translate():
    pass


@translate.command('model-to-rad')
@click.argument('model-file', type=click.Path(
    exists=True, file_okay=True, dir_okay=False, resolve_path=True))
@click.option('--multiplier/--full-geometry', ' /-fg', help='Flag to note if the '
              'multipliers on each Building story will be passed along to the '
              'generated Honeybee Room objects or if full geometry objects should be '
              'written for each story in the building.', default=True, show_default=True)
@click.option('--no-plenum/--plenum', ' /-p', help='Flag to indicate whether '
              'ceiling/floor plenums should be auto-generated for the Rooms.',
              default=True, show_default=True)
@click.option('--no-ceil-adjacency/--ceil-adjacency', ' /-a', help='Flag to indicate '
              'whether adjacencies should be solved between interior stories when '
              'Room2Ds perfectly match one another in their floor plate. This ensures '
              'that Surface boundary conditions are used instead of Adiabatic ones. '
              'Note that this input has no effect when the object-per-model is Story.',
              default=True, show_default=True)
@click.option('--blk', help='Boolean to note whether the "blacked out" version '
              'of the geometry should be output, which is useful for direct studies '
              'and isolation studies of individual apertures.',
              default=False, show_default=True)
@click.option('--minimal/--maximal', help='Flag to note whether the radiance strings '
              'should be written in a minimal format (with spaces instead of line '
              'breaks).', default=False, show_default=True)
@click.option('--output-file', '-f', help='Optional Rad file to output the Rad string '
              'of the translation. By default this will be printed out to stdout',
              type=click.File('w'), default='-', show_default=True)
def model_to_rad(model_file, multiplier, no_plenum, no_ceil_adjacency,
                 blk, minimal, output_file):
    """Translate a Dragonfly Model file to a Radiance string.

    The resulting string will include all geometry and all modifiers.

    \b
    Args:
        model_file: Full path to a Dragonfly Model JSON or Pkl file.
    """
    try:
        # re-serialize the Dragonfly Model
        model = Model.from_file(model_file)

        # convert Dragonfly Model to Honeybee
        add_plenum = not no_plenum
        ceil_adjacency = not no_ceil_adjacency
        hb_models = model.to_honeybee(
            object_per_model='District', use_multiplier=multiplier,
            add_plenum=add_plenum, solve_ceiling_adjacencies=ceil_adjacency)
        hb_model = hb_models[0]

        # create the strings for modifiers and geometry
        model_str, modifier_str = hb_model.to.rad(hb_model, blk, minimal)
        rad_str_list = ['# ========  MODEL MODIFIERS ========', modifier_str,
                        '# ========  MODEL GEOMETRY ========', model_str]
        rad_str = '\n\n'.join(rad_str_list)

        # write out the Rad file
        output_file.write(rad_str)
    except Exception as e:
        _logger.exception('Model translation failed.\n{}\n'.format(e))
        sys.exit(1)
    else:
        sys.exit(0)
