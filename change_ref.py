#!/usr/bin/python
import argparse
import re
import sys
import os, fnmatch
import shutil
import subprocess
import os.path
import json
import warnings

FROM_PROJECT_ID = '3997'
TO_PROJECT_ID = '1234'
FROM_PROJECT = 'cc-baccarat-3997'
TO_PROJECT = 'cc-newgame-1234'

def find(name, path):
    for root, dirs, files in os.walk(path):
        if name in files:
            return os.path.join(root, name)

def findFile(pattern, path):
    result = []
    for root, dirs, files in os.walk(path):
        for name in files:
            if fnmatch.fnmatch(name, pattern):
                result.append(os.path.join(root, name))
    return result

def getFileNameAndUID(filePath) :
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

# Return the png uid
# filePath:                 cc-newgame-1234/Assets/Background/Info_Baccarat.png.meta
# fileName:                 Info_Baccarat.png.meta
# content in files:         "uuid": "d8e13355-4287-4f45-a24a-d6c35db8afb0",
def getPNGUID(filePath, fileName):
    with open(filePath) as json_file:
        data = json.load(json_file)
        fileName = fileName.replace('.png.meta', '')
        result = ''
        if fileName not in data['subMetas']:
            print("FIND NO UUID FOR FILE ", filePath)
            return None
        else:
            return data['subMetas'][fileName]['uuid']

# Return the fnt uid
# filePath:                 cc-newgame-1234/Assets/Font/MyriadR_Gold-export.fnt.meta
# fileName:                 MyriadR_Gold-export.fnt.meta
def getFontUID(filePath):
    with open(filePath) as json_file:
        data = json.load(json_file)
        if 'uuid' not in data:
            print("FIND NO UUID FOR FILE ", filePath)
            return None
        else:
            return data['uuid']

def getPrefabUID(filePath):
    return getFontUID(filePath)

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

def changeScriptRefInPrefab(filePath):
    remove_uid, remove_file = getFileNameAndUID(filePath)

    # Predict the file to replace
    # Ex: from_name is "CardItem3997" ==> file to replace to_name is "CardItem1234"
    by_file = remove_file.replace(FROM_PROJECT_ID, TO_PROJECT_ID)

    # Find the to_uid
    if by_file is None:
        print('CANNOT FIND FILE', filePath)
        return

    by_file_path = find(by_file + '.js', quick_scripts_path + '/_Scripts')
    by_uid, by_name = getFileNameAndUID(by_file_path)

#     print("Replace {0} in file {1} by {2} in file {3}".format(remove_uid, remove_file, by_uid, by_file))

    curDir = to_project_dir + '/_Prefabs'
    for root, dirs, files in os.walk(curDir):
        for file in files:
             replaceFileContent(os.path.join(root, file), remove_uid, by_uid)

    curDir = to_project_dir
    for root, dirs, files in os.walk(curDir):
        for file in files:
            if file.endswith(".fire"):
                replaceFileContent(os.path.join(root, file), remove_uid, by_uid)

def changePNGRefInPrefab(filePath, fileName) :
    to_replaced_uuid = getPNGUID(filePath, fileName)
    replace_by_file_path = filePath.replace('Assets', '_Assets')
    replace_by_uuid = getPNGUID(replace_by_file_path, fileName)
    if to_replaced_uuid == None or replace_by_uuid == None:
        return
#     print("Replace {0} by {1} in file {2}".format(to_replaced_uuid, replace_by_uuid, replace_by_file_path))
    curDir = to_project_dir + '/_Prefabs'
    for root, dirs, files in os.walk(curDir):
        for file in files:
            if file.endswith(".prefab"):
                replaceFileContent(os.path.join(root, file), str(to_replaced_uuid), str(replace_by_uuid))

    curDir = to_project_dir
    for root, dirs, files in os.walk(curDir):
        for file in files:
            if file.endswith(".fire"):
                replaceFileContent(os.path.join(root, file), str(to_replaced_uuid), str(replace_by_uuid))

