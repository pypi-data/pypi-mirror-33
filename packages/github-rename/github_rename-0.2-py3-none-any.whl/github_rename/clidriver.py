import os
import re

import click

VERSION = '0.2'
PROG_NAME = 'GitHub-rename'


def github_rename(name_before, name_after, file_name, bak=True):
    if not os.path.isfile(file_name):
        print(f'{file_name} does not exist.\n')
        return

    if name_before:
        pattern = re.compile(f'https://github.com/{name_before}/')
    else:
        # This is dangerous because you may have others' submodule.
        pattern = re.compile(r'https://github.com/[a-zA-Z0-9_]+/')

    with open(file_name, 'r') as f:
        lines = f.readlines()
    if bak:
        with open(file_name + '.bak', 'w') as f:
            for l in lines:
                f.write(l)

    with open(file_name, 'w') as f:
        print(f'Searching for {file_name}...\nReplaced line(s):\n')
        matched = 0
        for l in lines:
            if pattern.search(l):
                matched += 1
                new_l = pattern.sub(f'https://github.com/{name_after}/', l)
                f.write(new_l)
                print(l, end='')
                print('->', new_l)
            else:
                f.write(l)
        print(f'\nMatched and replaced {matched} time(s).\n')


@click.command()
@click.option('f', '-f', '--from', prompt='Old username', help='Name to change from.')
@click.option('t', '-t', '--to', prompt='New username', help='Name to change to.')
@click.option('--bak/--no-bak', default=True, help='Make .bak file for backup. (Defalult is True)')
@click.version_option(version=VERSION, prog_name=PROG_NAME)
@click.help_option('-h', '--help')
def main(f, t, bak):
    '''GitHub-rename

    \b
    This cli tool helps you to rename your github urls
    in .git/config and .gitmodules.

    \b
    Please help us improve by opening issues
    in https://github.com/qqghst/GitHub-rename
    '''
    file_name = './.git/config'
    github_rename(name_before=f, name_after=t, file_name=file_name, bak=bak)
    file_name = './.gitmodules'
    github_rename(name_before=f, name_after=t, file_name=file_name, bak=bak)


if __name__ == '__main__':
    main()
