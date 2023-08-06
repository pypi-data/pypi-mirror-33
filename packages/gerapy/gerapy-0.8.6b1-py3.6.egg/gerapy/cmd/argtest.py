import argparse

parser = argparse.ArgumentParser()
subparsers = parser.add_subparsers(dest='command')

# migrate
parser_migrate = subparsers.add_parser('migrate', help='migrate database')
# create superuser
parser_createsuperuser = subparsers.add_parser('createsuperuser', help='create superuser')

# makemigrations
parser_makemigrations = subparsers.add_parser('makemigrations', help='create superuser')

# runserver
parser_runserver = subparsers.add_parser('runserver', help='runserver')
parser_runserver.add_argument('-p', '--port', default=8000, type=int, help='server port')
parser_runserver.add_argument('-H', '--host', default='127.0.0.1', type=str, help='server host')

# init
parser_init = subparsers.add_parser('init', help='init workspace')
parser_init.add_argument('-f', '--folder', default='gerapy', type=str, help='initial workspace')

# generate
parser_generate = subparsers.add_parser('generate', help='generate code for project')
parser_generate.add_argument('project', type=str, help='project to generate')

# parse
parser_parse = subparsers.add_parser('parse', help='parse project for debugging')
parser_parse.add_argument('project', type=str, help='target project')
parser_parse.add_argument('spider', type=str, help='target spider')
parser_parse.add_argument('-d', '--dir', default='.', type=str, help='default workspace')
parser_parse.add_argument('-s', '--start', default=False, type=bool, help='parse start requests or not')
parser_parse.add_argument('-u', '--url', default='', type=str, help='url to parse')
parser_parse.add_argument('-c', '--callback', default='parse', type=str, help='callback')
parser_parse.add_argument('-m', '--method', default='GET', type=str, help='method')

# loaddata
parser_loaddata = subparsers.add_parser('loaddata', help='load data from configs')
parser_loaddata.add_argument('source', type=str, help='configs path')

# dumpdata
parser_dumpdata = subparsers.add_parser('dumpdata', help='dump data to configs')
parser_dumpdata.add_argument('appname', type=str, help='configs path')

args = parser.parse_args()
print(args)
