"""Test cli translate module."""
import os
from click.testing import CliRunner
from ladybug.futil import nukedir

from dragonfly_radiance.cli.translate import model_to_rad_folder_cli, model_to_rad_cli


def test_model_to_rad_folder():
    runner = CliRunner()
    input_hb_model = './tests/assets/model_complete_simple.dfjson'
    output_hb_model = './tests/assets/model'

    result = runner.invoke(model_to_rad_folder_cli, [input_hb_model, '--folder', output_hb_model])
    assert result.exit_code == 0
    assert os.path.isdir(output_hb_model)
    nukedir(output_hb_model, True)


def test_model_to_rad():
    runner = CliRunner()
    input_df_model = './tests/assets/model_complete_simple.dfjson'

    output_rad = './tests/assets/in.rad'
    result = runner.invoke(model_to_rad_cli, [input_df_model, '--output-file', output_rad])
    assert result.exit_code == 0

    assert os.path.isfile(output_rad)
    os.remove(output_rad)
