import os
from pytest_bdd import scenario, given, when, then, parsers
from pathlib import Path
from smol import smol


@scenario('first_run.feature', 'generate the default config')
def test_generate_config():
    pass


@given("there is no config directory at .smol")
def no_config(tmpdir: Path):
    smol.smol_path = tmpdir


@when("I launch smol")
def launch():
    smol.main()


@then(parsers.parse("the file {file_path} exists"))
def config_content(file_path):
    path = Path(f'{smol.smol_path}{os.sep}{file_path}')
    assert path.is_file(), f'Files: {os.listdir(smol.smol_path)} Path: {file_path}'

