from pathlib import Path
import importlib
import configparser
from mailbox import mbox
import src.smol.resources


class App:
    def __init__(self, working_dir):
        self.working_dir = working_dir
        working_dir.joinpath('.smol').mkdir()
        config_path = working_dir.joinpath('.smol', 'config.ini')
        with open(config_path, 'w') as f:
            config_text = importlib.resources.read_text('src.smol.resources', 'config.ini')
            f.write(config_text)
            self.config = configparser.ConfigParser()
            self.config.read_string(config_text)
        self.screen = 'main menu'
        self.email_menu = None

    def update(self, user_input):
        if user_input == 'new post from email':
            self.screen = self.get_email_menu()

    def get_email_menu(self):
        if not self.email_menu:
            self.email_menu = Menu()
            for mail in mbox(self.config['mail']['path']):
                if self.config['mail']['author_email'] == mail['From'][mail['From'].find('<')+1:-1].strip():
                    self.email_menu.append(EmailMenuItem(mail))
        return self.email_menu


class Menu:
    def __init__(self, items=[]):
        self.items = items

    def append(self, item):
        self.items.append(item)

    def __str__(self):
        menu_str = ''
        for item in self.items:
            menu_str += f'{str(item)}\n'
        return menu_str


class EmailMenuItem:
    def __init__(self, email):
        self.email = email

    def __str__(self):
        return f'{self.email["Date"]} / {self.email["Subject"]}'


if __name__ == '__main__':
    App(Path('.'))