def changeFontRef(filePath, fileName) :
    to_replaced_uuid = getFontUID(filePath)
    replace_by_file_path = filePath.replace('Assets', '_Assets')
    replace_by_uuid = getFontUID(replace_by_file_path)
    if to_replaced_uuid == None or replace_by_uuid == None:
        return
#     print("Replace {0} by {1} in file {2}".format(to_replaced_uuid, replace_by_uuid, replace_by_file_path))
    curDir = to_project_dir + '/_Prefabs'
    for root, dirs, files in os.walk(curDir):
        for file in files:
            if file.endswith(".prefab"):
                replaceFileContent(os.path.join(root, file), str(to_replaced_uuid), str(replace_by_uuid))

    curDir = to_project_dir
    for root, dirs, files in os.walk(curDir):
        for file in files:
            if file.endswith(".fire"):
                replaceFileContent(os.path.join(root, file), str(to_replaced_uuid), str(replace_by_uuid))

def changePrefabRef(filePath, fileName) :
    to_replaced_uuid = getPrefabUID(filePath)
    replace_by_file_path = filePath.replace('Prefabs', '_Prefabs')
    replace_by_uuid = getPrefabUID(replace_by_file_path)
    if to_replaced_uuid == None or replace_by_uuid == None:
        return
#     print("Replace {0} by {1} in file {2}".format(to_replaced_uuid, replace_by_uuid, replace_by_file_path))
    curDir = to_project_dir + '/_Prefabs'
    for root, dirs, files in os.walk(curDir):
        for file in files:
            if file.endswith(".prefab"):
                replaceFileContent(os.path.join(root, file), str(to_replaced_uuid), str(replace_by_uuid))

    curDir = to_project_dir
    for root, dirs, files in os.walk(curDir):
        for file in files:
            if file.endswith(".fire"):
                replaceFileContent(os.path.join(root, file), str(to_replaced_uuid), str(replace_by_uuid))

tool_path = os.path.dirname(os.path.realpath(__file__))
root_path = os.path.abspath(os.path.join(tool_path, os.pardir))
all_in_one = os.path.abspath(os.path.join(root_path, os.pardir))
from_project_dir = root_path + '/' + FROM_PROJECT
to_project_dir = root_path + '/' + TO_PROJECT
quick_scripts_path = all_in_one + '/temp/quick-scripts/assets/' + TO_PROJECT

print("############ 1.CHANGE SCRIPTS REFERENCES IN PREFAB, SCENE ############")
curDir = quick_scripts_path + '/Scripts'
for root, dirs, files in os.walk(curDir):
    for file in files:
        if file.endswith(".js"):
            changeScriptRefInPrefab(os.path.join(root, file))

print('')
print("############ 2.CHANGE ASSETS IMAGES .PNG REF IN PREFAB, SCENE ############")
curDir = to_project_dir + '/Assets'
for root, dirs, files in os.walk(curDir):
    for file in files:
        if file.endswith(".png.meta"):
            changePNGRefInPrefab(os.path.join(root, file), file)

print('')
print("############ 3.CHANGE FONT REF IN PREFAB, SCENE ############")
curDir = to_project_dir + '/Assets'
for root, dirs, files in os.walk(curDir):
    for file in files:
        if file.endswith(".fnt.meta"):
            changeFontRef(os.path.join(root, file), file)

# print('')
# print("############ 4.CHANGE SKELETON REF ############")
#
# print('')
# print("############ 4.CHANGE SOUND REF ############")

print('')
print("############ 4.CHANGE PREFAB REF IN SCENE ############")
curDir = to_project_dir + '/Prefabs'
for root, dirs, files in os.walk(curDir):
    for file in files:
        if file.endswith(".prefab.meta"):
            changePrefabRef(os.path.join(root, file), file)