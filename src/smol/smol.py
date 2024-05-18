from enum import Enum
from pathlib import Path
import importlib
import importlib.resources
import configparser
from mailbox import mbox
import src.smol.resources


class App:
    def __init__(self, working_dir):
        self.running = True
        self.working_dir = working_dir
        self.config_dir = working_dir.joinpath('.smol')
        self.config_dir.mkdir(exist_ok=True)
        self.config_path = self.config_dir.joinpath('config.ini')
        self.template_path = self.config_dir.joinpath('template.gmi')
        if self.config_path.exists():
            with open(self.config_path, 'r') as f:
                config_text = f.read()
            with open(self.template_path, 'r') as f:
                self.template = f.read()
        else:
            with open(self.config_path, 'w') as f:
                config_text = importlib.resources.read_text('src.smol.resources', 'config.ini')
                f.write(config_text)
            with open(self.template_path, 'w') as f:
                self.template = importlib.resources.read_text('src.smol.resources', 'template.gmi')
                f.write(self.template)
        self.config = configparser.ConfigParser()
        self.config.read_string(config_text)
        self.screen = Screen.MAIN_MENU
        self.screens = dict()
        self.post = None

    def update(self, user_input):
        if user_input == 'quit':
            self.running = False
        if self.screen == Screen.MAIN_MENU:
            if user_input == 'new post from email':
                self.screen = Screen.EMAIL_MENU
        elif self.screen == Screen.EMAIL_MENU:
            self.post = Post(user_input.email.get_payload())
            self.screen = Screen.DATE_MENU
        elif self.screen == Screen.DATE_MENU:
            self.post.date = user_input
            self.post.year = user_input[:4]
            self.screen = Screen.SLUG_MENU
        elif self.screen == Screen.SLUG_MENU:
            self.post.slug = user_input
            self.screen = Screen.TAG_MENU
        elif self.screen == Screen.TAG_MENU:
            if user_input.startswith('[ ] '):
                self.post.add_tag(user_input.split('[ ] ')[1])
                self.screens.pop(Screen.TAG_MENU, None)
            elif user_input.startswith('[x] '):
                self.post.remove_tag(user_input.split('[x] ')[1])
                self.screens.pop(Screen.TAG_MENU, None)
            elif user_input == 'continue with selected tags':
                self.write_post()
                self.running = False
            else:
                self.config['gemlog']['tags'] = f'{self.config["gemlog"]["tags"]},{user_input}'
                with open(self.config_path, 'w') as configfile:
                    self.config.write(configfile)
                self.post.add_tag(user_input)
                self.screens.pop(Screen.TAG_MENU, None)

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
        elif self.screen == Screen.SLUG_MENU:
            self.screens[Screen.SLUG_MENU] = Menu('Enter a slug (format: my-great-post)')
        elif self.screen == Screen.TAG_MENU:
            self.screens[Screen.TAG_MENU] = Menu('Toggle existing tags or type a new one:')
            for tag in self.config['gemlog']['tags'].split(','):
                if tag in self.post.tags:
                    checkbox_and_tag = f'[x] {tag}'
                else:
                    checkbox_and_tag = f'[ ] {tag}'
                self.screens[Screen.TAG_MENU].append(checkbox_and_tag)
            self.screens[Screen.TAG_MENU].append('continue with selected tags')
        return self.screens[self.screen]

    def write_post(self):
        post_csv = self.config_dir.joinpath('posts.csv')
        with open(post_csv, 'a') as f:
            f.write(f'{self.post.get_record()}\n')
        gemlog_root = self.working_dir.joinpath(self.config['gemlog']['path'])
        gemlog_root.mkdir(exist_ok=True)
        index = gemlog_root.joinpath('index.gmi')
        with open(index, 'w') as f:
            f.write(self.template)
            # TODO update index, latest posts, tag count etc
        gemlog_root.joinpath('posts').mkdir(exist_ok=True)
        gemlog_root.joinpath('posts').joinpath(self.post.year).mkdir(exist_ok=True)
        # TODO update index file in year dir
        post_path = gemlog_root.joinpath('posts', self.post.year, f'{self.post.get_filename()}')
        with open(post_path, 'w') as f:
            f.write(self.post.text)
            # TODO write post footer
        gemlog_root.joinpath('tags').mkdir(exist_ok=True)
        for tag in self.post.tags:
            tag_path = gemlog_root.joinpath('tags', f'{tag}.gmi')
            # TODO update tag file
            # TODO update index file in tag dir


class Screen(Enum):
    MAIN_MENU = 1
    EMAIL_MENU = 2
    DATE_MENU = 3
    SLUG_MENU = 4
    TAG_MENU = 5


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
        else:
            return key

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
        self.slug = None
        self.tags = []

    def add_tag(self, tag):
        self.tags.append(tag)

    def remove_tag(self, tag):
        self.tags.remove(tag)

    def get_title(self):
        for line in self.text.split('\n'):
            if line.startswith('# '):
                return line[2:].strip()
        return None

    def get_filename(self):
        return f'{self.date[5:]}-{self.slug}.gmi'

    def get_record(self):
        return f'{self.year}|{self.get_filename()}|{self.get_title()}|{",".join(self.tags)}'


def update(app: App):
    k = input()
    app.update(app.get_menu().get_item(k))


def draw(app: App):
    app.get_menu().draw()


def ui(app: App):
    while app.running:
        draw(app)
        update(app)


if __name__ == '__main__':
    ui(App(Path('.')))
