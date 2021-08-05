#!/usr/bin/python
import argparse
import re
import sys
import os
import shutil
import subprocess
import os.path
import config
from zipfile import ZipFile

FROM_PROJECT_ID = config.FROM_PROJECT_ID
TO_PROJECT_ID = config.TO_PROJECT_ID
FROM_PROJECT = config.FROM_PROJECT
TO_PROJECT = config.TO_PROJECT
PREFIX = "_PREFIX_"

def clone_folder(fromFolder, toFolder) :
    tool_path = os.path.dirname(os.path.realpath(__file__))
    root_path = os.path.abspath(os.path.join(tool_path, os.pardir))
    src_path = root_path + '/' + TO_PROJECT + '/' + fromFolder
    dest_path = root_path + '/'+ TO_PROJECT + '/' + toFolder

    # Copying the contents from Source
    # to Destination without some
    # specified files or directories
    shutil.rmtree(dest_path, ignore_errors=True)
    shutil.copytree(src_path, dest_path, ignore = shutil.ignore_patterns('*.meta', 'a'))

def replaceFileContent(filename, old_string, new_string):
    # Safely read the input filename using 'with'
    with open(filename) as f:
        s = f.read()
        if old_string not in s:
            return

    # Safely write the changed content, if found in the file
    with open(filename, 'w') as f:
        print('Changing "{old_string}" to "{new_string}" in {filename}'.format(**locals()))
        s = s.replace(old_string, new_string)
        f.write(s)
########
# MAIN #
########
# # # 0.Copy to new folder, ignore .git
tool_path = os.path.dirname(os.path.realpath(__file__))
root_path = os.path.abspath(os.path.join(tool_path, os.pardir))
from_project_dir = root_path + '/' + FROM_PROJECT
to_project_dir = root_path + '/' + TO_PROJECT

# os.popen('killall CocosCreator')
print('##### BACKUP FILES ######')
backupFile = root_path + '/' + FROM_PROJECT
if os.path.isfile(backupFile + '.zip'):
    with ZipFile(backupFile + '.zip', 'r') as zipObj:
       zipObj.extractall(backupFile)
else:
    shutil.make_archive(backupFile, 'zip', from_project_dir)

print('##### COPY PROJECT ######')
shutil.rmtree(to_project_dir, ignore_errors=True)
shutil.copytree(from_project_dir, to_project_dir)
shutil.rmtree(to_project_dir + '/.git', ignore_errors=True)

curDir = to_project_dir
for dir in os.listdir(curDir):
    if os.path.isdir(os.path.join(curDir, dir)) :
        clone_folder(dir, PREFIX + dir)

# # 3.Rename file with ID
curDir = to_project_dir
subprocess.call([sys.executable, tool_path+'/rename_files.py', curDir, FROM_PROJECT_ID, TO_PROJECT_ID])
for dirname, dirnames, filenames in os.walk(curDir):
    for subdirname in dirnames:
        curDir = os.path.join(dirname, subdirname)
        if PREFIX in curDir:
            subprocess.call([sys.executable, tool_path+'/rename_files.py', curDir, FROM_PROJECT_ID, TO_PROJECT_ID])

# Replace gameID in file *.js
curDir = to_project_dir
for root, dirs, files in os.walk(curDir):
    for file in files:
        if file.endswith(".js") and PREFIX in root:
            if not file.endswith("Config" + TO_PROJECT_ID + ".js"):
                 replaceFileContent(os.path.join(root, file), FROM_PROJECT_ID, TO_PROJECT_ID)

# Replace gameID in file *.ts
curDir = to_project_dir
for root, dirs, files in os.walk(curDir):
    for file in files:
        if file.endswith(".ts") and PREFIX in root:
            if not file.endswith("Config" + TO_PROJECT_ID + ".ts"):
                 replaceFileContent(os.path.join(root, file), FROM_PROJECT_ID, TO_PROJECT_ID)

# Rename file scene
curDir = to_project_dir
subprocess.call([sys.executable, tool_path+'/rename_files.py', curDir, FROM_PROJECT_ID, TO_PROJECT_ID])

# Replace gameID in file R3997.fire
curDir = to_project_dir
for root, dirs, files in os.walk(curDir):
    for file in files:
        if file.endswith(".fire"):
            replaceFileContent(os.path.join(root, file), FROM_PROJECT_ID, TO_PROJECT_ID)

shutil.rmtree(from_project_dir, ignore_errors=True)
# os.popen('open -a CocosCreator')