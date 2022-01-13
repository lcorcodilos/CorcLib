template = '''
from argparse import ArgumentParser()
parser = ArgumentParser()

parser.add_argument('-o', '--output', metavar='OUTPUT', action='store', type=str,
                default   =   '',
                required  =   True,
                dest      =   'output',
                help      =   'Output name')

parser.add_argument('-n', '--number', metavar='COLUMNS', action='store', type=int,
                default   =   1,
                dest      =   'number',
                help      =   'Number of columns per page')

parser.add_argument('--off', action='store_true',
                default   =   False,
                dest      =   'off',
                help      =   'Add captions with file path')

parser.add_argument(dest = 'plotfiles', metavar='FILENAMES', type=str, nargs='+',
                help='Plot file names')

args = parser.parse_args()
'''

if __name__ == "__main__":
    print (template)