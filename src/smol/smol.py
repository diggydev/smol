from enum import Enum
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
        self.screen = Screen.MAIN_MENU
        self.screens = dict()
        self.post = None

    def update(self, user_input):
        if self.screen == Screen.MAIN_MENU:
            if user_input == 'new post from email':
                self.screen = Screen.EMAIL_MENU
        elif self.screen == Screen.EMAIL_MENU:
            self.post = Post(self.get_menu().get_item(user_input).email.get_payload())
            self.screen = Screen.DATE_MENU
        elif self.screen == Screen.DATE_MENU:
            self.post.date = user_input
            self.screen = Screen.TAG_MENU
        elif self.screen == Screen.TAG_MENU:
            for tag in user_input:
                self.post.add_tag(tag)
            self.write_post()

    def get_menu(self):
        if self.screen in self.screens:
            return self.screens[self.screen]
        if self.screen == Screen.EMAIL_MENU:
            menu = Menu()
            for mail in mbox(self.config['mail']['path']):
                if self.config['mail']['author_email'] == mail['From'][mail['From'].find('<')+1:-1].strip():
                    menu.append(EmailMenuItem(mail))
            self.screens[self.screen] = menu
        return self.screens[self.screen]

    def write_post(self):
        gemlog_root = self.working_dir.joinpath(self.config['gemlog']['path'])
        gemlog_root.mkdir()
        index = gemlog_root.joinpath('index.gmi')
        with open(index, 'w') as f:
            f.write('# The Index')
        gemlog_root.joinpath('posts').mkdir()
        post_path = gemlog_root.joinpath('posts', 'title.gmi')
        with open(post_path, 'w') as f:
            f.write(self.post.text)


class Screen(Enum):
    MAIN_MENU = 1
    EMAIL_MENU = 2
    DATE_MENU = 3
    TAG_MENU = 4


class Menu:
    def __init__(self, items=[]):
        self.items = items

    def append(self, item):
        self.items.append(item)

    def get_item(self, key):
        return self.items[key]

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


class Post:
    def __init__(self, text):
        self.text = text
        self.date = None
        self.tags = []

    def add_tag(self, tag):
        self.tags.append(tag)


if __name__ == '__main__':
    App(Path('.'))
