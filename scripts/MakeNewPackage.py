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
    with open('%s/templates/%s'%(lib_path(), template_name), 'r') as f:
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
    os.mkdir(name+'/'+name)
    os.mkdir(name+'/scripts')

    with cd(name):
        # simple copies first
        for filename in ['__init__.py', 'version.py']:
            cmd('cp {0}/templates/{1} {1}'.format(lib_path(), filename))

        # Make some dummy files
        open ('%s/__init__.py'%name, 'w')
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