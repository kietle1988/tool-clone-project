#!/usr/bin/python
import argparse
import re
import sys
import os, fnmatch
import shutil
import subprocess
import os.path
import json
import config
from zipfile import ZipFile

FROM_PROJECT_ID = config.FROM_PROJECT_ID
TO_PROJECT_ID = config.TO_PROJECT_ID
FROM_PROJECT = config.FROM_PROJECT
TO_PROJECT = config.TO_PROJECT
USER_DEFINE_TYPE = config.USER_DEFINE_TYPE
PREFIX = "_PREFIX_"

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
        if "_cclegacy._RF.push({}" in line:
            content = line.strip()
            break

    infos = content.split(', ')
    uid = infos[1][1:-1]
    file_name = infos[2][1:-1]
    return uid, file_name

# Return the png uid
# filePath:                 cc-newgame-1234/Assets/Background/Info_Baccarat.png.meta
# fileName:                 Info_Baccarat.png.meta
# ext:                      .png.meta, .jpg.meta
# content in files:         "uuid": "d8e13355-4287-4f45-a24a-d6c35db8afb0",
def getImageUID(filePath, fileName, ext):
    with open(filePath) as json_file:
        data = json.load(json_file)
        fileName = fileName.replace(ext, '')
        if "redirect" not in data['userData']:
            print("FIND NO UUID FOR FILE ", filePath)
            return None
        else:
            return data['userData']['redirect']

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

def changeScriptRef(root_path, by_file_name):
    by_file_path = os.path.join(root_path, by_file_name)
    by_uid, by_file = getFileNameAndUID(by_file_path)
    remove_file_path = os.path.join(root_path.replace(PREFIX, ''), by_file_name.replace(TO_PROJECT_ID, FROM_PROJECT_ID))
    remove_uid, remove_name = getFileNameAndUID(remove_file_path)

    curDir = to_project_dir
    for root, dirs, files in os.walk(curDir):
        for file in files:
            if PREFIX in root:
                replaceFileContent(os.path.join(root, file), remove_uid, by_uid)

    curDir = to_project_dir
    for root, dirs, files in os.walk(curDir):
        for file in files:
            if file.endswith(".scene"):
                replaceFileContent(os.path.join(root, file), remove_uid, by_uid)

def changeImageRef(root_path, by_file_name, ext) :
    by_file_path = os.path.join(root_path, by_file_name)
    by_uid = getImageUID(by_file_path, by_file_name, ext)
    remove_file_name = by_file_name.replace(TO_PROJECT_ID, FROM_PROJECT_ID)
    remove_file_path = os.path.join(root_path.replace(PREFIX, ''), remove_file_name)
    remove_uid = getImageUID(remove_file_path, remove_file_name, ext)
    if remove_uid == None or by_uid == None:
        return

    curDir = to_project_dir
    for root, dirs, files in os.walk(curDir):
        for file in files:
            if file.endswith(".prefab") and PREFIX in root:
                replaceFileContent(os.path.join(root, file), str(remove_uid), str(by_uid))

    curDir = to_project_dir
    for root, dirs, files in os.walk(curDir):
        for file in files:
            if file.endswith(".scene"):
                replaceFileContent(os.path.join(root, file), str(remove_uid), str(by_uid))

def changeFontRef(root_path, by_file_name) :
    by_file_path = os.path.join(root_path, by_file_name)
    by_uid = getFontUID(by_file_path)
    remove_file_name = by_file_name.replace(TO_PROJECT_ID, FROM_PROJECT_ID)
    remove_file_path = os.path.join(root_path.replace(PREFIX, ''), remove_file_name)
    remove_uid = getFontUID(remove_file_path)
    if remove_uid == None or by_uid == None:
        return

    curDir = to_project_dir
    for root, dirs, files in os.walk(curDir):
        for file in files:
            if file.endswith(".prefab") and PREFIX in root:
                replaceFileContent(os.path.join(root, file), str(remove_uid), str(by_uid))

    curDir = to_project_dir
    for root, dirs, files in os.walk(curDir):
        for file in files:
            if file.endswith(".scene"):
                replaceFileContent(os.path.join(root, file), str(remove_uid), str(by_uid))


