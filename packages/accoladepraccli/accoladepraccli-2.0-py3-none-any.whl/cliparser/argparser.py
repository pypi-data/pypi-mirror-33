import argparse
import os
import boto3

#Create an argument cliparser
parser = argparse.ArgumentParser()



def usoptionals():
    # Add all the optional and required arguments on the command line
    parser.add_argument('--file', help="File being moved")
    parser.add_argument('--folder', help="Place being added")
    parser.add_argument('command', help="Command to be executed on CLI")
    parser.add_argument('--filerem', help="File going to be removed")
    parser.add_argument('--newbucket', help="Create a new bucket")
    parser.add_argument('--listitems', help="List the items in a file", default="")
    parser.add_argument('--syncbuck1', help="First bucket to sync")
    parser.add_argument('--syncbuck2', help="Second bucket to sync")
    parser.add_argument('--emptybuck', help="Remove an empty bucket")
    parser.add_argument('--bucket', help="This is a bucket that has a variety of purposes")
    parser.add_argument('--othbucket', help="This is the bucket to upload files into")
    parser.add_argument('--key', help="This is the path within a bucket")
    parser.add_argument('--othkey', help="This is the path within a bucket")

    parser.add_argument('--emptybuck', help="Remove an empty bucket")
    parser.add_argument('--bucket', help="This is a bucket that has a variety of purposes")
    parser.add_argument('--othbucket', help="This is the bucket to upload files into")
    parser.add_argument('--key', help="This is the path within a bucket")
    parser.add_argument('--othkey', help="This is the path within a bucket")



#useoptionals()

# Set all the command-line arguments to respective variables for testing
# Uncomment only if using useoptionals()

# args = cliparser.parse_args()
# fl = args.file
# flder = args.folder
# flrem = args.filerem
# cmd = args.command
# newbuck = args.newbucket
# list = args.listitems
# buck_1 = args.syncbuck1
# buck_2 = args.syncbuck2
# empbuck = args.emptybuck
# buck = args.bucket
# ky = args.key
# othbuck = args.othbucket
# othky = args.othkey



#Print out all the arguments on the command for testing; usually defaults to "None"
# Uncomment only if using useoptionals()

# print(fl)
# print(flder)
# print(cmd)
# print(newbuck)
# print(list)
# print(buck_1)
# print(buck_2)
# print(empbuck)
# print(buck)
# print(ky)
# print(othbuck)


def ogcommandline():

    #'move' is to move, 'copy' is to copy
    if cmd == 'move':
        os.system('aws s3 {} {} {} --profile test '.format('mv', fl, flder))
    if cmd == 'copy':
        os.system('aws s3 {} {} {} --profile test '.format('cp', fl, flder))
    #'remove' is to remove
    elif cmd == 'remove':
        os.system('aws s3 {} {} --profile test '.format('rm', flrem))
    #'create' is to create a new bucket(credentials are required)
    elif cmd == 'create':
        os.system('aws s3 {} {} --profile test '.format('mb', newbuck))
    #'list' lists the items within a bucket or folder
    elif cmd == 'list':
        os.system('aws s3 {} {} --profile test '.format('ls', list))
    #'sync' basically recursively copies all directories from buck_1 to buck_2
    elif cmd == 'sync':
        os.system('aws s3 {} {} {} --profile test '.format(cmd, buck_1, buck_2))
    #'removebuck' will remove an empty bucket
    elif cmd == 'removebuck':
        os.system('aws s3 {} {} --profile test '.format('rb', empbuck))



parser = argparse.ArgumentParser()
subparser = parser.add_subparsers()

accolade_group = subparser.add_parser('accolade-cli')
accolade_subparser = accolade_group.add_subparsers()

accolade_storage = accolade_subparser.add_parser('storage')
accolade_subparser2 = accolade_storage.add_subparsers()

accolade_move = accolade_subparser2.add_parser('move')
accolade_move.add_argument('mfile', help="File being moved")
accolade_move.add_argument('mfolder', help="Place being added")

accolade_copy = accolade_subparser2.add_parser('copy')
accolade_copy.add_argument('cfile', help="File being copied")
accolade_copy.add_argument('cfolder', help="Place being copied")

