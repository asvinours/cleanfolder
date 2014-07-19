#! /usr/bin/python2.7
# -*- coding: utf-8 -*-

import os, os.path, argparse, sys, collections
from os.path import join

_ntuple_diskusage = collections.namedtuple('usage', 'total used free')

def disk_usage(path):
    st = os.statvfs(path)
    free = st.f_bavail * st.f_frsize
    total = st.f_blocks * st.f_frsize
    used = (st.f_blocks - st.f_bfree) * st.f_frsize
    return _ntuple_diskusage(total, used, free)

def sort_files_by_last_modified(path):
    if not os.path.isdir(path):
        return

    fileData = {}
    # for each file in each folder of the specified root
    for root, dirs, files in os.walk(path):
        # for each file in this folder
        for f in files:
            fullPath = os.path.join(root, f)
            fileData[fullPath] = os.stat(fullPath).st_mtime

    fileData = sorted(fileData.items(), key = itemgetter(1))
    return fileData 


def delete_oldest_files(sorted_files, to_delete = 5):
    if to_delete <= 0:
        return

    for x in range(0, to_delete):
        print "Deleting: " + sorted_files[x][0]
        os.remove(sorted_files[x][0])


def remove_empty_folders(path):
    if not os.path.isdir(path):
        return

    # remove empty subfolders
    files = os.listdir(path)
    if len(files):
        for f in files:
            fullpath = os.path.join(path, f)
            if os.path.isdir(fullpath):
                remove_empty_folders(fullpath)

    # if folder empty, delete it
    files = os.listdir(path)
    if len(files) == 0:
        print "Removing empty folder:", path
        os.rmdir(path)

# we check if the cache key is passed as an argument
parser = argparse.ArgumentParser(description='If the disk space get low, delete oldest files, then remove empty folders', prog='Clean oldest files')
parser.add_argument('--path', '-p', dest='folder_path', action='store', default=False, help='The full path of the folder we want to clean')
parser.add_argument('--percent', '-f', dest='limit', action='store', default=20, help='The limit of free space')

args = parser.parse_args()

if args.folder_path is False or args.folder_path is None:
    sys.exit(1)

disk_space = disk_usage(args.folder_path)
percent_free = (disk_space.free*100)/disk_space.total

if percent_free > args.limit:
    print "Free space: ", percent_free, "%"
    sys.exit(1)

files = sort_files_by_last_modified(args.folder_path)
delete_oldest_files(files)
remove_empty_folders(args.folder_path)

print "Cleaning over"