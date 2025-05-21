"""dragonfly radiance translation commands."""
import click
import sys
import os
import logging
import zipfile

from ladybug.futil import unzip_file
from ladybug.commandutil import process_content_to_output
from dragonfly.model import Model


_logger = logging.getLogger(__name__)


@click.group(help='Commands for translating Dragonfly files to/from Radiance.')
def translate():
    pass


@translate.command('model-to-rad-folder')
@click.argument('model-file', type=click.Path(
    exists=True, file_okay=True, dir_okay=False, resolve_path=True))
@click.option(
    '--multiplier/--full-geometry', ' /-fg', help='Flag to note if the '
    'multipliers on each Building story will be passed along to the '
    'generated Honeybee Room objects or if full geometry objects should be '
    'written for each story in the building.', default=True, show_default=True
)
@click.option(
    '--plenum/--no-plenum', '-p/-np', help='Flag to indicate whether '
    'ceiling/floor plenum depths assigned to Room2Ds should generate '
    'distinct 3D Rooms in the translation.', default=True, show_default=True
)
@click.option(
    '--no-ceil-adjacency/--ceil-adjacency', ' /-a', help='Flag to indicate '
    'whether adjacencies should be solved between interior stories when '
    'Room2Ds perfectly match one another in their floor plate. This ensures '
    'that Surface boundary conditions are used instead of Adiabatic ones. '
    'Note that this input has no effect when the object-per-model is Story.',
    default=True, show_default=True
)
@click.option(
    '--folder', help='Folder into which the model Radiance '
    'folders will be written. If None, the files will be output in the '
    'same location as the model_file.', default=None, show_default=True
)
@click.option(
    '--grid', '-g', multiple=True, help='List of grids to be included in folder. By '
    'default all the sensor grids will be exported. You can also use wildcards here. '
    'For instance first_floor_* will select all the sensor grids that has an identifier '
    'that starts with first_floor. To filter based on group_identifier use /. For '
    'example daylight/* will select all the grids that belong to daylight group.')
@click.option(
    '--view', '-v', multiple=True, help='List of views to be included in folder. By '
    'default all the views will be exported. You can also use wildcards to filter '
    'multiple views. For instance first_floor_* will select all the views that has an '
    'identifier that starts with first_floor. To filter based on group_identifier use '
    '/. For example daylight/* will select all the views that belong to daylight group.')
@click.option(
    '--full-match/--no-full-match', help='Flag to note whether the grids and'
    'views should be filtered by their identifiers as full matches. Setting '
    'this to True indicates that wildcard symbols will not be used in the '
    'filtering of grids and views.', default=False, show_default=True)
@click.option(
    '--config-file', '-c', help='An optional config file path to modify the '
    'default folder names. If None, folder.cfg in honeybee-radiance-folder '
    'will be used.', default=None, show_default=True)
@click.option(
    '--minimal/--maximal', '-min/-max', help='Flag to note whether the radiance strings '
    'should be written in a minimal format (with spaces instead of line '
    'breaks).', default=False, show_default=True)
@click.option(
    '--no-grid-check/--grid-check', ' /-gc', help='Flag to note whether the '
    'model should be checked for the presence of sensor grids. If the check '
    'is set and the model has no grids, an explicit error will be raised.',
    default=True, show_default=True)
@click.option(
    '--no-view-check/--view-check', ' /-vc', help='Flag to note whether the '
    'model should be checked for the presence of views. If the check '
    'is set and the model has no views, an explicit error will be raised.',
    default=True, show_default=True)
@click.option(
    '--create-grids', '-cg', default=False, show_default=True, is_flag=True,
    help='Flag to note whether sensor grids should be created if none exists. '
    'This will only create sensor grids for rooms if there are no sensor grids '
    'in the model.'
)
@click.option(
    '--log-file', help='Optional log file to output the path of the radiance '
    'folder generated from the model. By default this will be printed '
    'to stdout', type=click.File('w'), default='-')
def model_to_rad_folder_cli(
    model_file, multiplier, plenum, no_ceil_adjacency,
    folder, view, grid, full_match, config_file, minimal,
    no_grid_check, no_view_check, create_grids, log_file
):
    """Translate a Model file into a Radiance Folder.

    \b
    Args:
        model_file: Full path to a Model JSON file (HBJSON) or a Model
            pkl (HBpkl) file. This can also be a zipped version of a Radiance
            folder, in which case this command will simply unzip the file
            into the --folder and no other operations will be performed on it.
    """
    try:
        full_geometry = not multiplier
        no_plenum = not plenum
        ceil_adjacency = not no_ceil_adjacency
        grid_check = not no_grid_check
        view_check = not no_view_check
        model_to_rad_folder(
            model_file, full_geometry, no_plenum, ceil_adjacency,
            folder, view, grid, full_match, config_file,
            minimal, grid_check, view_check, create_grids, log_file)
    except Exception as e:
        _logger.exception('Model translation failed.\n{}'.format(e))
        sys.exit(1)
    else:
        sys.exit(0)


