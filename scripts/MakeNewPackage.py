#!/usr/bin/env python3
'''Makes a basic package with the following structure and with basic infrastructure already in place.
Package/
|--- __init__.py
|--- setup.py
|--- version.py
|--- Package/
|--- .git/
|--- scripts/
'''

import subprocess, os
from CorcLib.common import cd, lib_path

def cmd(cmd):
    print (cmd)
    subprocess.call(cmd, shell=True)

def template_replace(template_name, replace):
    with open(f'{lib_path()}/templates/{template_name}', 'r') as f:
        content = f.read()
        for find, replace in vars(replace).items():
            content = content.replace(find, replace)
    
    return content

if __name__ == '__main__':
    from argparse import ArgumentParser

    parser = ArgumentParser()

    parser.add_argument('-n', '--name', metavar='OUTPUT', action='store', type=str,
                    default   =   '',
                    required  =   True,
                    dest      =   'PACKAGE_NAME',
                    help      =   'Package name including the path')

    parser.add_argument('--author', metavar='AUTHOR', action='store', type=str,
                    default   =   'Lucas Corcodilos',
                    dest      =   'AUTHOR_NAME',
                    help      =   'Author name to include in setup.py')

    parser.add_argument('--email', metavar='me@email.com', action='store', type=str,
                    default   =   'corcodilos.lucas@gmail.com',
                    dest      =   'AUTHOR_EMAIL',
                    help      =   'Author email to include in setup.py.')

    args = parser.parse_args()
    name = args.PACKAGE_NAME

    os.mkdir(name)
    os.mkdir(f'{name}/src')
    os.mkdir(f'{name}/src/{name}')
    os.mkdir(f'{name}/scripts')

    with cd(name):
        # simple copies first
        for filename in ['version.py']:
            cmd(f'cp {lib_path()}/templates/{filename} {filename}')

        for filename in ['__init__.py']:
            cmd(f"sed 's/PACKAGE_NAME/{name}/g' {lib_path()}/templates/{filename} > {filename}")

        # Make some dummy files
        open (f'src/{name}/__init__.py', 'w')
        with open('scripts/dummy.py', 'w') as f:
            f.write('#!/usr/bin/env python3')

        # Find replaces for package specific setup
        for filename in ['setup.py', 'README.md']:
            with open(filename, 'w') as f:
                f.write(template_replace(filename, args))

        # Make a git commit
        cmd('git init')
        cmd('git add *')
        cmd("git commit -m 'Base package structure created'")