accolade_list = accolade_subparser2.add_parser('list')
accolade_list.add_argument('lfile', help="Directory of which the files will be listed")

accolade_remove = accolade_subparser2.add_parser('remove')
accolade_remove.add_argument('rfile', help="File that will be deleted")

accolade_create = accolade_subparser2.add_parser('create')
accolade_create.add_argument('cbuck', help="Bucket that will be created")


accolade_sync = accolade_subparser2.add_parser('sync')
accolade_sync.add_argument('buck1', help="Bucket items are being copied from")
accolade_sync.add_argument('buck2', help="Bucket items are being copied into")

accolade_removebucket = accolade_subparser2.add_parser('removebucket')
accolade_removebucket.add_argument('rembuck', help="Bucket that will be removed if it's empty")



args = parser.parse_args()

def errorhandling():
    try:
        # 'move' is to move
        if args.mfile:
            os.system('aws s3 mv {} {} --profile test '.format(args.mfile, args.mfolder))
    except:
        try:
            # 'copy' is to copy
            if args.cfile:
                os.system('aws s3 cp {} {} --profile test '.format(args.cfile, args.cfolder))
        except:
            try:
                # 'list' lists the items within a bucket or folder
                if args.lfile:
                    os.system('aws s3 ls {} --profile test '.format(args.list))
            except:
                try:
                    if args.rfile:
                        os.system('aws s3 rm {} --profile test '.format(args.rfile))
                except:
                    try:
                        if args.cbuck:
                            os.system('aws s3 mb {} --profile test '.format(args.cbuck))
                    except:
                        try:
                            if args.buck1:
                                os.system('aws s3 sync {} {} --profile test '.format(args.buck1, args.buck2))
                        except:
                            try:
                                if args.rembuck:
                                    os.system('aws s3 rb {} --profile test '.format(args.rembuck))
                            except:
                                pass



#Use os library to run AWS CLI in this python script by passing in the command-line arguments
#There are some interesting rules between required or optional
def commandline():

    # 'move' is to move
    if args.mfile:
        os.system('aws s3 mv {} {} --profile test '.format(args.mfile, args.mfolder))

    # 'copy' is to copy
    elif args.cfile:
        os.system('aws s3 cp {} {} --profile test '.format(args.cfile, args.cfolder))

    # 'list' lists the items within a bucket or folder
    elif args.lfile:
        os.system('aws s3 ls {} --profile test '.format(args.lfile))

    #'remove' is to remove
    elif args.rfile:
        os.system('aws s3 {} --profile test '.format(args.rfile))

    #'create' is to create a new bucket(credentials are required)
    elif args.create:
        os.system('aws s3 mb {} --profile test '.format(args.cbuck))

    #'sync' basically recursively copies all directories from buck_1 to buck_2
    elif args.syncfile:
        os.system('aws s3 sync {} {} --profile test '.format( args.buck1, args.buck2))

    #'removebuck' will remove an empty bucket
    elif args.rembuck:
        os.system('aws s3 rm {} --profile test '.format(args.rembuck))

#commandline()

def useboto():
    # Creating Boto objects to replicate everything on top without OS but instead Boto
    session = boto3.Session(profile_name='test')
    s3res = session.resource('s3')
    s3client = session.client('s3')

    # Creates a new bucket
    if cmd == 'create':
        s3res.create_bucket(Bucket=buck)

    # Key must be like Vikram/file1.txt
    if cmd == 'up':
        s3client.upload_file(fl, buck, ky)

    # Othkey must also be like Jai/file2.txt
    if cmd == 'copy':
        copy_source = {
            'Bucket': buck,
            'Key': ky
        }
        s3client.copy(copy_source, othbuck, othky)

    # Download object at bucket-name with key-name to file
    if cmd == 'download':
        s3client.download_file(buck, ky, fl)

    # Lists all the buckets
    if cmd == 'ls':
        listbuckets = s3client.list_buckets()
        buckets = [bucket['Name'] for bucket in listbuckets['Buckets']]
        print("Bucket List: %s" % buckets)