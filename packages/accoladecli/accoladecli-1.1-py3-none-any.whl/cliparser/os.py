import argparse
import os
import boto3

parser = argparse.ArgumentParser()
subparser = parser.add_subparsers()

accolade_group = subparser.add_parser('accolade')
accolade_subparser = accolade_group.add_subparsers()

accolade_storage = accolade_subparser.add_parser('storage')
accolade_subparser2 = accolade_storage.add_subparsers()

accolade_move = accolade_subparser2.add_parser('move')
accolade_move.set_defaults(which='move')
accolade_move.add_argument('mfile', help="File being moved")
accolade_move.add_argument('mfolder', help="Place being added")

accolade_copy = accolade_subparser2.add_parser('copy')
accolade_copy.set_defaults(which='copy')
accolade_copy.add_argument('cfile', help="File being copied")
accolade_copy.add_argument('cfolder', help="Place being copied")

accolade_list = accolade_subparser2.add_parser('list')
accolade_list.set_defaults(which='list')
accolade_list.add_argument('lfile', help="Directory of which the files will be listed")



accolade_remove = accolade_subparser2.add_parser('remove')
accolade_remove.set_defaults(which='remove')
accolade_remove.add_argument('rfile', help="File that will be deleted")

accolade_create = accolade_subparser2.add_parser('create')
accolade_create.set_defaults(which='create')
accolade_create.add_argument('cbuck', help="Bucket that will be created")


accolade_sync = accolade_subparser2.add_parser('sync')
accolade_sync.set_defaults(which='sync')
accolade_sync.add_argument('buck1', help="Bucket items are being copied from")
accolade_sync.add_argument('buck2', help="Bucket items are being copied into")

accolade_removebucket = accolade_subparser2.add_parser('removebucket')
accolade_removebucket.set_defaults(which="removebucket")
accolade_removebucket.add_argument('rembuck', help="Bucket that will be removed if it's empty")




args = vars(parser.parse_args())

which = args['which']


session = boto3.Session(profile_name='test')
s3res = session.resource('s3')
s3client = session.client('s3')


if which == 'list':
  os.system('aws s3 ls {} --profile test'.format(args['lfile']))

elif which == 'copy':
    os.system('aws s3 cp {} {} --profile test'.format(args['cfile'], args['cfolder']))

elif which == 'move':
    os.system('aws s3 mv {} {} --profile test'.format(args['mfile'], args['mfolder']))


elif which == 'create':
    os.system('aws s3 mb {} --profile test'.format(args['cbuck']))

elif which == 'sync':
    os.system('aws s3 sync {} {} --profile test'.format(args['buck1'], args['buck2']))


elif which == 'removebucket':
    os.system('aws s3 rb {} --profile test'.format(args['rembuck']))


elif which == 'remove':
    os.system('aws s3 rm {} --profile test'.format(args['rfile']))