def changeSpineRef(filePath, fileName) :
    changeFontRef(filePath, fileName)

def changeAnimRef(filePath, fileName) :
    changeFontRef(filePath, fileName)

def changeSoundRef(filePath, fileName) :
    changeFontRef(filePath, fileName)

def changeAtlasRef(filePath, fileName) :
    changeFontRef(filePath, fileName)

def getListUIDFromPackedFile(filePath) :
    listUIDs = []
    with open(filePath) as json_file:
        data = json.load(json_file)
        if 'atlasTextureName' in data['userData']:
            subMetas = data['subMetas']
            for key in subMetas:
                listUIDs.append(subMetas[key]['uuid'])
        else:
            print('NOT A PACKED FILE', filePath)
    return listUIDs

def changeImageInPackerRef(root_path, by_file_name) :
    by_file_path = os.path.join(root_path, by_file_name)
    by_uids = getListUIDFromPackedFile(by_file_path)
    remove_file_name = by_file_name.replace(TO_PROJECT_ID, FROM_PROJECT_ID)
    remove_file_path = os.path.join(root_path.replace(PREFIX, ''), remove_file_name)
    remove_uids = getListUIDFromPackedFile(remove_file_path)
    if by_uids == None or remove_uids == None:
        return

    curDir = to_project_dir
    for root, dirs, files in os.walk(curDir):
        for file in files:
            if file.endswith(".prefab") and PREFIX in root:
                for i in range(len(remove_uids)):
                    replaceFileContent(os.path.join(root, file), str(remove_uids[i]), str(by_uids[i]))

    curDir = to_project_dir
    for root, dirs, files in os.walk(curDir):
        for file in files:
            if file.endswith(".scene"):
                for i in range(len(remove_uids)):
                    replaceFileContent(os.path.join(root, file), str(remove_uids[i]), str(by_uids[i]))

def changePrefabRef(root_path, by_file_name) :
    by_file_path = os.path.join(root_path, by_file_name)
    by_uid = getPrefabUID(by_file_path)
    remove_file_name = by_file_name.replace(TO_PROJECT_ID, FROM_PROJECT_ID)
    remove_file_path = os.path.join(root_path.replace(PREFIX, ''), remove_file_name)
    remove_uid = getPrefabUID(remove_file_path)
    if remove_uid == None or by_uid == None:
        return

    curDir = to_project_dir
    for root, dirs, files in os.walk(curDir):
        for file in files:
            if file.endswith(".prefab") and PREFIX in root:
                replaceFileContent(os.path.join(root, file), str(remove_uid), str(by_uid))

    curDir = to_project_dir
    for root, dirs, files in os.walk(curDir):
        for file in files:
            if file.endswith(".scene"):
                replaceFileContent(os.path.join(root, file), str(remove_uid), str(by_uid))

tool_path = os.path.dirname(os.path.realpath(__file__))
root_path = os.path.abspath(os.path.join(tool_path, os.pardir))
all_in_one = os.path.abspath(os.path.join(root_path, os.pardir))
from_project_dir = root_path + '/' + FROM_PROJECT
to_project_dir = root_path + '/' + TO_PROJECT
quick_scripts_path = all_in_one + '/temp/programming/packer-driver/targets/editor/mods/fs/0/assets/' + TO_PROJECT

os.popen('killall CocosCreator')
print("############ 1.CHANGE USER DEFINE TYPE IN PREFAB ############")
curDir = to_project_dir
for root, dirs, files in os.walk(curDir):
    for file in files:
        if file.endswith(".prefab"):
            for fromCustomType in USER_DEFINE_TYPE:
                toCustomType = fromCustomType.replace(FROM_PROJECT_ID, TO_PROJECT_ID)
                if toCustomType is not None:
                    replaceFileContent(os.path.join(root, file), fromCustomType, toCustomType)


print("############ 2.CHANGE SCRIPTS REFERENCES IN PREFAB, SCENE ############")
curDir = quick_scripts_path
for root, dirs, files in os.walk(curDir):
    for file in files:
        if file.endswith(".js") and PREFIX in root:
            changeScriptRef(root, file)

