import os
from pathlib import Path

smol_path = None


def main():
    smol_path.mkdir('.smol')
    with open(f'{smol_path}{os.sep}.smol{os.sep}config.toml', 'w') as f:
        f.write('hello')


if __name__ == '__main__':
    smol_path = Path('.')
    main()
