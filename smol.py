import curses
from mailbox import mbox
import os
import sys
import tomllib

version = '0.0.1'
banner = f'''
                                  ████ 
                                 ░░███ 
  █████  █████████████    ██████  ░███ 
 ███░░  ░░███░░███░░███  ███░░███ ░███ 
░░█████  ░███ ░███ ░███ ░███ ░███ ░███ 
 ░░░░███ ░███ ░███ ░███ ░███ ░███ ░███ 
 ██████  █████░███ █████░░██████  █████
░░░░░░  ░░░░░ ░░░ ░░░░░  ░░░░░░  ░░░░░ 

easy gemlog updates for people who are using ssh in a park
version {version}
'''


class Screen:
    def __init__(self, components):
        self.components = components

    def draw(self, w):
        for comp in self.components:
            comp.draw(w)

    def update(self, k):
        for comp in self.components:
            if type(comp) is Menu:
                comp.update(k)


class Label:
    def __init__(self, label):
        self.label = label

    def draw(self, w):
        for line in self.label.split('\n'):
            w.addstr(context['row'], 0, line)
            context['row'] += 1


class MenuOption:
    def __init__(self, content, operation):
        self.content = content
        self.operation = operation


class Menu:
    def __init__(self, options, label=lambda x: str(x), include_quit=False):
        self.options = options
        self.label = label
        self.include_quit = include_quit
        self.cursor = 0

    def draw(self, w):
        option_num = 1
        for option in self.options[self.cursor:min(self.cursor + 9, len(self.options))]:
            if type(option.content) is str:
                label = option.content
            else:
                label = self.label(option.content)
            w.addstr(context['row'], 0, f'[{option_num}] {label}')
            option_num += 1
            context['row'] += 1
        if self.cursor > 0:
            w.addstr(context['row'], 0, '[p] previous')
            context['row'] += 1
        if len(self.options) > (self.cursor + 9):
            w.addstr(context['row'], 0, '[n] next')
            context['row'] += 1
        if self.include_quit:
            w.addstr(context['row'], 0, '[q] quit')
            context['row'] += 1

    def update(self, k):
        if k.isdigit():
            k_num = int(k)
            if 0 < k_num <= len(self.options):
                context['selected'] = k_num
                self.options[k_num-1].operation()#recalculate index based on cursor
        elif k == 'q':
            quit_app()
        elif k == 'p':#and can go next...
            self.cursor = self.cursor - 10
        elif k == 'n':
            self.cursor = self.cursor + 10


def quit_app():
    context['run'] = False


def rebuild_gemini():
    context['active screen'] = screens['rebuild gemini']


def write_post():
    selected_mail = context['mails'][context['selected']-1]
    context['individual email'] = Screen([Label('str(selected_mail)')])
    context['active screen'] = screens['individual email']


def new_post_from_mail():
    options = []
    for mail in mbox(config['mail']['file']):
        if config['mail']['author_email'] == mail['From'][mail['From'].find('<')+1:-1].strip():
            options.append(MenuOption(mail, write_post))
    options.append(MenuOption('quit', quit_app))
    screens['email menu'] = Screen([Label('select email:'), Menu(options, label=lambda x: f'Subject: {x["Subject"]}')])
    context['active screen'] = screens['email menu']


def new_post_from_file():
    options = []
    with os.scandir(context['path']) as it:
        for entry in it:
            options.append(MenuOption(entry, write_post))
    options.append(MenuOption('quit', quit_app))
    screens['file menu'] = Screen([Label('select file:'), Menu(options, label=lambda x: f'{x.name}')])
    context['active screen'] = screens['file menu']


def update(w):
    k = w.getkey()
    context['active screen'].update(k)


def draw(w):
    w.clear()
    context['row'] = 0
    context['active screen'].draw(w)
    w.refresh()


def cli(w):
    while context['run']:
        draw(w)
        update(w)


if __name__ == '__main__':
    with open('/Users/briandurcan/Dropbox/sdf/smol/config.toml', 'rb') as f:
        config = tomllib.load(f)
    context = {}
    screens = dict()
    screens['main menu'] = Screen([
        Label(banner),
        Label('main menu:'),
        Menu([
            MenuOption('rebuild gemini', rebuild_gemini),
            MenuOption('new post from mail', new_post_from_mail),
            MenuOption('new post from file', new_post_from_file)],
            include_quit=True
        )
    ])
    screens['rebuild gemini'] = Screen([Label('Rebuilding...')])
    screens['email menu'] = None
    context['active screen'] = screens['main menu']
    context['path'] = '.'
    context['run'] = True
    curses.wrapper(cli)


# def addstr(w, str, mode=None):
#     if mode:
#         w.addstr(context['row'], 0, str, mode)
#     else:
#         w.addstr(context['row'], 0, str)
#     context['row'] += len(str.split('\n'))

#
#
#
#
# def draw_menu(w, items, label=lambda x: x):
#     index = 0
#     display_index = 0
#     next = False
#     for item in items:
#         index += 1
#         if index < context['cursor']:
#             continue
#         display_index += 1
#         if display_index == 10:
#             next = True
#             break
#         addstr(w, f'[{display_index}]\t{label(item)}')
#     if context['cursor'] > 1:
#         addstr(w, '[p]\tprevious')
#     else:
#         context['row'] += 1
#     if next:
#         addstr(w, '[n]\tnext')
#     else:
#         context['row'] += 1
#
#
# def label_file(f):
#     mode = None
#     if f.is_dir():
#         return f'(dir) {f.name}'
#     return f.name
#
#
# def draw(w):
#     w.clear()
#     context['row'] = 0
#     if context['stage'] == 'main menu':
#         addstr(w, banner)
#         draw_menu(w, ['new post from file', 'new post from mail', 'refresh an edited post'])
#     if context['stage'] == 'file selection':
#         addstr(w, 'file selection:')
#         draw_menu(w, context['files'], label_file)
#     addstr(w, '[q]\tquit')
#     w.refresh()
#
#
# def update(w):
#     k = w.getkey()
#     if k == 'q':
#         context['run'] = False
#     elif context['stage'] == 'main menu':
#         if k == '1':
#             context['stage'] = 'file selection'
#             ls(context['path'])
#     elif context['stage'] == 'file selection':
#         if context['cursor'] > 1 and k == 'p':
#             context['cursor'] = context['cursor'] - 1
#         if (context['cursor'] + 9) < len(context['files']) and k == 'n':
#             context['cursor'] += 1
#         if k.isdigit():
#             if context['files'][int(k) - context['cursor']].is_dir():
#                 context['path'] = f"{context['path']}/{context['files'][int(k) - context['cursor']].name}"
#                 ls(context['path'])
#
#
#     if k == 'q':
#         context['run'] = False
#     elif context['stage'] == 'main menu':
#         if k == '1':
#             context['stage'] = 'file selection'
#             ls(context['path'])
#     elif context['stage'] == 'file selection':
#         if context['cursor'] > 1 and k == 'p':
#             context['cursor'] = context['cursor'] - 1
#         if (context['cursor'] + 9) < len(context['files']) and k == 'n':
#             context['cursor'] += 1
#         if k.isdigit():
#             if context['files'][int(k) - context['cursor']].is_dir():
#                 context['path'] = f"{context['path']}/{context['files'][int(k) - context['cursor']].name}"
#                 ls(context['path'])