print('')
print("############ 3.CHANGE ASSETS IMAGES .PNG, JPG REF IN PREFAB, SCENE ############")
curDir = to_project_dir
for root, dirs, files in os.walk(curDir):
    for file in files:
        if PREFIX in root:
            if file.endswith(".png.meta"):
                changeImageRef(root, file, ".png.meta")
            if file.endswith(".jpg.meta"):
                changeImageRef(root, file, ".jpg.meta")

print('')
print("############ 4.CHANGE FONT REF IN PREFAB, SCENE ############")
curDir = to_project_dir
for root, dirs, files in os.walk(curDir):
    for file in files:
        if file.endswith(".fnt.meta") and PREFIX in root:
            changeFontRef(root, file)

print('')
print("############ 5.CHANGE SKELETON REF ############")
curDir = to_project_dir
for root, dirs, files in os.walk(curDir):
    for file in files:
        if file.endswith(".json.meta") and PREFIX in root:
            print(file)
            changeSpineRef(root, file)

print('')
print("############ 5.1.CHANGE ANIM REF ############")
curDir = to_project_dir
for root, dirs, files in os.walk(curDir):
    for file in files:
        if file.endswith(".anim") and PREFIX in root:
            print(file)
            changeAnimRef(root, file)

print('')
print("############ 6.CHANGE ATLAS REF ############")
curDir = to_project_dir + '/Assets'
for root, dirs, files in os.walk(curDir):
    for file in files:
        if file.endswith(".plist.meta") and PREFIX in root:
            print(file)
            changeAtlasRef(root, file)

curDir = to_project_dir + '/resources'
for root, dirs, files in os.walk(curDir):
    for file in files:
        print(file)
        if file.endswith(".plist.meta") and PREFIX in root:
            changeAtlasRef(root, file)

print('')
print("############ 7.CHANGE SOUND REF ############")
curDir = to_project_dir
for root, dirs, files in os.walk(curDir):
    for file in files:
        if file.endswith(".mp3.meta") and PREFIX in root:
            changeSoundRef(root, file)

print('')
print("############ 8.CHANGE IMAGE IN TEXTURE PACKER REF ############")
curDir = to_project_dir
for root, dirs, files in os.walk(curDir):
    for file in files:
        if file.endswith(".plist.meta"):
            print(file)
            changeImageInPackerRef(root, file)

print('')
print("############ 9.CHANGE PREFAB REF IN SCENE ############")
curDir = to_project_dir
for root, dirs, files in os.walk(curDir):
    for file in files:
        if file.endswith(".prefab.meta") and PREFIX in root:
            print(file)
            changePrefabRef(root, file)

print('')
print("############ 10.UPDATE gameState.ts ############")
curDir = to_project_dir
gameStateName = 'GameState' + TO_PROJECT_ID + '.ts'
for root, dirs, files in os.walk(curDir):
    for file in files:
        if gameStateName in file and PREFIX in root:
            print(file)
            oldGameStateName = gameStateName.replace(TO_PROJECT_ID, FROM_PROJECT_ID)
            shutil.rmtree(os.path.join(root, oldGameStateName), ignore_errors=True)
            shutil.copy(os.path.join(root, gameStateName), os.path.join(root, oldGameStateName))
            replaceFileContent(os.path.join(root, oldGameStateName), TO_PROJECT_ID, FROM_PROJECT_ID)
            break

print('')
print("############ 11.CLEAN ############")
curDir = to_project_dir
for dir in os.listdir(curDir):
    full_dir = os.path.join(curDir, dir)
    if os.path.isdir(full_dir) and PREFIX in full_dir:
        old_dir = full_dir.replace(PREFIX, '')
        shutil.rmtree(old_dir, ignore_errors=True)
        os.rename(full_dir, old_dir)

backupFile = root_path + '/' + FROM_PROJECT
if os.path.isfile(backupFile + '.zip'):
    with ZipFile(backupFile + '.zip', 'r') as zipObj:
       zipObj.extractall(backupFile)

try:
    os.remove(backupFile + '.zip')
except OSError:
    pass

os.popen('open -a CocosCreator')
