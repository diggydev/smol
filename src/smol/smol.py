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
            print('user_input')
            print(user_input)
            self.post = Post(user_input.email.get_payload())
            self.screen = Screen.DATE_MENU
        elif self.screen == Screen.DATE_MENU:
            self.post.date = user_input
            self.post.year = user_input[:4]
            self.screen = Screen.TAG_MENU
        elif self.screen == Screen.TAG_MENU:
            for tag in user_input:
                self.post.add_tag(tag)
            self.write_post()

    def get_menu(self):
        if self.screen in self.screens:
            return self.screens[self.screen]
        elif self.screen == Screen.MAIN_MENU:
            self.screens[Screen.MAIN_MENU] = Menu('Select an operation')
            self.screens[Screen.MAIN_MENU].append('new post from email')
        elif self.screen == Screen.EMAIL_MENU:
            self.screens[Screen.EMAIL_MENU] = Menu('Select an email')
            for mail in mbox(self.config['mail']['path']):
                if self.config['mail']['author_email'] == mail['From'][mail['From'].find('<')+1:-1].strip():
                    self.screens[Screen.EMAIL_MENU].append(EmailMenuItem(mail))
        elif self.screen == Screen.DATE_MENU:
            self.screens[Screen.DATE_MENU] = Menu('Enter a date (format: 2024-01-31)')
        elif self.screen == Screen.TAG_MENU:
            self.screens[Screen.TAG_MENU] = Menu('Choose an existing tag or add a new one:')
            self.screens[Screen.TAG_MENU].append('general')
        return self.screens[self.screen]

    def write_post(self):
        gemlog_root = self.working_dir.joinpath(self.config['gemlog']['path'])
        gemlog_root.mkdir()
        index = gemlog_root.joinpath('index.gmi')
        with open(index, 'w') as f:
            f.write('# The Index')
        gemlog_root.joinpath('posts').mkdir()
        gemlog_root.joinpath('posts').joinpath(self.post.year).mkdir()
        post_path = gemlog_root.joinpath('posts', self.post.year, f'{self.post.year[5:]}-title.gmi')
        with open(post_path, 'w') as f:
            f.write(self.post.text)


class Screen(Enum):
    MAIN_MENU = 1
    EMAIL_MENU = 2
    DATE_MENU = 3
    TAG_MENU = 4


class Menu:
    def __init__(self, title):
        self.items = []
        self.title = title

    def append(self, item):
        self.items.append(item)

    def get_item(self, key):
        if key.isdigit():
            k_num = int(key)
            if 0 < k_num <= len(self.items):
                return self.items[k_num - 1]
        elif key == 'q':
            return 'quit'

    def draw(self):
        print(self.title)
        for row in range(0, len(self.items)):
            print(f'{row + 1}. {str(self.items[row])}')
        print('q. quit')


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
        self.year = None
        self.tags = []

    def add_tag(self, tag):
        self.tags.append(tag)


def update(app: App):
    k = input()
    app.update(app.get_menu().get_item(k))


def draw(app: App):
    app.get_menu().draw()


def ui(app: App):
    while True:
        draw(app)
        update(app)


if __name__ == '__main__':
    ui(App(Path('.')))