def model_to_rad_folder(
    model_file, full_geometry=False, no_plenum=False, ceil_adjacency=False,
    folder=None, view=None, grid=None, full_match=False, config_file=None,
    minimal=False, grid_check=False, view_check=False, create_grids=False, log_file=None,
    multiplier=True, plenum=True, no_ceil_adjacency=True,
    no_full_match=True, maximal=True, no_grid_check=False, no_view_check=False,
):
    """Translate a Model file into a Radiance Folder.

    Args:
        model_file: Full path to a Model JSON file (HBJSON) or a Model
            pkl (HBpkl) file. This can also be a zipped version of a Radiance
            folder, in which case this command will simply unzip the file
            into the --folder and no other operations will be performed on it.
        folder: Folder into which the model Radiance folders will be written.
            If None, the files will be output in the same location as the model_file.
        view: List of grids to be included in folder. By default all the sensor
            grids will be exported. You can also use wildcards here. For instance
            first_floor_* will select all the sensor grids that has an identifier
            that starts with first_floor. To filter based on group_identifier
            use /. For example daylight/* will select all the grids that belong
            to daylight group. (Default: None).
        grid: List of views to be included in folder. By default all the views
            will be exported. You can also use wildcards to filter multiple views.
            For instance first_floor_* will select all the views that has an
            identifier that starts with first_floor. To filter based on
            group_identifier use /. For example daylight/* will select all the
            views that belong to daylight group. (Default: None).
        full_match: Boolean to note whether the grids and views should be
            filtered by their identifiers as full matches. Setting this to
            True indicates that wildcard symbols will not be used in the
            filtering of grids and views. (Default: False).
        config_file: An optional config file path to modify the default folder
            names. If None, folder.cfg in honeybee-radiance-folder will be used.
        minimal: Boolean to note whether the radiance strings should be written
            in a minimal format (with spaces instead of line breaks). (Default: False).
        grid_check: Boolean to note whether the model should be checked for the
            presence of sensor grids. If the check is set and the model has no
            grids, an explicit error will be raised. (Default: False).
        view_check: Boolean to note whether the model should be checked for the
            presence of views. If the check is set and the model has no views,
            an explicit error will be raised. (Default: False).
        log_file: Optional log file to output the path of the radiance folder
            generated from the model. If None, it will be returned from this method.
    """
    # set the default folder if it's not specified
    if folder is None:
        folder = os.path.dirname(os.path.abspath(model_file))

    # first check to see if the model_file is a zipped radiance folder
    if zipfile.is_zipfile(model_file):
        unzip_file(model_file, folder)
        if log_file is None:
            return folder
        else:
            log_file.write(folder)
    else:
        # re-serialize the Dragonfly Model
        model = Model.from_file(model_file)

        # convert Dragonfly Model to Honeybee
        multiplier = not full_geometry
        hb_models = model.to_honeybee(
            object_per_model='District', use_multiplier=multiplier,
            exclude_plenums=no_plenum, solve_ceiling_adjacencies=ceil_adjacency)
        model = hb_models[0]

        if create_grids:
            if not model.properties.radiance.has_sensor_grids:
                sensor_grids = []

                unit_conversion = {
                    'Meters': 1,
                    'Millimeters': 0.001,
                    'Centimeters': 0.01,
                    'Feet': 0.3048,
                    'Inches': 0.0254
                }

                if model.units in ['Meters', 'Millimeters', 'Centimeters']:
                    grid_size = 0.5 / unit_conversion[model.units]
                    offset = 0.76 / unit_conversion[model.units]
                    wall_offset = 0.3 / unit_conversion[model.units]
                else:  # assume IP units
                    grid_size = 2 * 0.3048 / unit_conversion[model.units]
                    offset = 2.5 * 0.3048 / unit_conversion[model.units]
                    wall_offset = 1 * 0.3048 / unit_conversion[model.units]

                for room in model.rooms:
                    sensor_grids.append(room.properties.radiance.generate_sensor_grid(
                        grid_size, offset=offset, wall_offset=wall_offset))
                model.properties.radiance.sensor_grids = sensor_grids

        if grid_check and len(model.properties.radiance.sensor_grids) == 0:
            raise ValueError('Model contains no sensor grids. These are required.')
        if view_check and len(model.properties.radiance.views) == 0:
            raise ValueError('Model contains no views These are required.')

        # translate the model to a radiance folder
        rad_fold = model.to.rad_folder(
            model, folder, config_file, minimal, views=view, grids=grid,
            full_match=full_match
        )

        if log_file is None:
            return rad_fold
        else:
            log_file.write(rad_fold)


