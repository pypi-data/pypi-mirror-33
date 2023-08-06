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
accolade_move.add_argument('buck1', help="Bucket that files are moving from")
accolade_move.add_argument('buck2', help="Bucket that files are going to be placed into")

accolade_copy = accolade_subparser2.add_parser('copy')
accolade_copy.set_defaults(which='copy')
accolade_copy.add_argument('buck', help="Bucket location to be copied")
accolade_copy.add_argument('key', help="Key location to be copied")
accolade_copy.add_argument('buck2', help="File being copied")
accolade_copy.add_argument('key2', help="Place being copied")

accolade_list = accolade_subparser2.add_parser('list')
accolade_list.set_defaults(which='list')
accolade_list.add_argument('lbuck', help="Directory of which the files will be listed")

accolade_listall = accolade_subparser2.add_parser('listallbuck')
accolade_listall.set_defaults(which='listallbuck')


accolade_remove = accolade_subparser2.add_parser('remove')
accolade_remove.set_defaults(which='remove')
accolade_remove.add_argument('rbucket', help="Bucket of object to be removed")
accolade_remove.add_argument('rkey', help="Key within bucket to remove file")


accolade_create = accolade_subparser2.add_parser('create')
accolade_create.set_defaults(which='create')
accolade_create.add_argument('cbuck', help="Bucket that will be created")


accolade_sync = accolade_subparser2.add_parser('sync')
accolade_sync.set_defaults(which='sync')
accolade_sync.add_argument('buckname1', help="Name of bucket that items are being copied from")
accolade_sync.add_argument('buckname2', help="Name of bucket that items are being copied into")
accolade_sync.add_argument('path1', help="Path to directory that files are being copied from")
accolade_sync.add_argument('path2', help="Path to directory that files are being copied to")


accolade_upload = accolade_subparser2.add_parser('upload')
accolade_upload.set_defaults(which='upload')
accolade_upload.add_argument('file', help="File that will be upload into the bucket-key location")
accolade_upload.add_argument('bucket', help="Bucket that the file will be uploaded to")
accolade_upload.add_argument('key', help="Key that the file will be uploaded to")

accolade_dirupload = accolade_subparser2.add_parser('dirupload')
accolade_dirupload.set_defaults(which='dirupload')
accolade_dirupload.add_argument('directory', help="Absolute path to the directory that will be copied")
accolade_dirupload.add_argument('bucketname', help="Bucket that files will be uploaded too")
accolade_dirupload.add_argument('key', help="Key that files will be uploaded to")

accolade_upload = accolade_subparser2.add_parser('replace')
accolade_upload.set_defaults(which='replace')
accolade_upload.add_argument('file', help="File that will be replacing its previous version")
accolade_upload.add_argument('repbucket', help="Bucket that the previous file was uploaded to")
accolade_upload.add_argument('repkey', help="Key that the previous file was uploaded to, Default to "" if not key")





args = vars(parser.parse_args())

which = args['which']


session = boto3.Session(profile_name='test')
s3res = session.resource('s3')
s3client = session.client('s3')


def uploadDirectory(path, bucketname, key):
    for root, dirs, files in os.walk(path):
        for file in files:
            local_path = os.path.join(root, file)
            relative_path = os.path.relpath(local_path, path)
            s3_path = os.path.join(key, relative_path)
            if file != '.DS_Store':
                s3client.upload_file(local_path, bucketname, s3_path)



if which == 'list':
  for object in s3res.Bucket(args['lbuck']).objects.all():
      print(object)

if which == 'listallbuck':
    listbucket = s3client.list_buckets()
    buckets = [bucket['Name'] for bucket in listbucket['Buckets']]
    for bucket in buckets:
        print(bucket)

# Should work- I just don't have access to do so
elif which == 'copy':
    copy_source = {
        'Bucket': 'buck',
        'Key': 'key'
    }
    s3client.copy(copy_source, 'buck2', 'key2')


elif which == 'move':
    src = s3res.Bucket(args['mfile'])
    dst = s3res.Bucket(args['mfolder'])
    for k in src.list():
        dst.copy_key(k.key.name, src.name, k.key.name)
        k.delete()

elif which == 'create':
    s3res.create_bucket(Bucket=args['cbuck'])


# Don't have permissions, but this should work
elif which == 'sync':
    # src = s3res.Bucket(args['buck1'])
    # dst = s3res.Bucket(args['buck2'])
    # for object in src.objects.all():
    #     file = object.key
    #     print(file)
    #     # if file not in dst.objects.all():
    #     #     s3client.upload_file(file, args['buck2'], '')
    old_bucket_name = args['buckname1']
    old_prefix = args['path1']
    new_bucket_name = args['buckname2']
    new_prefix = args['path2']
    old_bucket = s3res.Bucket(old_bucket_name)
    new_bucket = s3res.Bucket(new_bucket_name)

    for obj in old_bucket.objects.filter(Prefix=old_prefix):
        old_source = {'Bucket': old_bucket_name,
                      'Key': obj.key}
        new_key = obj.key.replace(old_prefix, new_prefix)
        new_obj = new_bucket.Object(new_key)
        new_obj.copy(old_source)

# For key, must put location/file name
elif which == 'upload':
    s3client.upload_file(args['file'], args['bucket'], args['key'])

elif which == 'dirupload':
    uploadDirectory(args['directory'], args['bucketname'], args['key'])

elif which == 'replace':
    s3res.Object(args['repbucket'], args['repkey']).delete()
    s3client.upload_file(args['file'], args['repbucket'], args['repkey'])

elif which == 'remove':
    s3res.Object(args['rbucket'], args['rkey']).delete()




# This is a will eventually be used to restrict access to specific buckets
# aws s3api put-bucket-policy --bucket Test --policy file://policy.json
#
# policy.json:
# {
#    "Statement": [
#       {
#          "Effect": "Allow",
#          "Principal": "*",
#          "Action": "s3:GetObject",
#          "Resource": "arn:aws:s3:::Test/*"
#       },
#       {
#          "Effect": "Allow",
#          "Principal": {
#             "AWS": "arn:aws:iam::123456789012:root"
#          },
#          "Resource": "arn:aws:s3:::Test/*"
#       }
#    ]
# }