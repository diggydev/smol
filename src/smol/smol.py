import curses
from enum import Enum
from pathlib import Path
import importlib
import importlib.resources
import configparser
from mailbox import mbox
import src.smol.resources


class App:
    def __init__(self, working_dir):
        self.working_dir = working_dir
        if not working_dir.joinpath('.smol').exists():
            working_dir.joinpath('.smol').mkdir()
        config_path = working_dir.joinpath('.smol', 'config.ini')
        if config_path.exists():
            with open(config_path, 'r') as f:
                config_text = f.read()
        else:
            with open(config_path, 'w') as f:
                config_text = importlib.resources.read_text('src.smol.resources', 'config.ini')
                f.write(config_text)
        self.config = configparser.ConfigParser()
        self.config.read_string(config_text)
        self.screen = Screen.MAIN_MENU
        self.screens = dict()
        self.post = None

    def update(self, user_input):
        if user_input == 'quit':
            exit(0)
        if self.screen == Screen.MAIN_MENU:
            if user_input == 'new post from email':
                self.screen = Screen.EMAIL_MENU
        elif self.screen == Screen.EMAIL_MENU:
            self.post = Post(user_input.email.get_payload())
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
        elif self.screen == Screen.MAIN_MENU:
            self.screens[Screen.MAIN_MENU] = Menu()
            self.screens[Screen.MAIN_MENU].append('new post from email')
        elif self.screen == Screen.EMAIL_MENU:
            self.screens[Screen.EMAIL_MENU] = Menu()
            for mail in mbox(self.config['mail']['path']):
                if self.config['mail']['author_email'] == mail['From'][mail['From'].find('<')+1:-1].strip():
                    self.screens[Screen.EMAIL_MENU].append(EmailMenuItem(mail))
        elif self.screen == Screen.DATE_MENU:
            self.screens[Screen.DATE_MENU] = Menu()
            self.screens[Screen.DATE_MENU].append('2024-03-27')
        elif self.screen == Screen.TAG_MENU:
            self.screens[Screen.TAG_MENU] = Menu()
            self.screens[Screen.TAG_MENU].append('general')
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
    def __init__(self):
        self.items = []

    def append(self, item):
        self.items.append(item)

    def get_item(self, key):
        if key.isdigit():
            k_num = int(key)
            if 0 < k_num <= len(self.items):
                return self.items[k_num - 1]
        elif key == 'q':
            return 'quit'

    # def __str__(self):
    #     menu_str = ''
    #     for item in self.items:
    #         menu_str += f'{str(item)}\n'
    #     return menu_str

    def draw(self, w):
        for row in range(0, len(self.items)):
            w.addstr(row, 0, f'{row + 1}. {str(self.items[row])}')
            row += 1
        w.addstr(row, 0, 'q. quit')

    # def update(self, k):
    #     if k.isdigit():
    #         k_num = int(k)
    #         if 0 < k_num <= len(self.items):
    #             self.items[k_num - 1].operation()
    #     elif k == 'q':
    #         exit(0)


class MenuItem:
    def __init__(self, label, operation):
        self.label = label
        self.operation = operation

    def __str__(self):
        return self.label


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


def update(w, app: App):
    k = w.getkey()
    app.update(app.get_menu().get_item(k))
    # app.get_menu().update(k)


def draw(w, app):
    w.clear()
    app.get_menu().draw(w)
    w.refresh()


def cli(w, app):
    while True:
        draw(w, app)
        update(w, app)


if __name__ == '__main__':
    curses.wrapper(cli, App(Path('.')))
