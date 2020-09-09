#!/usr/bin/python
import argparse
import re
import sys
import os
import shutil
import subprocess
import os.path

FROM_PROJECT_ID = '3997'
TO_PROJECT_ID = '1234'
FROM_PROJECT = 'cc-baccarat-3997'
TO_PROJECT = 'cc-newgame-1234'

def getFileNameAndUID(filePath) :
#     print(filePath)
    file1 = open(filePath, 'r')
    Lines = file1.readlines()

    count = 0
    # Strips the newline character
    content = ''
    for line in Lines:
        if count == 1:
            content = line.strip()
            content = content[20:-14]
            break
        count = count + 1

    infos = content.split(', ')
    uid = infos[0][1:-1]
    file_name = infos[1][1:-1]
    return uid, file_name

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

tool_path = os.path.dirname(os.path.realpath(__file__))
root_path = os.path.abspath(os.path.join(tool_path, os.pardir))
all_in_one = os.path.abspath(os.path.join(root_path, os.pardir))
from_project_dir = root_path + '/' + FROM_PROJECT
to_project_dir = root_path + '/' + TO_PROJECT
quick_scripts_path = all_in_one + '/temp/quick-scripts/assets/' + TO_PROJECT
filePath = quick_scripts_path + '/Scripts/Card/CardItem3997.js'

remove_uid, remove_file = getFileNameAndUID(filePath)

# Predict the file to replace
# Ex: from_name is "CardItem3997" ==> file to replace to_name is "CardItem1234"
by_file = remove_file.replace(FROM_PROJECT_ID, TO_PROJECT_ID)

# Find the to_uid
if by_file is None:
    print('CANNOT FIND file ', by_file)

by_file_path = quick_scripts_path + '/_Scripts/Card/' + by_file + '.js'
by_uid, by_name = getFileNameAndUID(by_file_path)

print("Replace {0} in file {1} by {2} in file {3}".format(remove_uid, remove_file, by_uid, by_file))

# Replace from_uid by to_uid in all files (prefab)
curDir = to_project_dir + '/_Prefabs'
for root, dirs, files in os.walk(curDir):
    for file in files:
        if file.endswith(".prefab"):
             replaceFileContent(os.path.join(root, file), remove_uid, by_uid)