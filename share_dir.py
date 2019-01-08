#!/usr/bin/env python
# vim: set et sw=4 ts=4:

import argparse
import os
import sys
import time

from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools

import escapism

parser = argparse.ArgumentParser(
    usage="python share_dir.py -d 1tfOuRuWR_wkbPnfVVBWjRHGm4pLsbknj -s .tar.gz -e berkeley.edu",
    description="""
Share the google drive file to corresponding student, 
it will map regex (.+)\{file_suffix\}  to (.+)@\{email-suffix}. 

For example, given `--file-suffix .tar.gz --email-suffix berkeley.edu` and a file 
called xmo.tar.gz under the google drive directory, it will share the xmo.tar.gz 
to xmo@berkeley.edu
""",
)
parser.add_argument("--directory-id", "-d", required=True, help="Directory ID")
parser.add_argument("--file-suffix", "-s", required=True)
parser.add_argument("--email-suffix", "-e", required=True)
parser.add_argument("--email-message", "-E",
    help="Path to file containing custom notification message.")
parser.add_argument("--yes", "-y", action="store_true",
    help="Skip confirmation")
parser.add_argument("--no-unescape", "-U", action="store_true",
    help="Do not unescape email address.")
parser.add_argument("--exclude", "-x", default='',
    help="Comma-separated list of file prefixes to exclude.")
parser.add_argument("--users", "-u", default=None,
    help="Comma-separated list of users to restrict sharing to.")
args = parser.parse_args()

print(args)

# If modifying these scopes, delete the file token.json.
SCOPES = "https://www.googleapis.com/auth/drive"

store = file.Storage("token.json")
creds = store.get()
if not creds or creds.invalid:
    flow = client.flow_from_clientsecrets("credentials.json", SCOPES)
    creds = tools.run_flow(flow, store)
service = build("drive", "v3", http=creds.authorize(Http()))
files = service.files()


def list_file_items(dir_id):
    '''Get a list of all file names under {dir_id}.'''
    q = f"'{dir_id}' in parents"
    page_size = 500
    fields = "nextPageToken, files(mimeType, id, name)"
    file_items = []
    results = files.list(q=q, pageSize=page_size, fields=fields).execute()
    while True:
        file_items += results["files"]
        if 'nextPageToken' not in results: break
        next_page = results['nextPageToken']
        results = files.list(q=q, pageSize=page_size, fields=fields,
            pageToken=next_page).execute()
    return file_items


def get_file(f_id, dir_name=os.getcwd()):
    meta_data = files.get(fileId=f_id).execute()
    file_name = meta_data["name"]
    result = files.get_media(fileId=f_id).execute()
    with open(os.path.join(dir_name, file_name), "wb") as f:
        f.write(result)


def is_dir(f_id):
    result = files.get(fileId=f_id).execute()
    return result["mimeType"] == "application/vnd.google-apps.folder"

def derive_user(filename):
    '''
    Derive the username given an archive filename. For example, given
    foo-2ebar.tar.gz, return foo.bar.
    '''
    userpart = filename.replace(args.file_suffix, '')
    if not args.no_unescape: # default
        userpart = escapism.unescape(userpart, escape_char='-')
    return userpart

def callback(request_id, response, exception):
    if exception is not None:
        # Handle error
        print(exception)

def batch(iterable, n=100):
    '''
    The Google API limits batch requests to 100 calls at a time, so
    split up our file list into bunches of n.
    https://developers.google.com/drive/api/v3/batch

    This function is from https://stackoverflow.com/a/8290508.
    '''
    l = len(iterable)
    for i in range(0, l, n):
        yield iterable[i:min(i + n, l)]

## main

assert is_dir(args.directory_id), "The specified ID is not a directory."

file_items = list_file_items(args.directory_id)
exclude = args.exclude.split(',')
only_include = False
if args.users is not None:
    only_users = args.users.split(',')
    only_include = True

email_message = None
if args.email_message and os.path.exists(args.email_message):
    email_message = open(args.email_message).read()

for bunch in batch(file_items, n=10):
    batch = service.new_batch_http_request(callback=callback)
    for file_item in bunch:
        file_id = file_item['id']
        filename = file_item['name']
        userpart = derive_user(filename)

        # skip if we explicitly exclude
        if userpart in exclude: continue

        # skip if not in explicitly include
        if only_include and userpart not in only_users: continue

        email_to_share = userpart + '@' + args.email_suffix
        print("sharing {file_name} to {email}".format(file_name=filename,
            email=email_to_share))
        user_permission = {
            'type': 'user',
            'role': 'writer',
            'emailAddress': email_to_share
        }
        batch.add(service.permissions().create(
                fileId=file_id,
                body=user_permission,
                fields='id',
                emailMessage=email_message,
            ),
            callback=callback)
    
    if not args.yes:
        inp = input("confirm? [y/n]")
        if inp.lower() == 'y':
            batch.execute()
    else:
        batch.execute()
    time.sleep(1)