@translate.command('model-to-rad')
@click.argument('model-file', type=click.Path(
    exists=True, file_okay=True, dir_okay=False, resolve_path=True))
@click.option('--multiplier/--full-geometry', ' /-fg', help='Flag to note if the '
              'multipliers on each Building story will be passed along to the '
              'generated Honeybee Room objects or if full geometry objects should be '
              'written for each story in the building.', default=True, show_default=True)
@click.option('--plenum/--no-plenum', '-p/-np', help='Flag to indicate whether '
              'ceiling/floor plenum depths assigned to Room2Ds should generate '
              'distinct 3D Rooms in the translation.', default=True, show_default=True)
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
def model_to_rad_cli(model_file, multiplier, plenum, no_ceil_adjacency,
                     blk, minimal, output_file):
    """Translate a Dragonfly Model file to a Radiance string.

    The resulting string will include all geometry and all modifiers.

    \b
    Args:
        model_file: Full path to a Dragonfly Model JSON or Pkl file.
    """
    try:
        full_geometry = not multiplier
        no_plenum = not plenum
        ceil_adjacency = not no_ceil_adjacency
        model_to_rad(model_file, full_geometry, no_plenum, ceil_adjacency,
                     blk, minimal, output_file)
    except Exception as e:
        _logger.exception('Model translation failed.\n{}\n'.format(e))
        sys.exit(1)
    else:
        sys.exit(0)


def model_to_rad(
    model_file, full_geometry=False, no_plenum=False, ceil_adjacency=False,
    blk=False, minimal=False, output_file=None,
    multiplier=True, plenum=True, no_ceil_adjacency=True, maximal=True
):
    """Translate a Model file to a Radiance string.

    The resulting strings will include all geometry (Rooms, Faces, Shades, Apertures,
    Doors) and all modifiers. However, it does not include any states for dynamic
    geometry and will only write the default state for each dynamic object. To
    correctly account for dynamic objects, model-to-rad-folder should be used.

    Args:
        model_file: Full path to a Model JSON file (HBJSON) or a Model pkl (HBpkl) file.
        full_geometry: Boolean to note if the multipliers on each Building story
            will be passed along to the generated Honeybee Room objects or if
            full geometry objects should be written for each story in the
            building. (Default: False).
        no_plenum: Boolean to indicate whether ceiling/floor plenum depths
            assigned to Room2Ds should generate distinct 3D Rooms in the
            translation. (Default: False).
        ceil_adjacency: Boolean to indicate whether adjacencies should be solved
            between interior stories when Room2Ds perfectly match one another
            in their floor plate. This ensures that Surface boundary conditions
            are used instead of Adiabatic ones. Note that this input has no
            effect when the object-per-model is Story. (Default: False).
        blk: Boolean to note whether the "blacked out" version of the geometry
            should be output, which is useful for direct studies and isolation
            studies of individual apertures.
        minimal: Boolean to note whether the radiance strings should be written
            in a minimal format (with spaces instead of line breaks).
        output_file: Optional RAD file to output the RAD string of the translation.
            If None, the string will be returned from this method. (Default: None).
    """
    # re-serialize the Dragonfly Model
    model = Model.from_file(model_file)

    # convert Dragonfly Model to Honeybee
    multiplier = not full_geometry
    hb_models = model.to_honeybee(
        object_per_model='District', use_multiplier=multiplier,
        exclude_plenums=no_plenum, solve_ceiling_adjacencies=ceil_adjacency)
    hb_model = hb_models[0]

    # create the strings for modifiers and geometry
    model_str, modifier_str = hb_model.to.rad(hb_model, blk, minimal)
    rad_str_list = ['# ========  MODEL MODIFIERS ========', modifier_str,
                    '# ========  MODEL GEOMETRY ========', model_str]
    rad_str = '\n\n'.join(rad_str_list)

    # write out the rad string
    return process_content_to_output(rad_str, output_file)
