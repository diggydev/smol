from pathlib import Path
import importlib
import configparser
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
        self.screen = 'main'

    def update(self, user_input):
        if user_input == 'new post from email':
            self.screen = 'Sun, 28 Jan 2024 00:17:52 GMT / My first post'


if __name__ == '__main__':
    App(Path('.'))
