from importlib import resources
import pytest
from pytest_bdd import scenario, given, when, then, parsers
from smol import smol
from pathlib import Path
import tests.resources


@pytest.fixture()
def app(tmp_path):
    return smol.App(tmp_path)


@scenario('generate_default_config.feature', 'Generate the default config')
def test_generate_config():
    pass


@scenario('posting_from_email.feature', 'View the list of available emails')
def test_view_email_list():
    pass


@scenario('posting_from_email.feature', 'Select an email to use as a new post')
def test_select_an_email():
    pass


def copy_resource_file_to_tmpdir(tmp_path, source):
    dest_path = tmp_path.joinpath(source)
    with open(dest_path, 'w') as f:
        config_text = resources.read_text('tests.resources', source)
        f.write(config_text)
    return dest_path


@given("the email inbox contains emails from the author")
def inbox_contains_author_emails(app, tmp_path):
    mail_path = copy_resource_file_to_tmpdir(tmp_path, 'mail')
    app.config['mail']['path'] = str(mail_path)


@given("the application is at the main menu")
def application_at_main_menu(app):
    app.screen = smol.Screen.MAIN_MENU


@when('the site administrator chooses "new post from email"')
def select_new_post_from_email(app):
    app.update('new post from email')


@then('the emails from the author are displayed')
def verify_emails_displayed(app):
    assert str(app.get_menu()) == 'Sun, 28 Jan 2024 10:17:52 GMT / My first post\n'


@given("the current directory does not contain the directory .smol")
def no_config():
    pass


@when("the application is started")
def launch(app):
    pass


@then(parsers.parse("the file {file_path} exists"))
def verify_file_exists(tmp_path, file_path):
    expected_file = tmp_path.joinpath(file_path)
    assert expected_file.exists(), f'{str(expected_file)} does not exist'


@given('the application is at the email selection menu')
def application_at_email_menu(app, tmp_path):
    inbox_contains_author_emails(app, tmp_path)
    select_new_post_from_email(app)


@when('the site administrator chooses an email')
def choose_an_email(app):
    app.update(0)


@when('the site administrator enters a publication date')
def choose_pub_date(app):
    app.update('2024-02-29')


@when('the site administrator chooses tags')
def choose_tags(app):
    app.update(['tag1', 'tag2'])


@then('the new post is created')
def verify_new_post(tmp_path, app):
    root = tmp_path.joinpath(app.config['gemlog']['path'])
    assert root.is_dir()
    index = root.joinpath('index.gmi')
    assert index.exists()
    post = root.joinpath('posts', 'title.gmi')
    assert post.exists()
