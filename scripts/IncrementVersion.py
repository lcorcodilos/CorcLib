#!/usr/bin/env python
from argparse import ArgumentError

if __name__ == '__main__':
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument('-p', metavar='PATH', action='store', type=str,
                    default   =   './',
                    dest      =   'path',
                    help      =   'Package path where version.py lives.')

    parser.add_argument('--major', action='store_true',
                    default   =   False,
                    dest      =   'major',
                    help      =   'Increment major version')

    parser.add_argument('--minor', action='store_true',
                    default   =   False,
                    dest      =   'minor',
                    help      =   'Increment minor version')

    parser.add_argument('--subminor', action='store_true',
                    default   =   False,
                    dest      =   'subminor',
                    help      =   'Increment subminor version')

    args = parser.parse_args()

    if sum([args.major, args.minor, args.subminor]) != 1:
        raise ArgumentError('Exactly one version level must be specified.')

    # Open in "read" to start and get current version
    with open('%s/version.py'%args.path, 'r') as f:
        lines = f.readlines()
        ver_str = None
        for line_num, line in enumerate(lines):
            if '__version__' in line:
                ver_str = line.split('=')[-1].strip().strip("'")
                on_line = line_num
                break
        
    if not ver_str:
        raise RuntimeError('Could not find __version__ in version.py.')

    # Manipulate the version number
    maj, minor, submin = [int(i) for i in ver_str.split('.')]
    
    if args.major:
        maj += 1
        minor = 0
        submin = 0
    elif args.minor:
        minor += 1
        submin = 0
    elif args.subminor:
        submin += 1

    lines[on_line] = lines[on_line].replace(ver_str, '%s.%s.%s'%(maj, minor, submin))

    # Write the output
    open('%s/version.py'%args.path, 'w').writelines(lines)